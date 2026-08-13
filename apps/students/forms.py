from django import forms
from .models import Student, Guardian


class StudentForm(forms.ModelForm):
    photo = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*',
        })
    )
    
    class Meta:
        model = Student
        fields = ['full_name', 'gender', 'date_of_birth', 'student_class', 'photo', 'status']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter full name'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'student_class': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


class GuardianForm(forms.ModelForm):
    class Meta:
        model = Guardian
        fields = ['guardian_name', 'relationship', 'email', 'phone', 'is_primary']
        widgets = {
            'guardian_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Guardian name'}),
            'relationship': forms.Select(attrs={'class': 'form-select'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email address'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone number'}),
            'is_primary': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }