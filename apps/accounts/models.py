from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Custom User Model for Smart School Attendance System
    Two roles: Principal (Admin) and Teacher
    """
    
    ROLE_CHOICES = [
        ('Principal', 'Principal'),
        ('Teacher', 'Teacher'),
    ]
    
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='Teacher'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Active'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.username} - {self.role}"

    @property
    def is_principal(self):
        return self.role == 'Principal'

    @property
    def is_teacher(self):
        return self.role == 'Teacher'

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username