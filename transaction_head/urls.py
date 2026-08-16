from django.urls import path
from . import views

urlpatterns = [
    path('transaction-heads/', views.transaction_head_page, name='transaction_head_page'),
    path('transaction-heads/transaction-heads-form/', views.transaction_head_form, name='transaction_head_form'),
    path('transaction-heads/save-transaction-heads/', views.save_transaction_heads, name='save_transaction_heads'),
    path('transaction-heads/update-transaction-heads/', views.update_transaction_heads, name='update_transaction_heads'),
    path('transaction-heads/load-transaction-head/', views.load_transaction_head, name='load_transaction_head'),
    # path('transaction-heads/store/', views.transaction_groupe_store),
    # path('transaction-groupe/fetch/', views.transaction_groupe_fetch),
    # path('transaction-groupe/update/', views.transaction_groupe_update),
    # path('transaction-groupe/delete/', views.transaction_groupe_delete),

]