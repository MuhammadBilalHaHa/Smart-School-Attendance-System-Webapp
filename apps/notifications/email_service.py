from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.utils import timezone
from django.template.loader import render_to_string
from apps.notifications.models import EmailLog
from apps.students.models import Student, Guardian
from apps.attendance.models import AttendanceSession, AttendanceRecord
from apps.audit.models import AuditLog


class NotificationService:
    """Handle email notifications for attendance"""
    
    @staticmethod
    def get_student_guardian_emails(student):
        """Get all guardian emails for a student"""
        guardians = Guardian.objects.filter(student=student)
        return [
            {
                'email': g.email,
                'name': g.guardian_name,
            }
            for g in guardians if g.email
        ]
    
    @staticmethod
    def get_email_subject(attendance_status):
        """Get email subject based on status"""
        subjects = {
            'Present': 'Attendance Confirmation - Present Today',
            'Absent': 'Absence Alert - Your Child is Absent Today',
            'Late': 'Late Arrival Notice - Your Child Arrived Late Today',
            'Leave': 'Leave Status - Your Child is on Leave Today',
        }
        return subjects.get(attendance_status, 'Attendance Update')
    
    @staticmethod
    def get_status_colors():
        """Get color scheme based on status"""
        return {
            'Present': {
                'primary': '#059669',
                'background': '#ECFDF5',
                'border': '#A7F3D0',
                'icon': 'fa-circle-check',
                'badge': 'PRESENT'
            },
            'Absent': {
                'primary': '#DC2626',
                'background': '#FEF2F2',
                'border': '#FECACA',
                'icon': 'fa-circle-xmark',
                'badge': 'ABSENT'
            },
            'Late': {
                'primary': '#D97706',
                'background': '#FFFBEB',
                'border': '#FDE68A',
                'icon': 'fa-clock',
                'badge': 'LATE'
            },
            'Leave': {
                'primary': '#4B5563',
                'background': '#F3F4F6',
                'border': '#E5E7EB',
                'icon': 'fa-calendar-minus',
                'badge': 'ON LEAVE'
            },
        }
    
    @staticmethod
    def get_email_html(student, attendance_status, date):
        """Generate premium HTML email body"""
        colors = NotificationService.get_status_colors().get(attendance_status, NotificationService.get_status_colors()['Present'])
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
        </head>
        <body style="margin: 0; padding: 0; background-color: #F3F4F6; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
            
            <!-- Main Container -->
            <table width="100%" cellpadding="0" cellspacing="0" style="max-width: 600px; margin: 30px auto; background: #FFFFFF; border-radius: 16px; box-shadow: 0 4px 24px rgba(0,0,0,0.08); overflow: hidden;">
                
                <!-- Header -->
                <tr>
                    <td style="background: linear-gradient(135deg, #0A1628 0%, #1a2a4a 100%); padding: 30px 40px; text-align: center;">
                        <table width="100%" cellpadding="0" cellspacing="0">
                            <tr>
                                <td style="text-align: center; padding-bottom: 20px;">
                                    <i class="fas fa-graduation-cap" style="font-size: 36px; color: #C9A84C; display: inline-block; margin-bottom: 10px;"></i>
                                </td>
                            </tr>
                            <tr>
                                <td style="text-align: center;">
                                    <h1 style="color: #FFFFFF; font-size: 22px; font-weight: 700; margin: 0 0 5px 0; letter-spacing: -0.3px;">
                                        Smart Attendance System
                                    </h1>
                                    <p style="color: rgba(255,255,255,0.7); font-size: 13px; margin: 0; font-weight: 500;">
                                        Automated Attendance Notification
                                    </p>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
                
                <!-- Status Badge -->
                <tr>
                    <td style="padding: 30px 40px 0 40px;">
                        <table width="100%" cellpadding="0" cellspacing="0">
                            <tr>
                                <td style="text-align: center;">
                                    <div style="display: inline-block; background: {colors['background']}; border: 1px solid {colors['border']}; border-radius: 12px; padding: 15px 25px;">
                                        <i class="fas {colors['icon']}" style="font-size: 28px; color: {colors['primary']}; display: block; margin-bottom: 8px;"></i>
                                        <span style="color: {colors['primary']}; font-size: 16px; font-weight: 700; letter-spacing: 0.5px;">
                                            {colors['badge']}
                                        </span>
                                    </div>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
                
                <!-- Main Content -->
                <tr>
                    <td style="padding: 30px 40px;">
                        <table width="100%" cellpadding="0" cellspacing="0">
                            
                            <!-- Greeting -->
                            <tr>
                                <td style="padding-bottom: 20px;">
                                    <h2 style="color: #0A1628; font-size: 18px; font-weight: 600; margin: 0 0 8px 0;">
                                        Dear Parent / Guardian,
                                    </h2>
                                    <p style="color: #4B5563; font-size: 14px; line-height: 1.6; margin: 0;">
                                        This is an automated notification regarding your child's attendance status for today.
                                    </p>
                                </td>
                            </tr>
                            
                            <!-- Student Info Card -->
                            <tr>
                                <td style="padding-bottom: 25px;">
                                    <table width="100%" cellpadding="0" cellspacing="0" style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 12px;">
                                        <tr>
                                            <td style="padding: 20px 25px;">
                                                <table width="100%" cellpadding="0" cellspacing="0">
                                                    <tr>
                                                        <td style="padding-bottom: 12px;">
                                                            <span style="font-size: 11px; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 1px;">Student Information</span>
                                                        </td>
                                                    </tr>
                                                    <tr>
                                                        <td style="padding-bottom: 8px;">
                                                            <table width="100%" cellpadding="0" cellspacing="0">
                                                                <tr>
                                                                    <td width="50%" style="padding-bottom: 6px;">
                                                                        <span style="font-size: 12px; color: #64748B;">Student Name:</span>
                                                                        <span style="font-size: 13px; color: #0A1628; font-weight: 600; display: block;">{student.full_name}</span>
                                                                    </td>
                                                                    <td width="50%" style="padding-bottom: 6px;">
                                                                        <span style="font-size: 12px; color: #64748B;">Registration No:</span>
                                                                        <span style="font-size: 13px; color: #0A1628; font-weight: 600; display: block;">{student.registration_no}</span>
                                                                    </td>
                                                                </tr>
                                                                <tr>
                                                                    <td width="50%">
                                                                        <span style="font-size: 12px; color: #64748B;">Class:</span>
                                                                        <span style="font-size: 13px; color: #0A1628; font-weight: 600; display: block;">Grade {student.student_class.grade.grade_name}-{student.student_class.section.section_name}</span>
                                                                    </td>
                                                                    <td width="50%">
                                                                        <span style="font-size: 12px; color: #64748B;">Date:</span>
                                                                        <span style="font-size: 13px; color: #0A1628; font-weight: 600; display: block;">{date.strftime('%B %d, %Y')}</span>
                                                                    </td>
                                                                </tr>
                                                            </table>
                                                        </td>
                                                    </tr>
                                                </table>
                                            </td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>
                            
                            <!-- Status Message -->
                            <tr>
                                <td style="padding-bottom: 25px;">
                                    {NotificationService.get_status_message_html(student, attendance_status, colors)}
                                </td>
                            </tr>
                            
                            <!-- CTA Button -->
                            <tr>
                                <td style="text-align: center; padding-bottom: 10px;">
                                    <a href="#" style="display: inline-block; background: linear-gradient(135deg, #0A1628, #1a2a4a); color: #FFFFFF; text-decoration: none; padding: 12px 30px; border-radius: 10px; font-weight: 600; font-size: 14px;">
                                        <i class="fas fa-external-link-alt" style="margin-right: 8px; font-size: 12px;"></i>
                                        View Attendance Portal
                                    </a>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
                
                <!-- Footer -->
                <tr>
                    <td style="background: #F8FAFC; border-top: 1px solid #E2E8F0; padding: 20px 40px; text-align: center;">
                        <table width="100%" cellpadding="0" cellspacing="0">
                            <tr>
                                <td style="padding-bottom: 10px;">
                                    <p style="color: #64748B; font-size: 11px; line-height: 1.5; margin: 0;">
                                        This is an automated notification from Smart School Attendance System.
                                        Please do not reply to this email.
                                    </p>
                                </td>
                            </tr>
                            <tr>
                                <td style="padding-bottom: 8px;">
                                    <p style="color: #94A3B8; font-size: 10px; margin: 0;">
                                        <i class="fas fa-shield-alt" style="color: #C9A84C; margin-right: 4px;"></i>
                                        Secure & Automated Notification Service
                                    </p>
                                </td>
                            </tr>
                            <tr>
                                <td>
                                    <p style="color: #94A3B8; font-size: 9px; margin: 0;">
                                        &copy; {date.year} Smart School Attendance System. All rights reserved.
                                    </p>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
                
            </table>
        </body>
        </html>
        """
        return html
    
    @staticmethod
    def get_status_message_html(student, attendance_status, colors):
        """Get status-specific HTML message"""
        messages = {
            'Present': f"""
                <table width="100%" cellpadding="0" cellspacing="0" style="background: {colors['background']}; border: 1px solid {colors['border']}; border-radius: 12px;">
                    <tr>
                        <td style="padding: 20px 25px;">
                            <p style="color: {colors['primary']}; font-size: 14px; font-weight: 600; margin: 0 0 8px 0;">
                                <i class="fas fa-check-circle" style="margin-right: 8px;"></i>
                                Attendance Confirmed
                            </p>
                            <p style="color: #374151; font-size: 13px; line-height: 1.6; margin: 0;">
                                {student.full_name} was marked <strong style="color: {colors['primary']};">PRESENT</strong> in school today. 
                                We appreciate your commitment to your child's regular attendance and education.
                            </p>
                        </td>
                    </tr>
                </table>
            """,
            'Absent': f"""
                <table width="100%" cellpadding="0" cellspacing="0" style="background: {colors['background']}; border: 1px solid {colors['border']}; border-radius: 12px;">
                    <tr>
                        <td style="padding: 20px 25px;">
                            <p style="color: {colors['primary']}; font-size: 14px; font-weight: 600; margin: 0 0 8px 0;">
                                <i class="fas fa-exclamation-triangle" style="margin-right: 8px;"></i>
                                Absence Alert
                            </p>
                            <p style="color: #374151; font-size: 13px; line-height: 1.6; margin: 0;">
                                {student.full_name} was marked <strong style="color: {colors['primary']};">ABSENT</strong> from school today. 
                                If this absence is unexpected, please contact the school administration immediately.
                            </p>
                        </td>
                    </tr>
                </table>
            """,
            'Late': f"""
                <table width="100%" cellpadding="0" cellspacing="0" style="background: {colors['background']}; border: 1px solid {colors['border']}; border-radius: 12px;">
                    <tr>
                        <td style="padding: 20px 25px;">
                            <p style="color: {colors['primary']}; font-size: 14px; font-weight: 600; margin: 0 0 8px 0;">
                                <i class="fas fa-clock" style="margin-right: 8px;"></i>
                                Late Arrival Notice
                            </p>
                            <p style="color: #374151; font-size: 13px; line-height: 1.6; margin: 0;">
                                {student.full_name} arrived <strong style="color: {colors['primary']};">LATE</strong> to school today. 
                                We encourage punctuality to ensure your child doesn't miss important learning activities.
                            </p>
                        </td>
                    </tr>
                </table>
            """,
            'Leave': f"""
                <table width="100%" cellpadding="0" cellspacing="0" style="background: {colors['background']}; border: 1px solid {colors['border']}; border-radius: 12px;">
                    <tr>
                        <td style="padding: 20px 25px;">
                            <p style="color: {colors['primary']}; font-size: 14px; font-weight: 600; margin: 0 0 8px 0;">
                                <i class="fas fa-calendar-check" style="margin-right: 8px;"></i>
                                Leave Status Confirmed
                            </p>
                            <p style="color: #374151; font-size: 13px; line-height: 1.6; margin: 0;">
                                {student.full_name} is on <strong style="color: {colors['primary']};">LEAVE</strong> today. 
                                This absence has been approved and recorded in the system.
                            </p>
                        </td>
                    </tr>
                </table>
            """,
        }
        return messages.get(attendance_status, '')
    
    @staticmethod
    def get_plain_text_body(student, attendance_status, date):
        """Get plain text fallback email body"""
        messages = {
            'Present': f"""
