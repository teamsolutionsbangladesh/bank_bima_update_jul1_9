from django.urls import path
from . import views

urlpatterns = [
    path('corporates/', views.corporates_page, name='corporates_page'),
    path('corporate/store/', views.corporate_store, name='corporate_store'),
    path('corporate/fetch/', views.corporate_fetch, name='corporate_fetch'),
    path('corporate/update/', views.corporate_update, name='corporate_update'),
    path('corporate/delete/', views.corporate_delete, name='corporate_delete'),
]
