from django.urls import path
from . import views

urlpatterns = [
    path('transaction-withs/', views.transaction_with_page, name='transaction_with_page'),
    path('load-transaction-with/', views.load_transaction_with, name='load_transaction_with'),
    # path('transaction-with/store/', views.transaction_with_store),
    path('transaction-with-fetch-data/', views.transaction_with_fetch_data),
    path('save-transaction-with/', views.save_transaction_with),
    path('update-transaction-with/', views.update_transaction_with),
    path('delete-transaction-with/', views.delete_transaction_with),
]