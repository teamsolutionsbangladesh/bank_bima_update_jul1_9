from django.urls import path
from general_transaction import views
from . import views

urlpatterns = [
   
    # page init
    path('get-page-init-add-payment/', views.get_page_init_add_payment, name='get_page_init_add_payment'),
    
    path('product-search/', views.product_search, name='general-product-search'),
    path('payment/load/', views.payment_list_load, name='payment_list_load'),
    path('payment/report/pdf/', views.payment_report_pdf, name='payment_report_pdf'),
    path('get-transaction-with-combo-p/', views.get_transaction_with_combo_p,name="get_transaction_with_combo_p"),
    path('payment/save-payment/', views.save_general_payment, name='save_payment'),


    path('receive/add/', views.add_receive_page, name='add_receive_page'),
    path('receive/', views.receive_list, name='receive_list'),
    path('receive/save-receive/', views.save_general_receive, name='save_general_receive'),
    path('receive/load/', views.receive_list_load, name='receive_list_load'),
    path('receive/report/pdf/', views.receive_report_pdf, name='receive_report_pdf'),
    path('get-transaction-with-combo-r/', views.get_transaction_with_combo_r,name="get_transaction_with_combo_r"),
    path('get-supplier-by-tran-with-g/', views.get_supplier_by_tran_with_g, name='get_supplier_by_tran_with_g'),
    path('get-supplier-combo-g/', views.get_supplier_combo_g, name='get_supplier_combo_g'),


    # office bazar

    # path('payment/add-payment-ob/', views.add_payment_page_ob, name='add_payment_page_ob'),
    path('get-transaction-with-combo-ob/', views.get_transaction_with_combo_ob,name="get_transaction_with_combo_ob"),
    path('payment/load-ob', views.payment_list_load_ob, name='payment_list_load_ob'),
    path('payment/bazar', views.payment_list_ob, name='payment_list_ob'),
    path('get-supplier-by-tran-with-ob/', views.get_supplier_by_tran_with_ob, name='get_supplier_by_tran_with_ob'),
    path('payment/save-payment-ob/', views.save_general_payment_ob, name='save_payment_ob'),
    
    
    # setup
    
    # path('setup/transaction-with-user-form/', views.transaction_with_user_form, name='transaction_with_user_form'),

    # PARTY PAYMENT
    path('party-payment/',views.party_payment_list,name='party_payment_list'),
    path(
    'party-payment/load/',
    views.party_payment_list_load,
    name='party_payment_list_load'
    ),

    path(
            'get-tran-main-heads/',
            views.get_tran_main_heads,
            name='get_tran_main_heads'
        ),

    path(
        'api/tran-withs/',
        views.get_tran_withs,
        name='get_tran_withs'
    ),

    path(
        'api/tran-users/',
        views.get_tran_users,
        name='get_tran_users'
    ),

    path(
        'party-payment/details/<int:id>/',
        views.party_payment_details,
        name='party_payment_details'
    ),

    path(
        'party-payment/payment-form/<int:id>/',
        views.party_payment_form,
        name='party_payment_form'
    ),

    path(
        "party-payment/process/<int:id>/",
        views.process_party_payment,
        name="process_party_payment"
    ),

    path(
        "process-fifo-payment/",
        views.process_fifo_payment,
        name="process_fifo_payment"
    ),
    path('reports/party-payment/', views.party_payment_report_pdf, name='party_payment_report_pdf'),

    path(
    "payment/edit/<int:id>/",
    views.edit_payment_page,
    name="edit_payment_page"
),

    

]