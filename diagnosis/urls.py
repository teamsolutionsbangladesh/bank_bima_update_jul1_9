from django.urls import path
from . import views, tran_views

urlpatterns = [
    # 1. Main View UI Listing Gateway Endpoints
    path('patients/', views.patient_list_view, name='diagnosis_patient_list'),
    path('product-search/', views.product_search, name='diagnosis-product-search'),
    
    # CRITICAL FIX HERE: Direct map to views.patient_form_view instead of list_view
    path('patients/entry/', views.patient_form_view, name='patient_form'),
    path('patients/<int:pk>/edit/', views.patient_form_view, name='patient_edit_form'),
    
    # 2. AJAX Dynamic Endpoints Processing Matrix 
    path('patients/fetch/', views.fetch_patient, name='fetch_patient'),
    path('patients/store/', views.store_patient, name='store_patient'),
    path('patients/<int:pk>/update/', views.update_patient, name='update_patient'),
    path('patients/<int:pk>/delete/', views.delete_patient, name='delete_patient'),

    # referral

    path('referral/setup/', views.referral_setup_page, name='diagnosis_referral_setup'),  # #codex
    path('referral/sr/setup/', views.referral_sr_setup_page, name='diagnosis_referral_sr_setup'),  # #codex
    path('referral/groups/', views.referral_group_combo, name='diagnosis_referral_groups'),  # #codex
    path('referral/tests/', views.referral_tests_by_group, name='diagnosis_referral_tests'),  # #codex
    path('referral/saved-groups/', views.referral_saved_groups, name='diagnosis_referral_saved_groups'),  # #codex
    path('referral/save/', views.save_referral_setup, name='diagnosis_referral_save'),  # #codex
    path('referral/copy/', views.copy_referral_setup, name='diagnosis_referral_copy'),  # #codex
    path('referral/sr/tests/', views.referral_sr_tests_by_group, name='diagnosis_referral_sr_tests'),  # #codex
    path('referral/sr/saved-groups/', views.referral_sr_saved_groups, name='diagnosis_referral_sr_saved_groups'),  # #codex
    path('referral/sr/save/', views.save_referral_sr_setup, name='diagnosis_referral_sr_save'),  # #codex
    path('referral/sr/copy/', views.copy_referral_sr_setup, name='diagnosis_referral_sr_copy'),  # #codex
    path('referral/report/', views.referral_report_page, name='diagnosis_referral_report'),  # #codex
    path('referral/report/providers/', views.referral_report_providers, name='diagnosis_referral_report_providers'),  # #codex
    path('referral/report/data/', views.referral_report_data, name='diagnosis_referral_report_data'),  # #codex
    path('referral/report/pdf/', views.referral_report_pdf, name='diagnosis_referral_report_pdf'),  # #codex




    path('payment/add-payment/', tran_views.add_diagnosis_payment_page, name='add_diagnosis_payment_page'),
    path('payment/', tran_views.diag_payment_list, name='diag_payment_list'),
    path('get-page-init-add-payment/', tran_views.get_page_init_add_payment, name='get_page_init_add_payment'),
    
    path('product-search/', tran_views.product_search, name='general-product-search'),
    path('payment/load/', tran_views.payment_list_load, name='payment_list_load'),
    path('payment/report/pdf/', tran_views.payment_report_pdf, name='payment_report_pdf'),
    path('get-transaction-with-combo-p/', tran_views.get_transaction_with_combo_p,name="get_transaction_with_combo_p"),
    # path('payment/save-payment/', tran_views.save_general_payment, name='save_payment'),


    path('receive/add/', tran_views.add_receive_page, name='add_receive_page'),
    path('receive/', tran_views.receive_list, name='receive_list'),
    path('receive/save-receive/', tran_views.save_general_receive, name='save_general_receive'),
    path('receive/load/', tran_views.receive_list_load, name='receive_list_load'),
    path('receive/report/pdf/', tran_views.receive_report_pdf, name='receive_report_pdf'),
    path('get-transaction-with-combo-r/', tran_views.get_transaction_with_combo_r,name="get_transaction_with_combo_r"),
    path('get-supplier-by-tran-with-g/', tran_views.get_supplier_by_tran_with_g, name='get_supplier_by_tran_with_g'),
    path('get-supplier-combo-g/', tran_views.get_supplier_combo_g, name='get_supplier_combo_g'),


    # office bazar

    path('payment/add-payment-ob/', tran_views.add_payment_page_ob, name='add_payment_page_ob'),
    path('get-transaction-with-combo-ob/', tran_views.get_transaction_with_combo_ob,name="get_transaction_with_combo_ob"),
    path('payment/load-ob', tran_views.payment_list_load_ob, name='payment_list_load_ob'),
    path('payment/bazar', tran_views.payment_list_ob, name='payment_list_ob'),
    path('get-supplier-by-tran-with-ob/', tran_views.get_supplier_by_tran_with_ob, name='get_supplier_by_tran_with_ob'),
    path('payment/save-payment-ob/', tran_views.save_general_payment_ob, name='save_payment_ob'),
    
    # PARTY PAYMENT  # codex change
    path('party-payment/', tran_views.diagnosis_party_payment_list, name='diagnosis_party_payment_list'),  # codex change
    path('party-payment/load/', tran_views.diagnosis_party_payment_list_load, name='diagnosis_party_payment_list_load'),  # codex change
    path('party-payment/payment-form/<int:id>/', tran_views.diagnosis_party_payment_form, name='diagnosis_party_payment_form'),  # codex change
    path('party-payment/process/<int:id>/', tran_views.process_diagnosis_party_payment, name='process_diagnosis_party_payment'),  # codex change
    path('party-payment/process-fifo-payment/', tran_views.process_diagnosis_party_fifo_payment, name='process_diagnosis_party_fifo_payment'),  # codex change
    path('reports/party-payment/', tran_views.diagnosis_party_payment_report_pdf, name='diagnosis_party_payment_report_pdf'),  # codex change


    path('api/autocomplete/doctor/', views.autocomplete_doctor, name='api_autocomplete_doctor'),
    path('api/autocomplete/sr/', views.autocomplete_sr, name='api_autocomplete_sr'),


    #    diagnosis
path(
    "payment-form/<int:id>/",
    tran_views.diagnosis_payment_form,
    name="diagnosis_payment_form"
),

path(
    "process-payment/<int:id>/",
    tran_views.process_diagnosis_payment,
    name="process_diagnosis_payment"
),
    path("payment/save-payment/",tran_views.save_diagnosis_payment,name="save_diagnosis_payment"),
    path('payment/edit/<int:id>/', tran_views.edit_diagnosis_payment_page, name='edit_diagnosis_payment_page'),  # codex change

    path("payment-list-load/",tran_views.diagnosis_payment_list_load,name="diagnosis_payment_list_load"),
    path("reports/salesman/transaction-summary/", tran_views.diagnosis_salesman_transaction_summary_page, name="diagnosis_salesman_transaction_summary"),  # codex change
    path("reports/salesman/transaction-details/", tran_views.diagnosis_salesman_transaction_details_page, name="diagnosis_salesman_transaction_details"),  # codex change
    path("reports/salesman/transaction-details/load/", tran_views.diagnosis_salesman_transaction_details_load, name="diagnosis_salesman_transaction_details_load"),  # codex change
    path('api/autocomplete/doctor/', views.autocomplete_doctor, name='api_autocomplete_doctor'),
    path('api/autocomplete/sr/', views.autocomplete_sr, name='api_autocomplete_sr'),
    path('filter-doctor-combo/', tran_views.diagnosis_filter_doctor_combo, name='diagnosis_filter_doctor_combo'),  # codex change
    path('filter-sr-combo/', tran_views.diagnosis_filter_sr_combo, name='diagnosis_filter_sr_combo'),  # codex change
    path('filter-patient-combo/', tran_views.diagnosis_filter_patient_combo, name='diagnosis_filter_patient_combo'),  # codex change
    path('filter-tran-by-combo/', tran_views.diagnosis_filter_tran_by_combo, name='diagnosis_filter_tran_by_combo'), 

    path(
    "payment/report/pdf/",
    tran_views.diagnosis_payment_report_pdf,
    name="diagnosis_payment_report_pdf"
),

]
