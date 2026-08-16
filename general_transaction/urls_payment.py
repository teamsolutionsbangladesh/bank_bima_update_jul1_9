from django.urls import path
from general_transaction import views
from . import views

urlpatterns = [
    # # PAGE
    path('payment/add-payment/', views.add_payment_page, name='add_payment_page'),
    
    # # page init
    # path('get-page-init-add-payment/', views.get_page_init_add_payment, name='get_page_init_add_payment'),
    
    path('payment/', views.payment_list, name='payment_list'),


]