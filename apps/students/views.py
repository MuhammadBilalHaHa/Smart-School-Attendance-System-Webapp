import os
import json
import face_recognition
import numpy as np
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from .models import Student, Guardian, StudentFaceEncoding
from .forms import StudentForm, GuardianForm


@method_decorator(login_required, name='dispatch')
class StudentListView(ListView):
    model = Student
    template_name = 'students/student_list.html'
    context_object_name = 'students'

    def get_queryset(self):
        queryset = Student.objects.all()
        
        if self.request.user.is_teacher:
            try:
                teacher_profile = self.request.user.teacher_profile
                from apps.classes.models import Class
                assigned_class = Class.objects.filter(class_teacher=teacher_profile, status='Active').first()
                if assigned_class:
                    queryset = queryset.filter(student_class=assigned_class)
                else:
                    queryset = Student.objects.none()
            except:
                queryset = Student.objects.none()
        
        class_id = self.request.GET.get('class')
        if class_id and self.request.user.is_principal:
            queryset = queryset.filter(student_class_id=class_id)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from apps.classes.models import Class
        context['classes'] = Class.objects.filter(status='Active')
        return context


@method_decorator(login_required, name='dispatch')
class StudentDetailView(DetailView):
    model = Student
    template_name = 'students/student_detail.html'
    context_object_name = 'student'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['guardians'] = Guardian.objects.filter(student=self.object)
        context['has_face_encoding'] = hasattr(self.object, 'face_encoding')
        context['photo_count'] = self.object.get_photo_count()
        return context


@method_decorator(login_required, name='dispatch')
class StudentCreateView(SuccessMessageMixin, CreateView):
    model = Student
    form_class = StudentForm
    template_name = 'students/student_form.html'
    success_url = reverse_lazy('student_list')
    success_message = 'Student registered successfully!'

    def form_valid(self, form):
        student_class = form.cleaned_data['student_class']
        last_roll = Student.objects.filter(student_class=student_class).count()
        form.instance.roll_no = str(last_roll + 1)
        
        response = super().form_valid(form)
        
        # Generate face encoding if photo uploaded
        if form.cleaned_data.get('photo'):
            success = self.generate_face_encoding(self.object)
            if success:
                messages.success(self.request, '✅ Face encoding generated! Student can be recognized by camera.')
            else:
                messages.warning(self.request, '⚠️ No face detected. Upload a clearer front-facing photo.')
        
        return response

    def generate_face_encoding(self, student):
        """Generate and store face encoding from student photo"""
        try:
            if not student.photo:
                return False
                
            image_path = student.photo.path
            image = face_recognition.load_image_file(image_path)
            encodings = face_recognition.face_encodings(image)
            
            if encodings:
                encoding_list = encodings[0].tolist()
                encoding_json = json.dumps(encoding_list)
                
                StudentFaceEncoding.objects.update_or_create(
                    student=student,
                    defaults={
                        'encoding_data': encoding_json,
                        'photo_path': student.photo.name,
                    }
                )
                return True
            return False
        except Exception as e:
            messages.error(self.request, f'Error: {str(e)}')
            return False


@method_decorator(login_required, name='dispatch')
class StudentUpdateView(SuccessMessageMixin, UpdateView):
    model = Student
    form_class = StudentForm
    template_name = 'students/student_form.html'
    success_url = reverse_lazy('student_list')
    success_message = 'Student updated!'

    def form_valid(self, form):
        response = super().form_valid(form)
        
        if form.cleaned_data.get('photo'):
            success = StudentCreateView.generate_face_encoding(self, self.object)
            if success:
                messages.success(self.request, '✅ Face encoding updated!')
            else:
                messages.warning(self.request, '⚠️ No face detected in new photo.')
        
        return response


@method_decorator(login_required, name='dispatch')
class StudentDeleteView(DeleteView):
    model = Student
    template_name = 'students/student_confirm_delete.html'
    success_url = reverse_lazy('student_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Student deleted successfully!')
        return super().delete(request, *args, **kwargs)


# ==================== GUARDIAN VIEWS ====================

@login_required
def add_guardian(request, student_id):
    student = get_object_or_404(Student, pk=student_id)
    
    if request.method == 'POST':
        form = GuardianForm(request.POST)
        if form.is_valid():
            guardian = form.save(commit=False)
            guardian.student = student
            guardian.save()
            messages.success(request, 'Guardian added!')
            return redirect('student_detail', pk=student.pk)
    else:
        form = GuardianForm()
    
    return render(request, 'students/guardian_form.html', {
        'form': form,
        'student': student,
    })


@login_required
def edit_guardian(request, guardian_id):
    guardian = get_object_or_404(Guardian, pk=guardian_id)
    
    if request.method == 'POST':
        form = GuardianForm(request.POST, instance=guardian)
        if form.is_valid():
            form.save()
            messages.success(request, 'Guardian updated!')
            return redirect('student_detail', pk=guardian.student.pk)
    else:
        form = GuardianForm(instance=guardian)
    
    return render(request, 'students/guardian_form.html', {
        'form': form,
        'student': guardian.student,
        'guardian': guardian,
    })


@login_required
def delete_guardian(request, guardian_id):
    guardian = get_object_or_404(Guardian, pk=guardian_id)
    student_id = guardian.student.pk
    
    if request.method == 'POST':
        guardian.delete()
        messages.success(request, 'Guardian deleted!')
    
    return redirect('student_detail', pk=student_id)