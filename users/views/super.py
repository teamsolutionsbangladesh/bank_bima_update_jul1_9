from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from core.models import LoginUsers
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.hashers import make_password
from django.conf import settings
import os
from core.models import CompanyDetails, LocationInfos, UserInfos  # #codex
from django.db import connection  # #codex

# ==============================
# SUPER ADMIN CRUD
# ==============================

SUPER_ADMIN_ROLE_ID = 1  # Adjust based on your Roles table

def _build_media_url(file_name):  # #codex
    if not file_name:  # #codex
        return None  # #codex
    if str(file_name).startswith(('/media/', 'http://', 'https://')):  # #codex
        return file_name  # #codex
    return f"{settings.MEDIA_URL}{file_name}"  # #codex


def _location_label(location):  # #codex
    if not location:  # #codex
        return ""  # #codex
    return " - ".join(filter(None, [location.division, location.district, location.upazila]))  # #codex


def _sync_super_admin_info(sa, company_id=None, location_id=None, password=None):  # #codex
    with connection.cursor() as cursor:  # #codex
        cursor.execute(  # #codex
            "SELECT id FROM user__infos WHERE login_user_id=%s AND user_role=%s LIMIT 1",  # #codex
            [sa.user_id, SUPER_ADMIN_ROLE_ID]  # #codex
        )  # #codex
        row = cursor.fetchone()  # #codex
        if row:  # #codex
            cursor.execute("""
                UPDATE user__infos
                SET user_name=%s, user_email=%s, user_phone=%s, loc_id=%s, company_id=%s,
                    password=COALESCE(%s, password), image=%s, updated_at=NOW()
                WHERE id=%s
            """, [  # #codex
                sa.user_name, sa.user_email, sa.user_phone, location_id, company_id,  # #codex
                password, sa.image, row[0]  # #codex
            ])  # #codex
        else:  # #codex
            cursor.execute("""
                INSERT INTO user__infos (
                    user_id, login_user_id, user_name, user_email, user_phone, loc_id,
                    user_role, tran_method, tran_with_id, password, image, company_id,
                    status, added_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """, [  # #codex
                sa.user_id, sa.user_id, sa.user_name, sa.user_email, sa.user_phone, location_id,  # #codex
                SUPER_ADMIN_ROLE_ID, "", 0, password or sa.password, sa.image, company_id,  # #codex
                1  # #codex
            ])  # #codex


def super_admin_list(request):
    super_admins = LoginUsers.objects.filter(user_role_id=SUPER_ADMIN_ROLE_ID).order_by('id')
    companies = CompanyDetails.objects.filter(status=1).order_by('company_name')  # #codex
    locations = LocationInfos.objects.filter(status=1).order_by('division', 'district', 'upazila')  # #codex
    user_infos = UserInfos.objects.filter(user_role=SUPER_ADMIN_ROLE_ID)  # #codex
    info_map = {str(info.login_user_id): info for info in user_infos}  # #codex
    super_admin_rows = []  # #codex
    for sa in super_admins:  # #codex
        info = info_map.get(str(sa.user_id))  # #codex
        location = next((loc for loc in locations if info and loc.id == info.loc_id), None)  # #codex
        super_admin_rows.append({  # #codex
            "id": sa.id,  # #codex
            "user_id": sa.user_id,  # #codex
            "name": sa.user_name,  # #codex
            "email": sa.user_email,  # #codex
            "phone": sa.user_phone,  # #codex
            "image": sa.image,  # #codex
            "logo_url": _build_media_url(sa.image),  # #codex
            "company_id": sa.company_id or (info.company_id if info else ""),  # #codex
            "company_name": sa.company.company_name if sa.company else "",  # #codex
            "location_id": info.loc_id if info else "",  # #codex
            "location_name": _location_label(location),  # #codex
        })  # #codex
    return render(request, 'users/super_admin_list.html', {
        'super_admins': super_admin_rows,  # #codex
        'companies': companies,  # #codex
        'locations': locations,  # #codex
    })


