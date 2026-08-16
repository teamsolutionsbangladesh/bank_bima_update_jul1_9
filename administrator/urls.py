from django.urls import path
from general_transaction import views
from . import views

urlpatterns = [
    
    path('administrator/save-transaction-with-user/', views.save_transaction_with_user, name='save_transaction_with_user'),
    


]