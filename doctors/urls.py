from django.urls import path
from . import views

urlpatterns = [
    # =========================================================================
    # 📋 CORE INTERFACE AND WORKSPACE RENDERING VIEW CHANNELS
    # =========================================================================
    path('', views.doctor_list_view, name='doctor_list'),
    path('form/', views.doctor_form_view, name='doctor_add'),
    path('form/<int:pk>/', views.doctor_form_view, name='doctor_edit'),

    # =========================================================================
    # 🧪 FRONTEND INTERACTION FLOW AND AJAX PROCESSING ENDPOINTS
    # =========================================================================
    path('add/', views.store_doctor, name='ajax_store_doctor'),
    path('edit/<int:pk>/', views.update_doctor, name='ajax_update_doctor'),
    path('delete/<int:pk>/', views.delete_doctor, name='ajax_delete_doctor'),

    # =========================================================================
    # 🔍 REALTIME CORE SELECT2 MATRIX LOOKUP & DATA FETCH APIS
    # =========================================================================
    path('api/lookup-combo/', views.get_doctors_lookup_combo, name='api_doctors_lookup_combo'),
    path('api/lookup-sr/', views.get_sr_lookup_combo, name='api_sr_lookup_combo'),
    path('api/fetch-profile/', views.fetch_doctor_profile, name='api_fetch_doctor_profile'),
]