Dear Parent / Guardian,

This is to confirm that {student.full_name} (Reg: {student.registration_no}) 
was PRESENT in school today ({date.strftime('%B %d, %Y')}).

Student Information:
- Name: {student.full_name}
- Registration No: {student.registration_no}
- Class: Grade {student.student_class.grade.grade_name}-{student.student_class.section.section_name}
- Date: {date.strftime('%B %d, %Y')}

We appreciate your commitment to your child's regular attendance.

---
Smart School Attendance System
This is an automated notification. Please do not reply.
            """,
            'Absent': f"""
Dear Parent / Guardian,

This is to inform you that {student.full_name} (Reg: {student.registration_no}) 
was ABSENT from school today ({date.strftime('%B %d, %Y')}).

Student Information:
- Name: {student.full_name}
- Registration No: {student.registration_no}
- Class: Grade {student.student_class.grade.grade_name}-{student.student_class.section.section_name}
- Date: {date.strftime('%B %d, %Y')}

If this absence is unexpected, please contact the school administration.

---
Smart School Attendance System
This is an automated notification. Please do not reply.
            """,
            'Late': f"""
Dear Parent / Guardian,

This is to inform you that {student.full_name} (Reg: {student.registration_no}) 
arrived LATE to school today ({date.strftime('%B %d, %Y')}).

