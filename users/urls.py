from django.urls import path
from users.views import roles
from users.views import super
from users.views import admin
from django.conf import settings
from django.conf.urls.static import static

app_name = "users"

urlpatterns = [
    # ================= ROLES =================
    path('roles/', roles.roles_list, name='roles_list'),
    path('roles/create/', roles.create_role, name='create_role'),
    path('roles/update/<int:pk>/', roles.update_role, name='update_role'),
    path('roles/delete/<int:pk>/', roles.delete_role, name='delete_role'),

    # ================= Super-Admin =================
    path('super-admin/', super.super_admin_list, name='super_admin_list'),
    path('super-admin/create/', super.create_super_admin, name='create_super_admin'),
    path('super-admin/update/<int:pk>/', super.update_super_admin, name='update_super_admin'),
    path('super-admin/delete/<int:pk>/', super.delete_super_admin, name='delete_super_admin'),

     # ================= Admin =================
    path('admin/', admin.admin_list, name='admin_list'),
    path('admin/create/', admin.create_admin, name='create_admin'),
    path('admin/update/<int:pk>/', admin.update_admin, name='update_admin'),
    path('admin/delete/<int:pk>/', admin.delete_admin, name='delete_admin'),
    path('admin/get-transaction-withs/', admin.get_transaction_withs_by_type, name='get_transaction_withs_by_type'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
