from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from .models import Teacher
from .forms import TeacherForm
from apps.accounts.models import User
import random
import string


@method_decorator(login_required, name='dispatch')
class TeacherListView(ListView):
    model = Teacher
    template_name = 'teachers/teacher_list.html'
    context_object_name = 'teachers'

    def get(self, request, *args, **kwargs):
        # Clear session if ?clear=1
        if request.GET.get('clear') == '1':
            request.session.pop('new_teacher_credentials', None)
            request.session.pop('show_credentials_modal', None)
            request.session.modified = True
        
        # Set modal flag if credentials exist
        if request.session.get('new_teacher_credentials'):
            request.session['show_credentials_modal'] = True
        
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['show_modal'] = self.request.session.get('show_credentials_modal', False)
        context['credentials'] = self.request.session.get('new_teacher_credentials', None)
        return context

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_principal:
            messages.error(request, 'Access denied.')
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)


@method_decorator(login_required, name='dispatch')
class TeacherCreateView(SuccessMessageMixin, CreateView):
    model = Teacher
    form_class = TeacherForm
    template_name = 'teachers/teacher_form.html'
    success_url = reverse_lazy('teacher_list')
    success_message = 'Teacher added successfully!'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_principal:
            messages.error(request, 'Access denied.')
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        full_name = form.cleaned_data.get('full_name')
        email = form.cleaned_data.get('email', '')
        
        # Generate username and password
        first_name_part = full_name.split()[0].lower()
        username = f"{first_name_part}{random.randint(100,999)}"
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        
        # Create User account
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role='Teacher',
            first_name=full_name.split()[0] if ' ' in full_name else full_name,
            last_name=' '.join(full_name.split()[1:]) if ' ' in full_name else '',
            is_active=True,
            status='Active'
        )
        
        # Set user BEFORE saving
        form.instance.user = user
        response = super().form_valid(form)
        
        # Store credentials in session for modal
        self.request.session['new_teacher_credentials'] = {
            'name': full_name,
            'username': username,
            'password': password,
        }
        self.request.session['show_credentials_modal'] = True
        
        return response


@method_decorator(login_required, name='dispatch')
class TeacherUpdateView(SuccessMessageMixin, UpdateView):
    model = Teacher
    form_class = TeacherForm
    template_name = 'teachers/teacher_form.html'
    success_url = reverse_lazy('teacher_list')
    success_message = 'Teacher updated successfully!'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_principal:
            messages.error(request, 'Access denied.')
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)


@method_decorator(login_required, name='dispatch')
class TeacherDeleteView(DeleteView):
    model = Teacher
    template_name = 'teachers/teacher_confirm_delete.html'
    success_url = reverse_lazy('teacher_list')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_principal:
            messages.error(request, 'Access denied.')
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        teacher = self.get_object()
        if teacher.user:
            teacher.user.delete()
        messages.success(request, 'Teacher deleted successfully!')
        return super().delete(request, *args, **kwargs)