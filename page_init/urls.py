from django.urls import path
from . import views

urlpatterns = [
    path('page-init/', views.page_init, name='page_init'),
    path('get-withs/', views.get_withs, name='get_withs'),
    path(
        'get-transaction-groups/',
        views.get_transaction_groups,
        name='get_transaction_groups'
    ),

    path('add-page-init/', views.add_page_init, name='add_page_init'),
    path('save-page-init/', views.save_page_init, name='save_page_init'),
    path('update-page-init/', views.update_page_init, name='update_page_init'),
    path('remove-subject/', views.remove_subject, name='remove_subject'),
    path('load-page-init-list/', views.load_page_init_list, name='load_page_init_list'),
    path('fetch-data-for-edit/', views.fetch_data_for_edit, name='fetch_data_for_edit'),
]