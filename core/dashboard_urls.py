from django.urls import path
from core import views_dashboard

urlpatterns = [
    path('', views_dashboard.dashboard, name='dashboard'),
]
