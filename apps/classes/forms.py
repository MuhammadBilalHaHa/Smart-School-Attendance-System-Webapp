from django import forms
from .models import Class


class ClassForm(forms.ModelForm):
    class Meta:
        model = Class
        fields = ['grade', 'section', 'class_teacher', 'attendance_mode', 'status']
        widgets = {
            'grade': forms.Select(attrs={'class': 'form-select'}),
            'section': forms.Select(attrs={'class': 'form-select'}),
            'class_teacher': forms.Select(attrs={'class': 'form-select'}),
            'attendance_mode': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }