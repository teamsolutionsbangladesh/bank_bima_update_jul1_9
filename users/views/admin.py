from django.db import connection
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.hashers import make_password
from django.conf import settings
from core.models import LoginUsers, UserInfos   # import path adjust if needed
from core.models import TransactionWiths
from main_heads.models import TransactionMainHeads

# ==============================
# ADMIN CRUD
# ==============================

ADMIN_ROLE_ID = 2   # Roles table অনুযায়ী adjust korba


def _build_media_url(file_name):
    if not file_name:
        return None
    return f"{settings.MEDIA_URL}{file_name}"


def _next_admin_user_id():
    last = LoginUsers.objects.filter(user_role_id=ADMIN_ROLE_ID).order_by('id').last()
    if last and last.user_id and last.user_id.startswith("AD"):
        last_num = int(last.user_id[2:])
        return f"AD{last_num + 1:09d}"
    return "AD000000001"


def admin_list(request):
    admins = LoginUsers.objects.filter(user_role_id=ADMIN_ROLE_ID).order_by('id')
    user_infos = UserInfos.objects.filter(user_role=ADMIN_ROLE_ID)

    user_info_map = {str(u.login_user_id): u for u in user_infos}

    tran_heads = TransactionMainHeads.objects.filter(status=1).order_by('id')
    tran_withs = TransactionWiths.objects.filter(status=1).order_by('id')

    head_map = {h.id: h.type_name for h in tran_heads}
    tran_with_map = {tw.id: tw for tw in tran_withs}

    admin_rows = []
    for admin in admins:
        info = user_info_map.get(str(admin.user_id))
        selected_tw = None
        tran_type_id = None
        tran_type_name = ""
        tran_with_id = None
        tran_with_name = ""

        if info and info.tran_user_type_id:
            selected_tw = tran_with_map.get(info.tran_user_type_id)
            if selected_tw:
                tran_type_id = selected_tw.tran_type
                tran_type_name = head_map.get(selected_tw.tran_type, "")
                tran_with_id = selected_tw.id
                tran_with_name = selected_tw.tran_with_name

        admin_rows.append({
            "id": admin.id,
            "user_id": admin.user_id,
            "name": admin.user_name,
            "email": admin.user_email,
            "phone": admin.user_phone,
            "image": admin.image,
            "logo_url": _build_media_url(admin.image),
            "tran_type_id": tran_type_id,
            "tran_type_name": tran_type_name,
            "tran_with_id": tran_with_id,
            "tran_with_name": tran_with_name,
        })

    return render(request, 'users/admin_list.html', {
        'admins': admin_rows,
        'tran_heads': tran_heads,
    })


def get_transaction_withs_by_type(request):
    tran_type_id = request.GET.get("tran_type_id")
    if not tran_type_id:
        return JsonResponse({"success": False, "items": [], "message": "Tran type required"})

    items = TransactionWiths.objects.filter(
        status=1,
        tran_type=tran_type_id
    ).order_by('id')

    data = [
        {
            "id": item.id,
            "tran_with_name": item.tran_with_name,
            "tran_method": item.tran_method,
        }
        for item in items
    ]

    return JsonResponse({"success": True, "items": data})


@csrf_exempt
def create_admin(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request"})

    # ----------------------------
    # GET DATA
    # ----------------------------
    name = (request.POST.get("name") or "").strip()
    email = (request.POST.get("email") or "").strip()
    phone = (request.POST.get("phone") or "").strip()
    password = request.POST.get("password") or ""
    confirm_password = request.POST.get("confirm_password") or ""

    tran_type_id = request.POST.get("tran_type_id")
    tran_with_id = request.POST.get("tran_with_id")

    logo_file = request.FILES.get("logo")

    # ----------------------------
    # VALIDATION
    # ----------------------------
    if not all([name, email, phone, password, confirm_password, tran_type_id, tran_with_id]):
        return JsonResponse({
            "success": False,
            "message": "All required fields are mandatory"
        })

    if password != confirm_password:
        return JsonResponse({
            "success": False,
            "message": "Passwords do not match"
        })

    # ----------------------------
    # GET TRANSACTION WITH OBJECT
    # ----------------------------
    selected_tw = get_object_or_404(TransactionWiths, pk=tran_with_id, status=1)

    # ✔ IMPORTANT: method comes from DB
    tran_method = selected_tw.tran_method

    # ----------------------------
    # VALIDATE TYPE MATCH
    # ----------------------------
    if str(selected_tw.tran_type) != str(tran_type_id):
        return JsonResponse({
            "success": False,
            "message": "Tran Type mismatch"
        })

    # ----------------------------
    # FILE UPLOAD
    # ----------------------------
    logo_name = None
    logo_url = None

    if logo_file:
        fs = FileSystemStorage(location=settings.MEDIA_ROOT, base_url=settings.MEDIA_URL)
        logo_name = fs.save(logo_file.name, logo_file)
        logo_url = fs.url(logo_name)

    # ----------------------------
    # USER ID
    # ----------------------------
    next_id = _next_admin_user_id()

    # ----------------------------
    # CREATE LOGIN USER
    # ----------------------------
    admin = LoginUsers.objects.create(
        user_id=next_id,
        user_name=name,
        user_email=email,
        user_phone=phone,
        password=make_password(password),
        image=logo_name,
        user_role_id=ADMIN_ROLE_ID,
        status=1
    )

    # ----------------------------
    # INSERT USER INFO
    # ----------------------------
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO user__infos (
                user_id,
                login_user_id,
                title,
                user_name,
                user_email,
                user_phone,
                gender,
                loc_id,
                user_role,
                tran_user_type,
                tran_method,
                tran_with_id,
                status,
                added_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, [
            next_id,
            next_id,
            None,
            name,
            email,
            phone,
            None,
            None,
            ADMIN_ROLE_ID,
            tran_type_id,
            tran_method,   # ✔ from DB, NOT frontend
            tran_with_id,
            1,
            admin.added_at
        ])

    # ----------------------------
    # RESPONSE
    # ----------------------------
    return JsonResponse({
        "success": True,
        "id": admin.id,
        "user_id": admin.user_id,
        "name": admin.user_name,
        "email": admin.user_email,
        "phone": admin.user_phone,
        "logo_url": logo_url,
        "tran_type_id": tran_type_id,
        "tran_with_id": tran_with_id,
        "tran_method": tran_method,
        "tran_with_name": selected_tw.tran_with_name
    })


@csrf_exempt
def update_admin(request, pk):
    if request.method == "POST":
        admin = get_object_or_404(LoginUsers, pk=pk, user_role_id=ADMIN_ROLE_ID)
        user_info = UserInfos.objects.filter(login_user_id=admin.user_id, user_role=ADMIN_ROLE_ID).first()

        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")
        tran_type_id = request.POST.get("tran_type_id")
        tran_with_id = request.POST.get("tran_with_id")
        logo_file = request.FILES.get("logo")

        if not name or not email or not phone or not tran_type_id or not tran_with_id:
            return JsonResponse({"success": False, "message": "Name, Email, Phone, Tran Type and Transaction With are required"})

        if password and password != confirm_password:
            return JsonResponse({"success": False, "message": "Passwords do not match"})

        selected_tw = get_object_or_404(TransactionWiths, pk=tran_with_id, status=1)
        if str(selected_tw.tran_type) != str(tran_type_id):
            return JsonResponse({"success": False, "message": "Selected Transaction With does not match the selected Tran Type"})

        logo_url = _build_media_url(admin.image)

        if logo_file:
            fs = FileSystemStorage(location=settings.MEDIA_ROOT, base_url=settings.MEDIA_URL)
            logo_name = fs.save(logo_file.name, logo_file)
            admin.image = logo_name
            logo_url = fs.url(logo_name)

        admin.user_name = name
        admin.user_email = email
        admin.user_phone = phone
        if password:
            admin.password = make_password(password)
        admin.save()

        if user_info:
            user_info.user_name = name
            user_info.user_email = email
            user_info.user_phone = phone
            user_info.tran_user_type_id = selected_tw.id
            user_info.updated_at = admin.updated_at if hasattr(admin, 'updated_at') else None
            user_info.save()
        else:
            UserInfos.objects.create(
                user_id=admin.user_id,
                login_user_id=admin.user_id,
                user_name=name,
                user_email=email,
                user_phone=phone,
                user_role=ADMIN_ROLE_ID,
                tran_user_type_id=selected_tw.id,
                status=1,
                added_at=admin.added_at if hasattr(admin, 'added_at') and admin.added_at else None
            )

        return JsonResponse({
            "success": True,
            "id": admin.id,
            "user_id": admin.user_id,
            "name": admin.user_name,
            "email": admin.user_email,
            "phone": admin.user_phone,
            "logo_url": logo_url,
            "tran_type_id": selected_tw.tran_type,
            "tran_type_name": TransactionMainHeads.objects.filter(id=selected_tw.tran_type).values_list("type_name", flat=True).first() or "",
            "tran_with_id": selected_tw.id,
            "tran_with_name": selected_tw.tran_with_name,
        })

    return JsonResponse({"success": False, "message": "Invalid request"})


@csrf_exempt
def delete_admin(request, pk):
    if request.method == "POST":
        admin = get_object_or_404(LoginUsers, pk=pk, user_role_id=ADMIN_ROLE_ID)
        UserInfos.objects.filter(login_user_id=admin.user_id, user_role=ADMIN_ROLE_ID).delete()
        admin.delete()
        return JsonResponse({"success": True})

    return JsonResponse({"success": False, "message": "Invalid request"})