@csrf_exempt
def create_super_admin(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        company_id = request.POST.get("company_id")  # #codex
        location_id = request.POST.get("location_id")  # #codex
        logo_file = request.FILES.get("logo")
        logo_name = None
        logo_url = None

        if logo_file:
            fs = FileSystemStorage(location=settings.MEDIA_ROOT, base_url=settings.MEDIA_URL)
            logo_name = fs.save(logo_file.name, logo_file)
            logo_url = fs.url(logo_name)  # <-- this gives proper URL

        if not name or not email or not phone or not password or not confirm_password or not company_id or not location_id:  # #codex
            return JsonResponse({"success": False, "message": "All required fields are mandatory"})

        if password != confirm_password:
            return JsonResponse({"success": False, "message": "Passwords do not match"})

        company = get_object_or_404(CompanyDetails, company_id=company_id, status=1)  # #codex
        location = get_object_or_404(LocationInfos, pk=location_id, status=1)  # #codex
        hashed_password = make_password(password)  # #codex

        last = LoginUsers.objects.filter(user_role_id=SUPER_ADMIN_ROLE_ID).order_by('id').last()
        if last and last.user_id.startswith("SA"):
            last_num = int(last.user_id[2:])
            next_id = f"SA{last_num + 1:09d}"
        else:
            next_id = "SA000000001"
        next_db_id = (LoginUsers.objects.order_by('-id').values_list('id', flat=True).first() or 0) + 1  # #codex

        sa = LoginUsers.objects.create(
            id=next_db_id,  # #codex
            user_id=next_id,
            user_name=name,
            user_email=email,
            user_phone=phone,
            password=hashed_password,  # #codex
            image=logo_name,  # store file name in DB
            company_id=company.company_id,  # #codex
            user_role_id=SUPER_ADMIN_ROLE_ID,
            status=1
        )
        _sync_super_admin_info(sa, company.company_id, location.id, hashed_password)  # #codex
        sa = LoginUsers.objects.get(user_id=next_id)  # #codex

        return JsonResponse({
            "success": True,
            "id": sa.id,
            "user_id": sa.user_id,
            "name": sa.user_name,
            "email": sa.user_email,
            "phone": sa.user_phone,
            "logo_url": logo_url,  # <-- send full URL to frontend
            "company_id": company.company_id,  # #codex
            "company_name": company.company_name,  # #codex
            "location_id": location.id,  # #codex
            "location_name": _location_label(location),  # #codex
        })


@csrf_exempt
def update_super_admin(request, pk):
    if request.method == "POST":
        sa = get_object_or_404(LoginUsers, pk=pk, user_role_id=SUPER_ADMIN_ROLE_ID)
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        company_id = request.POST.get("company_id")  # #codex
        location_id = request.POST.get("location_id")  # #codex
        logo_file = request.FILES.get("logo")

        logo_url = _build_media_url(sa.image)  # #codex

        if logo_file:
            fs = FileSystemStorage(location=settings.MEDIA_ROOT, base_url=settings.MEDIA_URL)
            logo_name = fs.save(logo_file.name, logo_file)
            logo_url = fs.url(logo_name)
            sa.image = logo_name

        if not name or not email or not phone or not company_id or not location_id:  # #codex
            return JsonResponse({"success": False, "message": "Name, Email, Phone, Company and Location are required"})  # #codex

        if password and password != confirm_password:
            return JsonResponse({"success": False, "message": "Passwords do not match"})

        company = get_object_or_404(CompanyDetails, company_id=company_id, status=1)  # #codex
        location = get_object_or_404(LocationInfos, pk=location_id, status=1)  # #codex

        sa.user_name = name
        sa.user_email = email
        sa.user_phone = phone
        sa.company_id = company.company_id  # #codex
        hashed_password = None  # #codex
        if password:
            hashed_password = make_password(password)  # #codex
            sa.password = hashed_password  # #codex
        sa.save()
        _sync_super_admin_info(sa, company.company_id, location.id, hashed_password)  # #codex

        return JsonResponse({
            "success": True,
            "id": sa.id,
            "user_id": sa.user_id,
            "name": sa.user_name,
            "email": sa.user_email,
            "phone": sa.user_phone,
            "logo_url": logo_url,
            "company_id": company.company_id,  # #codex
            "company_name": company.company_name,  # #codex
            "location_id": location.id,  # #codex
            "location_name": _location_label(location),  # #codex
        })



@csrf_exempt
def delete_super_admin(request, pk):
    if request.method == "POST":
        sa = get_object_or_404(LoginUsers, pk=pk, user_role_id=SUPER_ADMIN_ROLE_ID)
        UserInfos.objects.filter(login_user_id=sa.user_id, user_role=SUPER_ADMIN_ROLE_ID).delete()  # #codex
        sa.delete()
        return JsonResponse({"success": True})
