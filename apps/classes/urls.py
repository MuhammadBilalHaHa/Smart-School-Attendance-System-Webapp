from django.urls import path
from . import views

urlpatterns = [
    path('', views.ClassListView.as_view(), name='class_list'),
    path('add/', views.ClassCreateView.as_view(), name='class_add'),
    path('<int:pk>/edit/', views.ClassUpdateView.as_view(), name='class_edit'),
    path('<int:pk>/delete/', views.ClassDeleteView.as_view(), name='class_delete'),
    path('ajax/add-grade/', views.add_grade_ajax, name='add_grade_ajax'),
    path('ajax/add-section/', views.add_section_ajax, name='add_section_ajax'),
]