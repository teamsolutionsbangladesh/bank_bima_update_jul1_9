# erp_core/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('page_init.urls')),
    path('', include('core.urls')),
    path('', include('pharmacy.urls')), 
    # path('pharmacy/', include('pharmacy.urls')),
    path('', include('company.urls')), 
    path('users/', include('users.urls')),
    path('', include('location.urls')),
    path('', include('bank.urls')),
    path('', include('store.urls')),
    path('', include('payment_method.urls')),
    path('', include('main_heads.urls')),
    path('', include('transaction_main_heads.urls')),
    path('', include('transaction_group.urls')),
    path('', include('transaction_head.urls')),    
    path('', include('transaction_with.urls')),    
    path('', include('transaction_with_user.urls')),    
    path('', include('corporates.urls')),
    path('', include('combo_load.urls')),
    path('', include('administrator.urls')),
    path('general/', include('general_transaction.urls')), 
    path('general/', include('general_transaction.urls_payment')), 
    path('diagnosis/', include('diagnosis.urls')),
    path('doctors/', include('doctors.urls')),
    path('representatives/', include('sr.urls')),

]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)