Student Information:
- Name: {student.full_name}
- Registration No: {student.registration_no}
- Class: Grade {student.student_class.grade.grade_name}-{student.student_class.section.section_name}
- Date: {date.strftime('%B %d, %Y')}

We encourage punctuality to ensure your child doesn't miss important learning activities.

---
Smart School Attendance System
This is an automated notification. Please do not reply.
            """,
            'Leave': f"""
Dear Parent / Guardian,

This is to confirm that {student.full_name} (Reg: {student.registration_no}) 
is on LEAVE today ({date.strftime('%B %d, %Y')}).

Student Information:
- Name: {student.full_name}
- Registration No: {student.registration_no}
- Class: Grade {student.student_class.grade.grade_name}-{student.student_class.section.section_name}
- Date: {date.strftime('%B %d, %Y')}

This absence has been approved and recorded.

---
Smart School Attendance System
This is an automated notification. Please do not reply.
            """,
        }
        return messages.get(attendance_status, 'Attendance Update')
    
    @staticmethod
    def send_attendance_notification(session):
        """Send HTML emails to all guardians for an attendance session"""
        records = AttendanceRecord.objects.filter(session=session).select_related('student')
        
        total_sent = 0
        total_failed = 0
        
        for record in records:
            student = record.student
            guardians = NotificationService.get_student_guardian_emails(student)
            
            for guardian in guardians:
                # Check for duplicate
                existing = EmailLog.objects.filter(
                    session=session,
                    student=student,
                    email_type=record.status
                ).first()
                
                if existing:
                    continue  # Skip duplicates
                
                subject = NotificationService.get_email_subject(record.status)
                html_body = NotificationService.get_email_html(student, record.status, session.attendance_date)
                plain_body = NotificationService.get_plain_text_body(student, record.status, session.attendance_date)
                
                try:
                    email = EmailMultiAlternatives(
                        subject=subject,
                        body=plain_body,
                        from_email=settings.EMAIL_HOST_USER or 'noreply@school.com',
                        to=[guardian['email']],
                    )
                    email.attach_alternative(html_body, "text/html")
                    email.send(fail_silently=False)
                    
                    # Log success
                    EmailLog.objects.create(
                        session=session,
                        student=student,
                        recipient_email=guardian['email'],
                        guardian_name=guardian['name'],
                        email_type=record.status,
                        attendance_status=record.status,
                        delivery_status='Sent',
                    )
                    total_sent += 1
                    
                except Exception as e:
                    # Log failure
                    EmailLog.objects.create(
                        session=session,
                        student=student,
                        recipient_email=guardian['email'],
                        guardian_name=guardian['name'],
                        email_type=record.status,
                        attendance_status=record.status,
                        delivery_status='Failed',
                        error_message=str(e)[:500],
                    )
                    total_failed += 1
        
        # Update session
        session.notifications_sent = True
        session.save()
        
        return total_sent, total_failed
    
    @staticmethod
    def retry_failed_emails(session_id):
        """Retry failed emails for a session"""
        failed_logs = EmailLog.objects.filter(
            session_id=session_id,
            delivery_status='Failed',
            retry_count__lt=3
        )
        
        for log in failed_logs:
            try:
                student = log.student
                subject = NotificationService.get_email_subject(log.attendance_status)
                html_body = NotificationService.get_email_html(student, log.attendance_status, log.session.attendance_date)
                plain_body = NotificationService.get_plain_text_body(student, log.attendance_status, log.session.attendance_date)
                
                email = EmailMultiAlternatives(
                    subject=subject,
                    body=plain_body,
                    from_email=settings.EMAIL_HOST_USER or 'noreply@school.com',
                    to=[log.recipient_email],
                )
                email.attach_alternative(html_body, "text/html")
                email.send(fail_silently=False)
                
                log.delivery_status = 'Sent'
                log.error_message = None
                
            except Exception as e:
                log.retry_count += 1
                log.error_message = str(e)[:500]
            
            log.save()