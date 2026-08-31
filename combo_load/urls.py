from django.urls import path
from general_transaction import views
from . import views

urlpatterns = [

    path('combo_load/transaction-method-combo/', views.transaction_method_combo, name='transaction_method_combo'),
    path('combo_load/transaction-group-combo/', views.transaction_group_combo, name='transaction_group_combo'),
    path('combo_load/transaction-group-combo-on-main-head/', views.transaction_group_combo_on_main_head, name='transaction_group_combo_on_main_head'),
    path('combo_load/transaction-category-combo/', views.transaction_category_combo, name='transaction_category_combo'),
    path('combo_load/transaction-head-combo/', views.transaction_head_combo, name='transaction_head_combo'),

    path('combo_load/transaction-with-method-combo/', views.transaction_with_method_combo, name='transaction_with_method_combo'),
    path('combo_load/transaction-with-combo/', views.transaction_with_combo, name='transaction_with_combo'),
    path('combo_load/transaction-with-user-combo/', views.transaction_with_user_combo, name='transaction_with_user_combo'),
    
    path('combo_load/user-role-combo/', views.user_role_combo, name='user_role_combo'),

    # path('combo_load/get-item-categories-combo/', views.get_item_categories_combo, name='get_item_categories_combo'),

    path('combo_load/get-transaction-main-heads-combo/', views.get_transaction_main_heads_combo, name='get_transaction_main_heads_combo'),
    
    path('combo_load/fetch-combo-data/', views.fetch_combo_data, name='fetch_combo_data'),

]
