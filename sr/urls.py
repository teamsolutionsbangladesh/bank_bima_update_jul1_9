from django.urls import path
from . import views

urlpatterns = [
    path('sr/', views.sr_list_view, name='sr_list'),
    path('sr/form/', views.sr_form_view, name='sr_add'),
    path('sr/form/<int:pk>/', views.sr_form_view, name='sr_edit'),

    path('sr/add/', views.store_sr, name='ajax_store_sr'),
    path('sr/edit/<int:pk>/', views.update_sr, name='ajax_update_sr'),
    path('sr/delete/<int:pk>/', views.delete_sr, name='ajax_delete_sr'),

    path('api/fetch-sr-profile/', views.fetch_sr_profile, name='api_fetch_sr_profile'),
]