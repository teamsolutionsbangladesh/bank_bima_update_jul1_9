from django.urls import path
from . import views

urlpatterns = [
    path('banks/', views.bank_page, name='bank_page'),

    path('bank/store/', views.bank_store, name='bank_store'),
    path('bank/fetch/', views.bank_fetch, name='bank_fetch'),
    path('bank/update/', views.bank_update, name='bank_update'),
    path('bank/delete/', views.bank_delete, name='bank_delete'),
]