from django.db import models
from apps.classes.models import Class
from apps.teachers.models import Teacher
from apps.students.models import Student


class AttendanceSession(models.Model):
    """One attendance session per class per day"""
    
    MODE_CHOICES = [
        ('Manual', 'Manual'),
        ('Automatic', 'Automatic'),
    ]
    
    class_info = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='attendance_sessions')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='attendance_sessions')
    attendance_date = models.DateField()
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    mode = models.CharField(max_length=20, choices=MODE_CHOICES, default='Manual')
    is_completed = models.BooleanField(default=False)
    is_finalized = models.BooleanField(default=False, help_text="Locked after teacher finalizes")
    finalized_at = models.DateTimeField(null=True, blank=True)
    notifications_sent = models.BooleanField(default=False)

    class Meta:
        db_table = 'attendance_sessions'
        verbose_name = 'Attendance Session'
        verbose_name_plural = 'Attendance Sessions'
        unique_together = ['class_info', 'attendance_date']
        ordering = ['-attendance_date', '-started_at']

    def __str__(self):
        return f"{self.class_info} - {self.attendance_date}"


class AttendanceRecord(models.Model):
    """Individual student attendance record"""
    
    STATUS_CHOICES = [
        ('Present', 'Present'),
        ('Absent', 'Absent'),
        ('Late', 'Late'),
        ('Leave', 'Leave'),
    ]
    
    session = models.ForeignKey(AttendanceSession, on_delete=models.CASCADE, related_name='records')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_records')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Present')
    marked_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'attendance_records'
        verbose_name = 'Attendance Record'
        verbose_name_plural = 'Attendance Records'
        unique_together = ['session', 'student']
        ordering = ['student__roll_no']

    def __str__(self):
        return f"{self.student.full_name} - {self.status}"