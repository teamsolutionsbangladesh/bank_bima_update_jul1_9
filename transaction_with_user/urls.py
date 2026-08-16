from django.urls import path
from . import views

urlpatterns = [
    path('transaction-with-user-form/', views.transaction_with_user_form, name='transaction_with_user_form'),    
    path('load-transaction-with-user/', views.load_transaction_with_user, name='load_transaction_with_user'),
    # # path('transaction-with/store/', views.transaction_with_store),
    path('transaction-with-user-fetch-data/', views.transaction_with_user_fetch_data),
    path('save-transaction-with-user/', views.save_transaction_with_user),
    path('update-transaction-with-user/', views.update_transaction_with_user),
    path('delete-transaction-with-user/', views.delete_transaction_with_user),
]