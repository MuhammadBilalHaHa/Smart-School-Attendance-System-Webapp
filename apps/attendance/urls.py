from django.urls import path
from . import views

urlpatterns = [
    path('', views.attendance_dashboard, name='attendance_dashboard'),
    path('start/', views.start_attendance, name='start_attendance'),
    path('create-session/', views.create_session, name='create_session'),
    path('take/<int:session_id>/', views.take_attendance, name='take_attendance'),
    path('camera/<int:session_id>/', views.camera_attendance, name='camera_attendance'),
    path('process-camera/<int:session_id>/', views.process_camera_attendance, name='process_camera'),
    path('summary/<int:session_id>/', views.attendance_summary, name='attendance_summary'),
    path('history/', views.attendance_history, name='attendance_history'),
    path('report/', views.attendance_report, name='attendance_report'),
    path('reset/<int:session_id>/', views.reset_attendance, name='reset_attendance'),
    path('finalize/<int:session_id>/', views.finalize_attendance, name='finalize_attendance'),
    path('retry-emails/<int:session_id>/', views.retry_emails, name='retry_emails'),
    path('email-logs/<int:session_id>/', views.email_logs, name='email_logs'),
    path('principal-reset/<int:session_id>/', views.principal_reset_attendance, name='principal_reset_attendance'),
    path('history/',                                  views.attendance_history,         name='attendance_history'),
path('student/<int:student_id>/history/',         views.student_attendance_history, name='student_attendance_history'),
]