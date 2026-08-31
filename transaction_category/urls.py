from django.urls import path
from . import views

urlpatterns = [
    # Main template render view routing path setup
    path('', views.transaction_category_view, name='transaction_category_page'),
    
    # Save Dynamic Action Endpoint
    path('save/', views.save_transaction_category, name='save_category'),

    path('update/', views.update_transaction_category, name='update_category'),
    
    # Grid Table Dynamic AJAX pipeline engine loader URL
    path('load-transaction-category/', views.load_transaction_category, name='load_transaction_category'),
    
    
    # Delete Endpoint
    path('delete/', views.delete_transaction_category, name='delete_category'),
]