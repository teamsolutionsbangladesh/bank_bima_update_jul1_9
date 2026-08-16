from django.urls import path
from . import views

urlpatterns = [
    path('stores/', views.store_page, name='store_page'),
    path('store/store/', views.store_store, name='store_store'),
    path('store/fetch/', views.store_fetch, name='store_fetch'),
    path('store/update/', views.store_update, name='store_update'),
    path('store/delete/', views.store_delete, name='store_delete'),
]