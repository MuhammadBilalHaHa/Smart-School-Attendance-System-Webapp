import face_recognition
import cv2
import numpy as np
import json
from django.conf import settings
from apps.students.models import Student, StudentFaceEncoding


class FaceRecognitionEngine:
    """Face detection and recognition engine"""
    
    def __init__(self):
        self.known_encodings = []
        self.known_student_ids = []
        self.known_student_names = []
        self.tolerance = 0.5  # Lower = stricter matching
    
    def load_known_faces(self, class_id=None):
        """Load face encodings from database"""
        students = Student.objects.filter(status='Active')
        if class_id:
            students = students.filter(student_class_id=class_id)
        
        self.known_encodings = []
        self.known_student_ids = []
        self.known_student_names = []
        
        for student in students:
            try:
                if hasattr(student, 'face_encoding') and student.face_encoding:
                    # Load encoding from database
                    encoding_array = json.loads(student.face_encoding.encoding_data)
                    self.known_encodings.append(np.array(encoding_array))
                    self.known_student_ids.append(student.pk)
                    self.known_student_names.append(student.full_name)
            except Exception as e:
                print(f"Error loading encoding for {student.full_name}: {e}")
        
        print(f"Loaded {len(self.known_encodings)} face encodings")
        return len(self.known_encodings)
    
    def recognize_face(self, face_image):
        """Recognize faces in an image frame"""
        try:
            # Convert BGR to RGB
            rgb_image = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)
            
            # Detect faces in frame
            face_locations = face_recognition.face_locations(rgb_image)
            face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
            
            results = []
            
            for face_encoding, face_location in zip(face_encodings, face_locations):
                # COMPARE live encoding with all stored encodings
                matches = face_recognition.compare_faces(
                    self.known_encodings,      # Stored encodings from DB
                    face_encoding,             # Live encoding from camera
                    tolerance=self.tolerance
                )
                
                name = "Unknown"
                student_id = None
                
                if True in matches:
                    # Find the best match
                    face_distances = face_recognition.face_distance(
                        self.known_encodings, 
                        face_encoding
                    )
                    best_match_index = np.argmin(face_distances)
                    
                    if matches[best_match_index]:
                        student_id = self.known_student_ids[best_match_index]
                        name = self.known_student_names[best_match_index]
                
                results.append({
                    'student_id': student_id,
                    'name': name,
                    'matched': student_id is not None,
                    'location': face_location,
                })
            
            return results, face_locations
            
        except Exception as e:
            print(f"Recognition error: {e}")
            return [], []
    
    def capture_and_recognize(self, class_id=None):
        """Open camera, capture, recognize faces, mark attendance"""
        self.load_known_faces(class_id)
        
        if len(self.known_encodings) == 0:
            print("⚠️ No face encodings found! Register student photos first.")
            return []
        
        print(f"📷 Opening camera... {len(self.known_encodings)} students loaded")
        print("Press 'Q' to stop and save attendance")
        
        cap = cv2.VideoCapture(0)
        recognized_students = set()
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Make a copy for display
            display_frame = frame.copy()
            
            # Recognize faces in current frame
            results, face_locations = self.recognize_face(frame)
            
            # Draw rectangles and names
            for result, (top, right, bottom, left) in zip(results, face_locations):
                if result['matched']:
                    # Green box for recognized
                    color = (0, 255, 0)
                    recognized_students.add(result['student_id'])
                else:
                    # Red box for unknown
                    color = (0, 0, 255)
                
                # Draw rectangle
                cv2.rectangle(display_frame, (left, top), (right, bottom), color, 2)
                
                # Draw name label
                label = result['name'] if result['matched'] else "Unknown"
                cv2.rectangle(display_frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
                cv2.putText(display_frame, label, (left + 6, bottom - 6),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            
            # Show count
            cv2.putText(display_frame, f"Recognized: {len(recognized_students)}", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (201, 168, 76), 2)
            
            cv2.imshow('Smart School Attendance - Press Q to Stop', display_frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        
        print(f"✅ Attendance complete! {len(recognized_students)} students recognized.")
        return list(recognized_students)