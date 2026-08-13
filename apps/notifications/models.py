from django.db import models
from apps.attendance.models import AttendanceSession
from apps.students.models import Student


class EmailLog(models.Model):
    """Store all email notifications sent"""
    
    EMAIL_TYPES = [
        ('Present', 'Present Notification'),
        ('Absent', 'Absent Alert'),
        ('Late', 'Late Alert'),
        ('Leave', 'Leave Notification'),
    ]
    
    STATUS_CHOICES = [
        ('Sent', 'Sent'),
        ('Failed', 'Failed'),
        ('Pending', 'Pending'),
    ]
    
    session = models.ForeignKey(AttendanceSession, on_delete=models.CASCADE, related_name='email_logs')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='email_logs')
    recipient_email = models.EmailField()
    guardian_name = models.CharField(max_length=100, blank=True, null=True)
    email_type = models.CharField(max_length=20, choices=EMAIL_TYPES)
    attendance_status = models.CharField(max_length=20)
    sent_at = models.DateTimeField(auto_now_add=True)
    delivery_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    error_message = models.TextField(blank=True, null=True)
    retry_count = models.IntegerField(default=0)

    class Meta:
        db_table = 'email_logs'
        verbose_name = 'Email Log'
        verbose_name_plural = 'Email Logs'
        ordering = ['-sent_at']
        unique_together = ['session', 'student', 'email_type']

    def __str__(self):
        return f"{self.student.full_name} - {self.email_type} - {self.delivery_status}"