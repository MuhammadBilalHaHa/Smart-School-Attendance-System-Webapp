from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import date, datetime, timedelta
from django.http import JsonResponse
from django.contrib.auth import authenticate
from django.db.models import Count, Q
from .models import AttendanceSession, AttendanceRecord
from apps.classes.models import Class
from apps.students.models import Student
from apps.teachers.models import Teacher
from .face_recognition import FaceRecognitionEngine
from apps.notifications.email_service import NotificationService
from apps.notifications.models import EmailLog
from apps.audit.services import AuditService


# ==================== DASHBOARD ====================

@login_required
def attendance_dashboard(request):
    """Attendance home - redirect based on role"""
    if request.user.is_teacher:
        return redirect('start_attendance')
    elif request.user.is_principal:
        return redirect('attendance_report')
    return redirect('dashboard')


# ==================== TAKE ATTENDANCE ====================

@login_required
def start_attendance(request):
    """Teacher: Choose attendance mode"""
    if not request.user.is_teacher:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    try:
        teacher_profile = request.user.teacher_profile
        assigned_class = Class.objects.filter(class_teacher=teacher_profile, status='Active').first()
    except:
        messages.error(request, 'You are not assigned to any class.')
        return redirect('teacher_dashboard')

    if not assigned_class:
        messages.error(request, 'You are not assigned to any class.')
        return redirect('teacher_dashboard')

    today = date.today()

    existing_session = AttendanceSession.objects.filter(
        class_info=assigned_class,
        attendance_date=today,
        is_completed=True
    ).first()

    if existing_session:
        messages.info(request, 'Attendance already completed for today.')
        return redirect('attendance_summary', session_id=existing_session.pk)

    mode = request.GET.get('mode', 'manual')
    students = Student.objects.filter(student_class=assigned_class, status='Active').order_by('roll_no')

    context = {
        'assigned_class': assigned_class,
        'students': students,
        'today': today,
        'mode': mode,
    }

    return render(request, 'attendance/start_attendance.html', context)


@login_required
def create_session(request):
    """Create new attendance session with mode"""
    if request.method == 'POST':
        class_id = request.POST.get('class_id')
        mode = request.POST.get('mode', 'Manual')

        try:
            class_info = Class.objects.get(pk=class_id)
            teacher_profile = request.user.teacher_profile
            today = date.today()

            session, created = AttendanceSession.objects.get_or_create(
                class_info=class_info,
                attendance_date=today,
                defaults={
                    'teacher': teacher_profile,
                    'mode': mode,
                }
            )

            if mode == 'Manual':
                return redirect('take_attendance', session_id=session.pk)
            else:
                return redirect('camera_attendance', session_id=session.pk)

        except Exception as e:
            messages.error(request, f'Error: {str(e)}')

    return redirect('start_attendance')


@login_required
def take_attendance(request, session_id):
    """Manual attendance marking - saves as DRAFT"""
    session = get_object_or_404(AttendanceSession, pk=session_id)

    if session.is_finalized:
        messages.error(request, 'Attendance is finalized. Cannot edit.')
        return redirect('attendance_summary', session_id=session.pk)

    if request.user.is_teacher:
        try:
            teacher_profile = request.user.teacher_profile
            if session.class_info.class_teacher != teacher_profile:
                messages.error(request, 'Access denied.')
                return redirect('dashboard')
        except:
            messages.error(request, 'Access denied.')
            return redirect('dashboard')

    students = Student.objects.filter(
        student_class=session.class_info,
        status='Active'
    ).order_by('roll_no')

    existing_records = AttendanceRecord.objects.filter(session=session)
    records_dict = {r.student_id: r.status for r in existing_records}

    if request.method == 'POST':
        for student in students:
            status = request.POST.get(f'status_{student.pk}')
            if status:
                AttendanceRecord.objects.update_or_create(
                    session=session,
                    student=student,
                    defaults={'status': status}
                )

        session.is_completed = True
        session.ended_at = timezone.now()
        session.save()

        messages.success(request, '✅ Draft attendance saved! Review and Finalize to send emails.')
        return redirect('attendance_summary', session_id=session.pk)

    context = {
        'session': session,
        'students': students,
        'records_dict': records_dict,
        'status_choices': AttendanceRecord.STATUS_CHOICES,
    }

    return render(request, 'attendance/take_attendance.html', context)


