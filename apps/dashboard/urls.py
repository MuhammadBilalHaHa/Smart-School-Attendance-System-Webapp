from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('principal/', views.principal_dashboard, name='principal_dashboard'),
    path('teacher/', views.teacher_dashboard, name='teacher_dashboard'),
]