from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Class, Grade, Section
from .forms import ClassForm


@method_decorator(login_required, name='dispatch')
class ClassListView(ListView):
    model = Class
    template_name = 'classes/class_list.html'
    context_object_name = 'classes'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_principal:
            messages.error(request, 'Access denied.')
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)


@method_decorator(login_required, name='dispatch')
class ClassCreateView(SuccessMessageMixin, CreateView):
    model = Class
    form_class = ClassForm
    template_name = 'classes/class_form.html'
    success_url = reverse_lazy('class_list')
    success_message = 'Class created successfully!'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_principal:
            messages.error(request, 'Access denied.')
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)


@method_decorator(login_required, name='dispatch')
class ClassUpdateView(SuccessMessageMixin, UpdateView):
    model = Class
    form_class = ClassForm
    template_name = 'classes/class_form.html'
    success_url = reverse_lazy('class_list')
    success_message = 'Class updated successfully!'


@method_decorator(login_required, name='dispatch')
class ClassDeleteView(DeleteView):
    model = Class
    template_name = 'classes/class_confirm_delete.html'
    success_url = reverse_lazy('class_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Class deleted successfully!')
        return super().delete(request, *args, **kwargs)


# ==================== AJAX VIEWS ====================

@csrf_exempt
def add_grade_ajax(request):
    """Add grade via AJAX from class form"""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if name:
            grade, created = Grade.objects.get_or_create(grade_name=name)
            return JsonResponse({'success': True, 'id': grade.pk, 'name': grade.grade_name})
    return JsonResponse({'success': False})


@csrf_exempt
def add_section_ajax(request):
    """Add section via AJAX from class form"""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip().upper()
        if name:
            section, created = Section.objects.get_or_create(section_name=name)
            return JsonResponse({'success': True, 'id': section.pk, 'name': section.section_name})
    return JsonResponse({'success': False})