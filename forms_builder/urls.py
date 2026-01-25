from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('forms/', views.FormListView.as_view(), name='form_list'),
    path('forms/create/', views.FormCreateView.as_view(), name='form_create'),
    path('forms/<int:pk>/edit/', views.FormUpdateView.as_view(), name='form_edit'),
    path('forms/<int:pk>/delete/', views.FormDeleteView.as_view(), name='form_delete'),
    path('forms/<int:pk>/builder/', views.form_builder, name='form_builder'),
    path('forms/<int:form_pk>/add-field/', views.add_field, name='add_field'),
    path('forms/<int:form_pk>/reorder-fields/', views.reorder_fields, name='reorder_fields'),
    path('fields/<int:field_pk>/', views.get_field, name='get_field'),
    path('fields/<int:field_pk>/update/', views.update_field, name='update_field'),
    path('fields/<int:field_pk>/delete/', views.delete_field, name='delete_field'),
    path('forms/<int:form_pk>/submissions/', views.submission_list, name='submission_list'),
    path('submissions/<int:pk>/', views.submission_detail, name='submission_detail'),
    path('forms/<int:form_pk>/export/', views.export_csv, name='export_csv'),
    
    # Public form submission
    path('f/<slug:slug>/', views.form_submit_view, name='form_submit'),
    path('f/<slug:slug>/success/', views.form_success, name='form_success'),
    path('f/<slug:slug>/my-submission/', views.my_submission, name='my_submission'),
    
    # API endpoints
    path('api/facultes/', views.api_facultes, name='api_facultes'),
    path('api/domaines/', views.api_domaines, name='api_domaines'),
    path('api/fields/<int:field_pk>/options/', views.api_child_options, name='api_child_options'),
]
