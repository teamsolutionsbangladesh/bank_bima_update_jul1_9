from django.urls import path
from . import views

urlpatterns = [

    path('transaction_main_heads/get-transaction-main-heads-combo/', views.get_transaction_main_heads_combo, name='get_transaction_main_heads_combo'),
    path('transaction_main_heads/set-transaction-main-head-id/', views.set_transaction_main_head_id, name='set_transaction_main_head_id'),
    
  

]