@login_required
def camera_attendance(request, session_id):
    """Camera-based attendance page"""
    session = get_object_or_404(AttendanceSession, pk=session_id)

    if session.is_finalized:
        messages.error(request, 'Attendance is finalized. Cannot edit.')
        return redirect('attendance_summary', session_id=session.pk)

    if request.user.is_teacher:
        try:
            teacher_profile = request.user.teacher_profile
            if session.class_info.class_teacher != teacher_profile:
                messages.error(request, 'Access denied.')
                return redirect('dashboard')
        except:
            messages.error(request, 'Access denied.')
            return redirect('dashboard')

    context = {
        'session': session,
        'assigned_class': session.class_info,
    }

    return render(request, 'attendance/camera_attendance.html', context)


@login_required
def process_camera_attendance(request, session_id):
    """Process attendance from camera feed - saves as DRAFT"""
    if request.method == 'POST':
        session = get_object_or_404(AttendanceSession, pk=session_id)

        if session.is_finalized:
            messages.error(request, 'Attendance is finalized.')
            return redirect('attendance_summary', session_id=session.pk)

        try:
            engine = FaceRecognitionEngine()
            recognized_ids = engine.capture_and_recognize(session.class_info_id)

            students = Student.objects.filter(student_class=session.class_info, status='Active')

            for student in students:
                status = 'Present' if student.pk in recognized_ids else 'Absent'
                AttendanceRecord.objects.update_or_create(
                    session=session,
                    student=student,
                    defaults={'status': status}
                )

            session.is_completed = True
            session.ended_at = timezone.now()
            session.mode = 'Automatic'
            session.save()

            messages.success(request, f'✅ Draft saved! {len(recognized_ids)} recognized. Review and Finalize.')
            return redirect('attendance_summary', session_id=session.pk)

        except Exception as e:
            messages.error(request, f'Camera error: {str(e)}. Try manual mode.')
            return redirect('take_attendance', session_id=session.pk)

    return redirect('start_attendance')


# ==================== SUMMARY ====================

@login_required
def attendance_summary(request, session_id):
    """Show attendance summary"""
    session = get_object_or_404(AttendanceSession, pk=session_id)
    records = AttendanceRecord.objects.filter(session=session).select_related('student')

    total   = records.count()
    present = records.filter(status='Present').count()
    absent  = records.filter(status='Absent').count()
    late    = records.filter(status='Late').count()
    leave   = records.filter(status='Leave').count()

    context = {
        'session': session,
        'records': records,
        'total':   total,
        'present': present,
        'absent':  absent,
        'late':    late,
        'leave':   leave,
        'attendance_percentage': round((present / total * 100) if total > 0 else 0, 1),
    }

    return render(request, 'attendance/attendance_summary.html', context)


# ==================== FINALIZE & NOTIFICATIONS ====================

@login_required
def finalize_attendance(request, session_id):
    """Finalize attendance, lock it, and send notifications"""
    session = get_object_or_404(AttendanceSession, pk=session_id)

    if request.user.is_teacher:
        try:
            teacher_profile = request.user.teacher_profile
            if session.class_info.class_teacher != teacher_profile:
                messages.error(request, 'Access denied.')
                return redirect('dashboard')
        except:
            messages.error(request, 'Access denied.')
            return redirect('dashboard')

    if session.is_finalized:
        messages.info(request, 'Attendance already finalized.')
        return redirect('attendance_summary', session_id=session.pk)

    if request.method == 'POST':
        password = request.POST.get('password', '')
        user = authenticate(username=request.user.username, password=password)

        if user is not None:
            session.is_finalized = True
            session.finalized_at = timezone.now()
            session.is_completed = True
            session.save()

            sent, failed = NotificationService.send_attendance_notification(session)

            AuditService.log_action(
                user=request.user,
                action=f'Finalized attendance for {session.class_info.class_name}',
                entity_name='AttendanceSession',
                entity_id=session.pk,
                details=f'Emails sent: {sent}, Failed: {failed}',
                request=request,
            )

            if sent > 0:
                messages.success(request, f'✅ Finalized! {sent} email(s) sent to parents.')
            if failed > 0:
                messages.warning(request, f'⚠️ {failed} email(s) failed.')

            return redirect('attendance_summary', session_id=session.pk)
        else:
            messages.error(request, 'Incorrect password!')

    return redirect('attendance_summary', session_id=session.pk)


