from django.urls import path
from . import views

urlpatterns = [
    path('', views.StudentListView.as_view(), name='student_list'),
    path('<int:pk>/', views.StudentDetailView.as_view(), name='student_detail'),
    path('add/', views.StudentCreateView.as_view(), name='student_add'),
    path('<int:pk>/edit/', views.StudentUpdateView.as_view(), name='student_edit'),
    path('<int:pk>/delete/', views.StudentDeleteView.as_view(), name='student_delete'),
    path('<int:student_id>/guardian/add/', views.add_guardian, name='add_guardian'),
    path('guardian/<int:guardian_id>/edit/', views.edit_guardian, name='edit_guardian'),
    path('guardian/<int:guardian_id>/delete/', views.delete_guardian, name='delete_guardian'),
]