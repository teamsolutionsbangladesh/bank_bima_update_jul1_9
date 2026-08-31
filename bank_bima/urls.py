from django.urls import path
from . import views


urlpatterns = [
    path('advertisement-sales/add/', views.advertisement_sales_add, name='bank_bima_advertisement_sales_add'),
    path('advertisement-sales/', views.advertisement_sales_list, name='bank_bima_advertisement_sales'),
    path('advertisement-sales/load/', views.advertisement_sales_load, name='bank_bima_advertisement_sales_load'),
    path('advertisement-sales/edit/<int:id>/', views.advertisement_sales_edit, name='bank_bima_advertisement_sales_edit'),
    path('get-page-init-add-payment/', views.advertisement_sales_page_init, name='bank_bima_get_page_init_add_payment'),
    path('product-search/', views.advertisement_sales_product_search, name='bank_bima_product_search'),
    path('payment/save-payment/', views.advertisement_sales_save, name='bank_bima_save_payment'),

    path('printing-sales/add/', views.printing_sales_add, name='bank_bima_printing_sales_add'),
    path('printing-sales/', views.printing_sales_list, name='bank_bima_printing_sales'),
    path('printing-sales/load/', views.printing_sales_load, name='bank_bima_printing_sales_load'),
    path('printing-sales/edit/<int:id>/', views.printing_sales_edit, name='bank_bima_printing_sales_edit'),
    path('printing-sales/get-page-init-add-payment/', views.printing_sales_page_init, name='bank_bima_printing_sales_get_page_init_add_payment'),
    path('printing-sales/product-search/', views.printing_sales_product_search, name='bank_bima_printing_sales_product_search'),
    path('printing-sales/payment/save-payment/', views.printing_sales_save, name='bank_bima_printing_sales_save_payment'),

    path('general-transaction/payment/', views.bank_bima_general_transaction_payment_list, name='bank_bima_general_transaction_payment_list'),
    path('general-transaction/payment/add/', views.bank_bima_general_transaction_payment_add, name='bank_bima_general_transaction_payment_add'),
    path('general-transaction/receive/', views.bank_bima_general_transaction_receive_list, name='bank_bima_general_transaction_receive_list'),
    path('general-transaction/receive/add/', views.bank_bima_general_transaction_receive_add, name='bank_bima_general_transaction_receive_add'),

    path('office-bazar/add/', views.office_bazar_add, name='bank_bima_office_bazar_add'),
    path('office-bazar/', views.office_bazar_list, name='bank_bima_office_bazar'),
    path('office-bazar/load/', views.advertisement_sales_load, name='bank_bima_office_bazar_load'),
    path('office-bazar/edit/<int:id>/', views.advertisement_sales_edit, name='bank_bima_office_bazar_edit'),
    path('office-bazar/get-page-init-add-payment/', views.office_bazar_page_init, name='bank_bima_office_bazar_get_page_init_add_payment'),
    path('office-bazar/product-search/', views.advertisement_sales_product_search, name='bank_bima_office_bazar_product_search'),
    path('office-bazar/payment/save-payment/', views.advertisement_sales_save, name='bank_bima_office_bazar_save_payment'),
]
