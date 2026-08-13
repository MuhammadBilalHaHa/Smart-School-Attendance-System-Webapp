# 🏫 Smart School Attendance System

**AI-Based Face Recognition Attendance Management System**

---

## 📌 Project Overview

The Smart School Attendance System is an AI-powered automated attendance management solution designed for schools to replace traditional manual attendance methods. The system uses face recognition technology to automatically identify students and mark their attendance in real-time, reducing human error, saving time, and improving accuracy.

This system is developed as a role-based application where only two types of users exist: **Principal** and **Teachers**. The Principal acts as the system administrator with full control over users, classes, academic structure, and reports, while Teachers manage daily classroom attendance for their assigned classes.

, this system demonstrates the integration of Computer Vision (Face Recognition), Web Development (Django), Database Management, Email Automation, and Role-Based Access Control in a single production-ready application.

---

## 🎯 Project Objective

The main objective of this project is to develop an intelligent and automated attendance system that:

- Eliminates manual attendance marking errors
- Uses facial recognition for student identification
- Provides real-time attendance tracking
- Sends automated notifications to parents
- Maintains complete audit logs for transparency
- Ensures secure role-based access control
- Reduces teacher workload significantly
- Improves overall attendance accuracy

---

## ✨ Features

### 🔐 Authentication & User Management

- **Role-Based Access**: Principal (Admin) and Teacher roles
- **Secure Login**: Username lowercase validation, password hashing
- **Profile Management**: Change username, email, and password
- **Session Management**: Auto logout, session expiry

---

### 👨‍🏫 Teacher Module

**Attendance Operations:**
- **Camera Attendance**: Real-time face recognition using OpenCV
- **Manual Attendance**: Dropdown marking (Present/Absent/Late/Leave)
- **Draft System**: Save as draft, review, edit before finalizing
- **Finalize Attendance**: Password-protected locking system

**Class Management:**
- View assigned class only
- My Students list with details
- Individual student profiles
- Class attendance summary

**Reports:**
- Daily attendance report (own class)
- Attendance history with filters
- Individual student attendance view

---

### 👨‍💼 Principal Module (Admin)

**Student Management:**
- Add, edit, delete students
- Student photo upload with drag & drop
- Face encoding generation for recognition
- Guardian/Parent information management
- Student search and filtering

**Teacher Management:**
- Create teacher accounts with auto-credentials
- Assign teachers to classes
- Manage teacher profiles
- Activate/Deactivate accounts

**Class Management:**
- Grade management (1-10)
- Section management (A, B, C)
- Class mapping (Grade + Section)
- Class teacher assignment

**Attendance Analytics:**
- School-wide attendance overview
- Class-wise attendance summary
- Daily/Weekly/Monthly reports
- Top absent students tracking
- Top late students tracking

**Student Promotion:**
- Bulk promote students to next grade
- Mark students for repeat grade
- Promotion history tracking
- Automatic roll number reassignment

---

### 📷 Face Recognition System

**Student Registration:**
- Photo upload with drag & drop interface
- Automatic face encoding generation (128-dimensional vector)
- Photos organized by registration number in folders
- Multiple photo support

**Real-Time Recognition:**
- OpenCV camera integration
- Live face detection with green/red boxes
- Green box = Recognized student (name displayed)
- Red box = Unknown face
- Auto attendance marking
- Press 'Q' to stop and save

**Technical Details:**
- Uses face_recognition library (dlib-based)
- Tolerance threshold: 0.5
- Encodings stored as JSON in database
- Fast matching with numpy arrays

---

### 📧 Parent Notification System

Email Workflow:
1. Attendance Recorded (Camera or Manual)
2. Draft Created
3. Teacher Reviews Attendance
4. Teacher Makes Corrections (If Needed)
5. Teacher Clicks Finalize (Password Protected)
6. Session Gets Locked
7. Emails Sent to All Guardians
8. Email Logs Stored in Database
9. Audit Trail Created for Accountability

**Email Types:**
- ✅ Present Confirmation Email
- ⚠️ Absence Alert Email
- ⏰ Late Arrival Notice Email
- 📋 Leave Notification Email

**Guardian Support:**
- One primary guardian (required)
- Multiple additional guardians (optional)
- All guardians receive notifications

**Duplicate Prevention:**
- Unique constraint per student/session/email-type
- No duplicate emails sent

**Error Handling:**
- Failed emails logged with error message
- Retry mechanism (up to 3 times)
- Delivery status tracking (Sent/Failed/Pending)

---

### 📊 Attendance Analytics

**School-Level Reports:**
- Overall attendance percentage
- Total present/absent/late/leave counts
- Daily attendance summary
- Attendance trends

**Class-Level Reports:**
- Class attendance percentage
- Student count per class
- Most absent students
- Most late students
- Class comparison

**Student-Level Reports:**
- Individual attendance percentage
- Present/Absent/Late/Leave breakdown
- Attendance history by date
- Filter by week/month/year

---

### 🔐 Security Features

- **Password-Protected Actions**: Finalize, Reset, Promotion
- **Role-Based Permissions**: Teacher vs Principal access control
- **Audit Logging**: All critical actions tracked
- **Session Security**: Auto logout on browser close
- **Username Validation**: Lowercase only enforcement
- **CSRF Protection**: All forms protected

---

### 🎓 Student Promotion System

- Select grade to promote
- Bulk select/deselect students
- Promote to next grade (auto roll number)
- Mark for repeat grade
- Complete promotion history
- Audit trail for accountability

---

### 📧 Email Logs

- View all sent emails per session
- Delivery status tracking
- Error message display
- Retry failed emails
- Filter by email type

---

## 🎨 User Interface

**Color Theme:**
- Deep Navy (#0A1628) - Professional background
- Gold (#C9A84C) - Premium accent color
- Teal Green (#198754) - Present status
- Red (#DC3545) - Absent status
- Amber (#FFC107) - Late status

**UI Features:**
- Responsive Bootstrap 5 design
- Role-based sidebar navigation
- Drag & drop photo upload
- Modal-based confirmations
- Progress bars for attendance rate
- Badge-based status indicators
- Clean table layouts
- Mobile-friendly interface

---

## 🏁 Conclusion

The Smart School Attendance System successfully replaces traditional paper-based attendance with a modern, AI-powered solution. By integrating face recognition technology with a robust web application, the system provides:

- **Accuracy**: Eliminates human error in attendance marking
- **Efficiency**: Reduces attendance time from minutes to seconds
- **Transparency**: Parents notified instantly via email
- **Accountability**: Complete audit trail of all actions
- **Scalability**: Can handle multiple grades and sections
- **Security**: Role-based access with password protection

This project demonstrates practical application of AI, computer vision, and web development in solving a real-world educational problem.

---

**© 2026 Smart School Attendance System | Muhammad Bilal**
