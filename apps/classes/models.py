from django.db import models
from apps.teachers.models import Teacher


class Grade(models.Model):
    grade_name = models.CharField(max_length=20, unique=True)

    class Meta:
        db_table = 'grades'
        verbose_name = 'Grade'
        verbose_name_plural = 'Grades'
        ordering = ['id']

    def __str__(self):
        return f"Grade {self.grade_name}"


class Section(models.Model):
    section_name = models.CharField(max_length=10, unique=True)

    class Meta:
        db_table = 'sections'
        verbose_name = 'Section'
        verbose_name_plural = 'Sections'
        ordering = ['section_name']

    def __str__(self):
        return f"Section {self.section_name}"


class Class(models.Model):
    MODE_CHOICES = [
        ('Manual', 'Manual'),
        ('Automatic', 'Automatic'),
    ]
    
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]

    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name='classes')
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='classes')
    class_teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_class')
    attendance_mode = models.CharField(max_length=20, choices=MODE_CHOICES, default='Manual')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'classes'
        verbose_name = 'Class'
        verbose_name_plural = 'Classes'
        unique_together = ['grade', 'section']
        ordering = ['grade__id', 'section__section_name']

    def __str__(self):
        return f"Grade {self.grade.grade_name} - Section {self.section.section_name}"

    @property
    def class_name(self):
        return f"{self.grade.grade_name}-{self.section.section_name}"