@login_required
def retry_emails(request, session_id):
    """Retry failed email notifications"""
    if request.method == 'POST':
        session = get_object_or_404(AttendanceSession, pk=session_id)

        failed_count = EmailLog.objects.filter(
            session=session,
            delivery_status='Failed'
        ).count()

        if failed_count == 0:
            messages.info(request, 'No failed emails to retry.')
        else:
            NotificationService.retry_failed_emails(session_id)

            still_failed = EmailLog.objects.filter(
                session=session,
                delivery_status='Failed'
            ).count()

            if still_failed == 0:
                messages.success(request, f'✅ All {failed_count} emails resent successfully!')
            else:
                messages.warning(request, f'⚠️ {still_failed} out of {failed_count} still failing.')

    return redirect('attendance_summary', session_id=session_id)


@login_required
def email_logs(request, session_id):
    """View email logs for a session"""
    session = get_object_or_404(AttendanceSession, pk=session_id)
    logs = EmailLog.objects.filter(session=session).select_related('student')

    context = {
        'session': session,
        'logs': logs,
    }

    return render(request, 'attendance/email_logs.html', context)


# ==================== RESET ====================

@login_required
def reset_attendance(request, session_id):
    """Reset attendance session - requires password confirmation"""
    session = get_object_or_404(AttendanceSession, pk=session_id)

    if session.is_finalized:
        messages.error(request, 'Cannot reset finalized attendance.')
        return redirect('attendance_summary', session_id=session.pk)

    if request.user.is_teacher:
        try:
            teacher_profile = request.user.teacher_profile
            if session.class_info.class_teacher != teacher_profile:
                messages.error(request, 'Access denied.')
                return redirect('dashboard')
        except:
            messages.error(request, 'Access denied.')
            return redirect('dashboard')

    if request.method == 'POST':
        password = request.POST.get('password', '')
        user = authenticate(username=request.user.username, password=password)

        if user is not None:
            AttendanceRecord.objects.filter(session=session).delete()
            session.is_completed = False
            session.ended_at = None
            session.save()
            messages.success(request, 'Attendance session reset successfully!')
            return redirect('take_attendance', session_id=session.pk)
        else:
            messages.error(request, 'Incorrect password! Reset failed.')
            return redirect('attendance_summary', session_id=session.pk)

    return redirect('attendance_summary', session_id=session.pk)


@login_required
def principal_reset_attendance(request, session_id):
    """Principal can reset any attendance with reason"""
    if not request.user.is_principal:
        messages.error(request, 'Access denied. Principal only.')
        return redirect('dashboard')

    session = get_object_or_404(AttendanceSession, pk=session_id)

    if request.method == 'POST':
        password = request.POST.get('password', '')
        reason   = request.POST.get('reason', '').strip()
        user = authenticate(username=request.user.username, password=password)

        if user is None:
            messages.error(request, 'Incorrect password!')
            return redirect('attendance_report')

        if not reason:
            messages.error(request, 'Please provide a reason for reset.')
            return redirect('attendance_report')

        AttendanceRecord.objects.filter(session=session).delete()

        session.is_completed       = False
        session.is_finalized       = False
        session.finalized_at       = None
        session.notifications_sent = False
        session.ended_at           = None
        session.save()

        EmailLog.objects.filter(session=session).delete()

        AuditService.log_action(
            user=request.user,
            action=f'Principal reset attendance for {session.class_info.class_name}',
            entity_name='AttendanceSession',
            entity_id=session.pk,
            details=f'Reason: {reason}',
            request=request,
        )

        messages.success(request, f'✅ Attendance reset for {session.class_info.class_name}. Reason: {reason}')

    return redirect('attendance_report')


# ==================== HISTORY ====================

