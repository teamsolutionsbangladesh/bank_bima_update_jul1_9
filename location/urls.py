from django.urls import path
from . import views

urlpatterns = [
    path('locations/', views.location_page, name='location_page'),

    path('location/store/', views.location_store, name='location_store'),
    path('location/update/', views.location_update, name='location_update'),
    path('location/delete/', views.location_delete, name='location_delete'),
    path('location/fetch/', views.location_fetch, name='location_fetch'),
]