from django.urls import path
from . import views

urlpatterns = [
    path('', views.TeacherListView.as_view(), name='teacher_list'),
    path('add/', views.TeacherCreateView.as_view(), name='teacher_add'),
    path('<int:pk>/edit/', views.TeacherUpdateView.as_view(), name='teacher_edit'),
    path('<int:pk>/delete/', views.TeacherDeleteView.as_view(), name='teacher_delete'),
]