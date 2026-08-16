from django.urls import path
from . import views

urlpatterns = [
path('transaction-main-heads/', views.transaction_head_page, name='transaction_main_head_page'),
path('transaction-head/fetch/', views.transaction_head_fetch),
path('transaction-head/update/', views.transaction_head_update),
path('transaction-head/delete/', views.transaction_head_delete),
]