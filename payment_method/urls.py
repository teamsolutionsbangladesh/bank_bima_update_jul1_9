from django.urls import path
from . import views

urlpatterns = [
path('payment-methods/', views.payment_method_page, name='payment_method_page'),
path('payment-method/store/', views.payment_method_store),
path('payment-method/fetch/', views.payment_method_fetch),
path('payment-method/update/', views.payment_method_update),
path('payment-method/delete/', views.payment_method_delete),
]