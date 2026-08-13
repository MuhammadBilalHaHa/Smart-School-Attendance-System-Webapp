from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import date

@login_required
def dashboard(request):
    """
    Main dashboard - redirects based on role
    """
    if request.user.is_principal:
        return redirect('principal_dashboard')
    elif request.user.is_teacher:
        return redirect('teacher_dashboard')
    else:
        messages.error(request, 'Invalid user role.')
        return redirect('login')


@login_required
def principal_dashboard(request):
    if not request.user.is_principal:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    from apps.students.models import Student
    from apps.teachers.models import Teacher
    from apps.classes.models import Class
    
    context = {
        'page_title': 'Principal Dashboard',
        'today': date.today(),
        'total_students': Student.objects.filter(status='Active').count(),
        'total_teachers': Teacher.objects.filter(status='Active').count(),
        'total_classes': Class.objects.filter(status='Active').count(),
        'today_attendance': 0,  # Will update when attendance module is built
        'recent_students': Student.objects.order_by('-created_at')[:5],
    }
    
    return render(request, 'dashboard/principal_dashboard.html', context)


@login_required
def teacher_dashboard(request):
    if not request.user.is_teacher:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    from apps.students.models import Student
    from apps.classes.models import Class
    
    # Get teacher's assigned class
    assigned_class = None
    total_students = 0
    
    try:
        teacher_profile = request.user.teacher_profile
        assigned_class = Class.objects.filter(class_teacher=teacher_profile, status='Active').first()
        if assigned_class:
            total_students = Student.objects.filter(student_class=assigned_class, status='Active').count()
    except:
        pass
    
    context = {
        'page_title': 'Teacher Dashboard',
        'today': date.today(),
        'assigned_class': assigned_class,
        'total_students': total_students,
        'today_attendance': 0,
    }
    
    return render(request, 'dashboard/teacher_dashboard.html', context)