@login_required
def attendance_history(request):
    """View attendance history - teacher sees own class, principal sees all"""

    sessions = AttendanceSession.objects.filter(
        is_completed=True
    ).annotate(
        count_present=Count('records', filter=Q(records__status='Present')),
        count_absent =Count('records', filter=Q(records__status='Absent')),
        count_late   =Count('records', filter=Q(records__status='Late')),
        count_total  =Count('records'),
    ).select_related(
        'class_info', 'teacher', 'class_info__grade', 'class_info__section'
    ).order_by('-attendance_date')

    if request.user.is_teacher:
        try:
            teacher_profile = request.user.teacher_profile
            assigned_class = Class.objects.filter(
                class_teacher=teacher_profile
            ).first()
            if assigned_class:
                sessions = sessions.filter(class_info=assigned_class)
            else:
                sessions = AttendanceSession.objects.none()
        except:
            sessions = AttendanceSession.objects.none()
            assigned_class = None

        students = Student.objects.filter(
            student_class=assigned_class,
            status='Active'
        ).order_by('roll_no') if assigned_class else Student.objects.none()

        selected_class  = ''
        selected_period = 'all'

    elif request.user.is_principal:
        selected_period = request.GET.get('period', 'all')
        selected_class  = request.GET.get('class', '')
        today = date.today()

        if selected_class:
            sessions = sessions.filter(class_info_id=selected_class)

        if selected_period == 'day':
            sessions = sessions.filter(attendance_date=today)
        elif selected_period == 'week':
            sessions = sessions.filter(
                attendance_date__gte=today - timedelta(days=today.weekday())
            )
        elif selected_period == 'month':
            sessions = sessions.filter(
                attendance_date__year=today.year,
                attendance_date__month=today.month
            )
        elif selected_period == 'year':
            sessions = sessions.filter(attendance_date__year=today.year)

        if selected_class:
            students = Student.objects.filter(
                student_class_id=selected_class,
                status='Active'
            ).order_by('roll_no')
        else:
            students = Student.objects.filter(
                status='Active'
            ).select_related('student_class').order_by('student_class', 'roll_no')
    else:
        return redirect('dashboard')

    context = {
        'sessions':        sessions,
        'students':        students,
        'classes':         Class.objects.filter(status='Active').select_related('grade', 'section'),
        'selected_class':  selected_class,
        'selected_period': selected_period,
    }

    return render(request, 'attendance/attendance_history.html', context)


@login_required
def student_attendance_history(request, student_id):
    """Individual student attendance history"""
    student = get_object_or_404(Student, pk=student_id)

    # Access control
    if request.user.is_teacher:
        try:
            teacher_profile = request.user.teacher_profile
            assigned_class = Class.objects.filter(class_teacher=teacher_profile).first()
            if not assigned_class or student.student_class != assigned_class:
                messages.error(request, 'Access denied.')
                return redirect('dashboard')
        except:
            messages.error(request, 'Access denied.')
            return redirect('dashboard')
    elif not request.user.is_principal:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    period = request.GET.get('period', 'month')
    today  = date.today()

    records = AttendanceRecord.objects.filter(
        student=student,
        session__is_completed=True
    ).select_related('session', 'session__class_info').order_by('-session__attendance_date')

    if period == 'week':
        records = records.filter(
            session__attendance_date__gte=today - timedelta(days=today.weekday())
        )
    elif period == 'month':
        records = records.filter(
            session__attendance_date__year=today.year,
            session__attendance_date__month=today.month
        )
    elif period == 'year':
        records = records.filter(session__attendance_date__year=today.year)
    # 'all' — no filter needed

    total   = records.count()
    present = records.filter(status='Present').count()
    absent  = records.filter(status='Absent').count()
    late    = records.filter(status='Late').count()
    leave   = records.filter(status='Leave').count()

    context = {
        'student':               student,
        'records':               records,
        'total':                 total,
        'present':               present,
        'absent':                absent,
        'late':                  late,
        'leave':                 leave,
        'attendance_percentage': round((present / total * 100) if total > 0 else 0, 1),
        'period':                period,
        'period_choices': [
            ('week',  'This Week'),
            ('month', 'This Month'),
            ('year',  'This Year'),
            ('all',   'All Time'),
        ],
    }

    return render(request, 'attendance/student_attendance_history.html', context)


# ==================== REPORT ====================

@login_required
def attendance_report(request):
    """Principal: Overall attendance report"""
    if not request.user.is_principal:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    today   = date.today()
    classes = Class.objects.filter(status='Active')

    report_data = []
    for c in classes:
        today_session = AttendanceSession.objects.filter(
            class_info=c,
            attendance_date=today
        ).first()

        if today_session:
            total      = AttendanceRecord.objects.filter(session=today_session).count()
            present    = AttendanceRecord.objects.filter(session=today_session, status='Present').count()
            percentage = round((present / total * 100) if total > 0 else 0, 1)
        else:
            total      = Student.objects.filter(student_class=c, status='Active').count()
            percentage = 0

        report_data.append({
            'class':            c,
            'total_students':   total,
            'attendance_taken': today_session is not None,
            'percentage':       percentage,
            'session':          today_session,
        })

    context = {
        'report_data': report_data,
        'today':       today,
    }

    return render(request, 'attendance/attendance_report.html', context)