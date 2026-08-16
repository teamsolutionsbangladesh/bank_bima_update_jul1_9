# urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Company Types
    path('company-types/', views.company_types_list, name='company_types_list'),
    path('company-types/create/', views.create_company_type, name='create_company_type'),
    path('company-types/update/<int:pk>/', views.update_company_type, name='update_company_type'),
    path('company-types/delete/<int:pk>/', views.delete_company_type, name='delete_company_type'),

    # Company Details
    path('company-details/', views.company_details_list, name='company_details_list'),
    path('company-details/create/', views.create_company_detail, name='company_detail_create'),
    path('company-details/update/<int:id>/', views.update_company_detail, name='company_detail_update'),
    path('company-details/delete/<int:id>/', views.delete_company_detail, name='company_detail_delete'),
]
