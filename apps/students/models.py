import os
from django.db import models
from django.conf import settings
from apps.classes.models import Class


def student_photo_path(instance, filename):
    """Upload to media/studentsImages/REG_NO/filename"""
    ext = filename.split('.')[-1]
    if instance.registration_no:
        new_filename = f"{instance.registration_no}.{ext}"
        return f"studentsImages/{instance.registration_no}/{new_filename}"
    return f"studentsImages/temp/{filename}"


class Student(models.Model):
    """Student registration and management"""
    
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
    ]
    
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        ('Transferred', 'Transferred'),
        ('Left', 'Left'),
    ]

    registration_no = models.CharField(max_length=50, unique=True)
    roll_no = models.CharField(max_length=20, blank=True, null=True)
    full_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    date_of_birth = models.DateField(null=True, blank=True)
    student_class = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='students')
    photo = models.ImageField(upload_to=student_photo_path, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'students'
        verbose_name = 'Student'
        verbose_name_plural = 'Students'
        ordering = ['registration_no']

    def __str__(self):
        return f"{self.full_name} ({self.registration_no})"

    def save(self, *args, **kwargs):
        # Generate registration number if not set
        if not self.registration_no:
            last_student = Student.objects.order_by('-id').first()
            if last_student and last_student.registration_no.startswith('STU'):
                try:
                    last_id = int(last_student.registration_no[3:])
                except:
                    last_id = 0
            else:
                last_id = 0
            self.registration_no = f"STU{str(last_id + 1).zfill(5)}"
        super().save(*args, **kwargs)
    
    def get_photo_dir(self):
        """Get the directory path for this student's photos"""
        return os.path.join(settings.MEDIA_ROOT, 'studentsImages', self.registration_no)
    
    def get_photo_count(self):
        """Count photos for this student"""
        photo_dir = self.get_photo_dir()
        if os.path.exists(photo_dir):
            return len([f for f in os.listdir(photo_dir) if f.endswith(('.jpg', '.jpeg', '.png'))])
        return 0
    
    def get_all_photos(self):
        """Get list of all photo paths for this student"""
        photo_dir = self.get_photo_dir()
        photos = []
        if os.path.exists(photo_dir):
            for f in sorted(os.listdir(photo_dir)):
                if f.endswith(('.jpg', '.jpeg', '.png')):
                    photos.append(os.path.join('studentsImages', self.registration_no, f))
        return photos


class Guardian(models.Model):
    """Student guardian/parent information"""
    
    RELATIONSHIP_CHOICES = [
        ('Father', 'Father'),
        ('Mother', 'Mother'),
        ('Guardian', 'Guardian'),
        ('Other', 'Other'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='guardians')
    guardian_name = models.CharField(max_length=100)
    relationship = models.CharField(max_length=20, choices=RELATIONSHIP_CHOICES)
    email = models.EmailField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    is_primary = models.BooleanField(default=False)

    class Meta:
        db_table = 'guardians'
        verbose_name = 'Guardian'
        verbose_name_plural = 'Guardians'

    def __str__(self):
        return f"{self.guardian_name} - {self.student.full_name}"
    
    def save(self, *args, **kwargs):
        if self.is_primary:
            Guardian.objects.filter(student=self.student, is_primary=True).update(is_primary=False)
        super().save(*args, **kwargs)


class StudentFaceEncoding(models.Model):
    """Store face encodings for students"""
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='face_encoding')
    encoding_data = models.TextField()  # JSON string of face encoding array
    photo_path = models.CharField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'student_face_encodings'
        verbose_name = 'Student Face Encoding'
        verbose_name_plural = 'Student Face Encodings'

    def __str__(self):
        return f"Face Encoding - {self.student.full_name}"
    
    def get_encoding_array(self):
        """Convert JSON string back to numpy array"""
        import json
        import numpy as np
        return np.array(json.loads(self.encoding_data))