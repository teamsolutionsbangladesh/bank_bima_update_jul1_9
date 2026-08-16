from datetime import timezone
from io import BytesIO
import json
from django.http import HttpResponse, JsonResponse
from django.forms import model_to_dict
from django.shortcuts import get_object_or_404, redirect, render
from .models import TransactionDetails, TransactionMains,UserInfos, TransactionWiths, TransactionHeads, Stores, ItemManufacturers, LocationInfos, TransactionMainsTemps, TransactionDetailsTemps, TransactionMainHeads
from django.core.paginator import Paginator
from django.db import connection
from django.db import transaction
from django.db.models import F, Q
from django.db.models import Count, Case, When, IntegerField, Q
from datetime import datetime
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from django.template.loader import get_template
from reportlab.platypus import Table
from django.utils.dateparse import parse_date
from reportlab.platypus import Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from zoneinfo import ZoneInfo

from django.contrib.sessions.models import Session 


LOCAL_TIMEZONE = ZoneInfo("Asia/Dhaka")


def get_local_tran_datetime(date_value=None):
    now = datetime.now(LOCAL_TIMEZONE).replace(tzinfo=None)
    if date_value:
        return datetime.combine(
            datetime.strptime(date_value, "%Y-%m-%d").date(),
            now.time()
        )
    return now

def get_login_location(request):  # #codex
    if not request.session.get("user_id") or not request.session.get("user_name"):  # #codex
        recent_user = get_recent_session_user()  # #codex
        request.session["user_id"] = recent_user.get("user_id", request.session.get("user_id", ""))  # #codex
        request.session["user_name"] = recent_user.get("user_name", request.session.get("user_name", ""))  # #codex
    location_id = request.session.get("loc_id")  # #codex
    location_name = request.session.get("location_name")  # #codex
    if not location_id and request.session.get("user_id"):  # #codex
        user_info = UserInfos.objects.filter(user_id=request.session.get("user_id")).first() or UserInfos.objects.filter(login_user_id=request.session.get("user_id")).first()  # #codex
        location_id = user_info.loc_id if user_info else None  # #codex
    if not location_id and request.session.get("user_name"):  # #codex
        user_info = UserInfos.objects.filter(user_name=request.session.get("user_name"), loc_id__isnull=False).order_by("-id").first()  # #codex
        location_id = user_info.loc_id if user_info else None  # #codex
    location = LocationInfos.objects.filter(id=location_id, status=1).first() if location_id else None  # #codex
    if location:  # #codex
        request.session["loc_id"] = location.id  # #codex
        request.session["location_name"] = location.division  # #codex
        return location.id, location.division  # #codex
    return "", ""  # #codex

def get_recent_session_user():  # #codex
    for session in Session.objects.filter(expire_date__gt=timezone.now()).order_by("-expire_date")[:20]:  # #codex
        data = session.get_decoded()  # #codex
        if data.get("user_id") and data.get("user_name"):  # #codex
            return data  # #codex
    return {}  # #codex

def add_payment_page(request):
    fixed_location_id, fixed_location_name = get_login_location(request)
    return render(request, 'general_transaction/payment.html',{
        "fixed_location_id": fixed_location_id or "",  # #codex
        "fixed_location_name": fixed_location_name or "",  # #codex
    }) 

def dictfetchall(cursor):
    """Return all rows from a cursor as a list of dicts."""
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]




def edit_payment_page(request, id):
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            m.id,
            m.tran_id,
            m.invoice_ref,
            m.loc_id,
            m.store_id,
            m.tran_type,
            m.tran_method,
            m.tran_type_with,
            tw.tran_method AS tran_with_method,
            COALESCE(CAST(ui.id AS CHAR), m.tran_user) AS tran_user, /* codex change */
            COALESCE(ui.user_name, m.user_name) AS user_name,
            loc.division AS location_name, /* codex change */
            m.bill_amount,
            m.discount,
            m.net_amount,
            m.payment,
            m.due,
            m.tran_date
        FROM transaction__mains m
        LEFT JOIN transaction__withs tw ON tw.id = m.tran_type_with
        LEFT JOIN user__infos ui
            ON ui.user_id = m.tran_user
            OR CAST(ui.id AS CHAR) = m.tran_user
        LEFT JOIN location__infos loc ON loc.id = m.loc_id /* codex change */
        WHERE m.id = %s
        LIMIT 1
    """, [id])

    rows = dictfetchall(cursor)
    transaction = rows[0] if rows else None

    if not transaction:
        return redirect('payment_list')

    cursor.execute("""
        SELECT
            d.id,
            d.tran_head_id AS product_id,
            h.tran_head_name AS product_name,
            d.quantity,
            d.cp,
            d.mrp,
            d.amount AS total,
            d.expiry_date,
            COALESCE(d.tran_groupe_id, h.groupe_id) AS tran_groupe_id,
            g.tran_method AS tran_group_method
        FROM transaction__details d
        LEFT JOIN transaction__heads h ON h.id = d.tran_head_id
        LEFT JOIN transaction__groupes g ON g.id = COALESCE(d.tran_groupe_id, h.groupe_id)
        WHERE d.tran_id = %s
        ORDER BY d.id ASC
    """, [transaction["tran_id"]])

    details = dictfetchall(cursor)

    if details:
        transaction["tran_group_id"] = details[0].get("tran_groupe_id")
        transaction["tran_group_method"] = details[0].get("tran_group_method")
    else:
        cursor.execute("""
            SELECT
                p.tran_group_id,
                g.tran_method
            FROM page_init p
            LEFT JOIN transaction__groupes g ON g.id = p.tran_group_id
            WHERE p.tran_main_head_id = %s
            AND p.user_tran_with_id = %s
            ORDER BY p.id ASC
            LIMIT 1
        """, [transaction.get("tran_type"), transaction.get("tran_type_with")])
        page_rows = dictfetchall(cursor)
        page_init = page_rows[0] if page_rows else {}
        transaction["tran_group_id"] = page_init.get("tran_group_id") or ""
        transaction["tran_group_method"] = page_init.get("tran_method") or ""

    transaction["tran_date"] = (
        transaction["tran_date"].strftime("%Y-%m-%d")
        if transaction.get("tran_date") else ""
    )

    for item in details:
        item["expiry_date"] = (
            item["expiry_date"].strftime("%Y-%m-%d")
            if item.get("expiry_date") else ""
        )

    return render(request, 'general_transaction/payment.html', {
        "edit_transaction": transaction,
        "edit_details": details,
        "edit_transaction_json": json.dumps(transaction),
        "edit_details_json": json.dumps(details),
        "edit_mode": True,
        "fixed_location_id": transaction.get("loc_id") or "",  # codex change
        "fixed_location_name": transaction.get("location_name") or "",  # codex change
    })

def payment_list(request):
    # return render(request, 'pharmacy/medicine_list.html')
    today = datetime.now().strftime("%Y-%m-%d")
    per_page_options = [50, 100, 200]

    try:
        per_page = int(request.GET.get("per_page", 50))
    except (TypeError, ValueError):
        per_page = 50

    if per_page not in per_page_options:
        per_page = 50

    return render(request, 'general_transaction/payment_list.html', {
        "search": request.GET.get("search", request.GET.get("q", "")),
        "status_filter": request.GET.get("status", ""),
        "start_date": request.GET.get("start_date") or today,
        "end_date": request.GET.get("end_date") or today,
        "per_page": per_page,
        "per_page_options": per_page_options,
    })

def product_search(request):
    q = request.GET.get('q', '').strip()
    offset = int(request.GET.get('offset', 0))
    tran_main_head_id = (request.GET.get('tran_main_head_id') or '').strip()
    tran_group_id = (request.GET.get('tran_group_id') or '').strip()
    limit = 10

    if not tran_main_head_id or not tran_group_id:
        return JsonResponse({'results': []})

    cursor = connection.cursor()

    if q:
        sql = """
            SELECT 
                t.id,
                t.tran_head_name AS name,
                t.cp,
                m.manufacturer_name AS manufacturer,
                f.form_name AS form,
                c.category_name,
                t.quantity,
                t.mrp
            FROM transaction__heads t
            JOIN transaction__groupes tg ON t.groupe_id = tg.id
            JOIN transaction__main__heads tmh ON tmh.id = tg.tran_groupe_type
            LEFT JOIN item__manufacturers m ON t.manufacturer_id = m.id
            LEFT JOIN item__forms f ON t.form_id = f.id
            LEFT JOIN item__categories c ON t.category_id = c.id
            WHERE t.tran_head_name LIKE %s
            AND tmh.id = %s
            AND tg.id = %s
            ORDER BY t.id ASC
            LIMIT %s OFFSET %s
        """

        params = [f"{q}%", tran_main_head_id, tran_group_id, limit, offset]
    
    else:

        sql = """
            SELECT 
                t.id,
                t.tran_head_name AS name,
                t.cp,
                m.manufacturer_name AS manufacturer,
                f.form_name AS form,
                c.category_name,
                t.quantity,
                t.mrp
            FROM transaction__heads t
            JOIN transaction__groupes tg ON t.groupe_id = tg.id
            JOIN transaction__main__heads tmh ON tmh.id = tg.tran_groupe_type
            LEFT JOIN item__manufacturers m ON t.manufacturer_id = m.id
            LEFT JOIN item__forms f ON t.form_id = f.id
            LEFT JOIN item__categories c ON t.category_id = c.id
            WHERE tmh.id = %s
            AND tg.id = %s
            ORDER BY t.id ASC
            LIMIT %s OFFSET %s
        """

        params = [tran_main_head_id, tran_group_id, limit, offset]


    cursor.execute(sql, params)
    data = dictfetchall(cursor)

    return JsonResponse({'results': data})

# def add_payment_page(request):
#     return render(request, 'general_transaction/payment.html')

# def payment_list(request):
#     # return render(request, 'pharmacy/medicine_list.html')
#     return render(request, 'general_transaction/payment_list.html')

def get_supplier_combo_g(request):

    cursor = connection.cursor()

    sql = """
        SELECT
        m.id AS id,
        m.manufacturer_name
        FROM item__manufacturers m
        ORDER BY m.manufacturer_name;
    """
    params = []

    cursor.execute(sql, params)
    data = dictfetchall(cursor)
    print("DEBUG",data)

    return JsonResponse({
        "supplier_combo": data
    })

def payment_list_load(request):
    q = (request.GET.get('q') or request.GET.get('search') or '').strip()
    status_filter = request.GET.get('status', '').strip()
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    tran_main_head = request.GET.get('tran_main_head') or request.GET.get('transactionmainheads')  # #codex
    tran_with_method = request.GET.get('tran_with_method') or request.GET.get('transaction_with_method')  # #codex
    tran_with = request.GET.get('tran_with') or request.GET.get('transaction_with')  # #codex
    supplier = request.GET.get('supplier') or request.GET.get('transaction_with_user')  # #codex

    try:
        offset = int(request.GET.get('offset', 0))
    except (TypeError, ValueError):
        offset = 0

    try:
        limit = int(request.GET.get('limit') or request.GET.get('per_page') or 50)
    except (TypeError, ValueError):
        limit = 50

    if limit <= 0:
        limit = 50
    limit = min(limit, 200)

    sql = """
        SELECT 
            m.id,
            m.tran_id AS tran_id,
            m.invoice_ref AS invoice_ref,
            DATE_FORMAT(m.tran_date, '%%Y-%%m-%%d') AS tran_date,
            DATE_FORMAT(m.tran_date, '%%H:%%i:%%s') AS tran_time,
            m.tran_type_with AS tran_type_with_id, /* #codex */
            COALESCE(tw.tran_with_name, CAST(m.tran_type_with AS CHAR)) AS tran_type_with, /* #codex */
            m.tran_user AS tran_user_id, /* #codex */
            COALESCE(NULLIF(m.user_name, ''), ui.user_name, m.tran_user) AS tran_user, /* #codex */
            m.bill_amount AS bill_total,
            m.discount AS discount,
            m.net_amount AS net_total,
            m.receive AS advance,
            m.due_col AS due_collection,
            m.due_disc AS due_discount,
            m.due AS due,
            m.status AS status
        FROM transaction__mains m
        LEFT JOIN transaction__withs tw ON tw.id = m.tran_type_with
        LEFT JOIN user__infos ui
            ON ui.user_id = m.tran_user
            OR CAST(ui.id AS CHAR) = m.tran_user
        WHERE 1=1
    """
    total_sql = """
        SELECT COALESCE(SUM(m.due), 0)
        FROM transaction__mains m
        LEFT JOIN user__infos ui
            ON ui.user_id = m.tran_user
            OR CAST(ui.id AS CHAR) = m.tran_user
        WHERE 1=1
    """

    params = []
    total_params = []

    # 🔥 SEARCH (optional)
    if q:
        sql += """
            AND (
                m.tran_id LIKE %s
                OR m.invoice_ref LIKE %s
                OR m.tran_user LIKE %s
                OR m.user_name LIKE %s
                OR ui.user_name LIKE %s
            )
        """
        params.extend([f"%{q}%"] * 5)

        total_sql += """
            AND (
                m.tran_id LIKE %s
                OR m.invoice_ref LIKE %s
                OR m.tran_user LIKE %s
                OR m.user_name LIKE %s
                OR ui.user_name LIKE %s
            )
        """
        total_params.extend([f"%{q}%"] * 5)

    if status_filter in ("0", "1"):
        sql += " AND m.status = %s"
        params.append(status_filter)

        total_sql += " AND m.status = %s"
        total_params.append(status_filter)

    if tran_main_head:
        sql += " AND m.tran_type = %s"
        params.append(tran_main_head)

        total_sql += " AND m.tran_type = %s"
        total_params.append(tran_main_head)

    if tran_with_method:
        sql += """
            AND m.tran_type_with IN (
                SELECT id FROM transaction__withs
                WHERE tran_method = %s
            )
        """
        params.append(tran_with_method)

        total_sql += """
            AND m.tran_type_with IN (
                SELECT id FROM transaction__withs
                WHERE tran_method = %s
            )
        """
        total_params.append(tran_with_method)

    if tran_with:
        sql += " AND m.tran_type_with = %s"
        params.append(tran_with)

        total_sql += " AND m.tran_type_with = %s"
        total_params.append(tran_with)

    if supplier:
        sql += """
            AND (
                m.tran_user = %s
                OR ui.user_id = %s
                OR CAST(ui.id AS CHAR) = %s
            )
        """
        params.extend([supplier, supplier, supplier])

        total_sql += """
            AND (
                m.tran_user = %s
                OR ui.user_id = %s
                OR CAST(ui.id AS CHAR) = %s
            )
        """
        total_params.extend([supplier, supplier, supplier])

    sql += " AND m.tran_id LIKE %s"
    params.append("GPA%")

    total_sql += " AND m.tran_id LIKE %s"
    total_params.append("GPA%")

    # 🔥 DATE FILTER (ALWAYS WORKS)
    if start_date:
        sql += " AND DATE(m.tran_date) >= %s"
        params.append(start_date)

        total_sql += " AND DATE(m.tran_date) >= %s"
        total_params.append(start_date)

    if end_date:
        sql += " AND DATE(m.tran_date) <= %s"
        params.append(end_date)

        total_sql += " AND DATE(m.tran_date) <= %s"
        total_params.append(end_date)

    sql += " ORDER BY m.id ASC LIMIT %s OFFSET %s"
    params.extend([limit, offset])

    cursor = connection.cursor()
    cursor.execute(sql, params)
    data = dictfetchall(cursor)

    cursor.execute(total_sql, total_params)
    total_due = cursor.fetchone()[0] or 0

    return JsonResponse({
        'results': data,
        'total_due': float(total_due)
    })


def payment_report_pdf(request):

    q = (request.GET.get('q') or request.GET.get('search') or '').strip()
    status_filter = request.GET.get('status', '').strip()
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    tran_main_head = request.GET.get('tran_main_head') or request.GET.get('transactionmainheads')
    tran_with_method = request.GET.get('tran_with_method')
    tran_with = request.GET.get('tran_with')
    supplier = request.GET.get('supplier')

    sql = """
        SELECT 
            m.tran_id,
            m.invoice_ref AS invoice_ref,
            m.tran_date,
            COALESCE(tw.tran_with_name, m.tran_type_with) AS tran_type_with,
            COALESCE(ui.user_name, m.user_name, m.tran_user) AS tran_user,
            m.bill_amount,
            m.discount,
            m.net_amount,
            m.receive,
            m.due_col,
            m.due_disc,
            m.due,
            m.status
        FROM transaction__mains m
        LEFT JOIN transaction__withs tw ON tw.id = m.tran_type_with
        LEFT JOIN user__infos ui
            ON ui.user_id = m.tran_user
            OR CAST(ui.id AS CHAR) = m.tran_user
        WHERE 1=1
    """

    params = []

    if q:
        sql += """
            AND (
                m.tran_id LIKE %s
                OR m.invoice_ref LIKE %s
                OR m.tran_user LIKE %s
                OR m.user_name LIKE %s
                OR ui.user_name LIKE %s
            )
        """
        params += [f"%{q}%"] * 5

    if status_filter in ("0", "1"):
        sql += " AND m.status = %s"
        params.append(status_filter)

    if tran_main_head:
        sql += " AND m.tran_type = %s"
        params.append(tran_main_head)

    if tran_with_method:
        sql += """
            AND m.tran_type_with IN (
                SELECT id FROM transaction__withs
                WHERE tran_method = %s
            )
        """
        params.append(tran_with_method)

    if tran_with:
        sql += " AND m.tran_type_with = %s"
        params.append(tran_with)

    if supplier:
        sql += """
            AND (
                m.tran_user = %s
                OR ui.user_id = %s
                OR CAST(ui.id AS CHAR) = %s
            )
        """
        params.extend([supplier, supplier, supplier])

    sql += " AND m.tran_id LIKE %s"
    params.append("GPA%")

    if start_date:
        sql += " AND DATE(m.tran_date) >= %s"
        params.append(start_date)

    if end_date:
        sql += " AND DATE(m.tran_date) <= %s"
        params.append(end_date)

    sql += " ORDER BY m.id ASC"
    

    cursor = connection.cursor()
    cursor.execute(sql, params)
    data = dictfetchall(cursor)

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)

    styles = getSampleStyleSheet()
    title_style = styles["Title"]
    normal_style = styles["Normal"]

    elements = []

    # =========================
    # HEADER
    # =========================
    title = Paragraph("Payment List Report", title_style)
    elements.append(title)
    elements.append(Spacer(1, 10))

    date_text = f"""
    <b>Start Date:</b> {start_date if start_date else '-'}  
    <b>End Date:</b> {end_date if end_date else '-'}
    """

    date_para = Paragraph(date_text, normal_style)
    elements.append(date_para)
    elements.append(Spacer(1, 20))

    # =========================
    # TABLE DATA
    # =========================
    table_data = [
        ["SL","Tran ID","Date","Supplier","Tran User","Bill","Disc","Net","Adv","Due Col","Due Disc","Due"]
    ]

    for i, p in enumerate(data, 1):
        table_data.append([
            i,
            p["tran_id"],
            str(p["tran_date"]),
            p["tran_type_with"],
            p["tran_user"],
            
            p["bill_amount"],
            p["discount"],
            p["net_amount"],
            p["receive"],
            p["due_col"],
            p["due_disc"],
            p["due"]
        ])

    table = Table(table_data)

    table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
    ]))

    elements.append(table)

    # =========================
    # BUILD PDF
    # =========================
    doc.build(elements)

    buffer.seek(0)
    return HttpResponse(buffer, content_type="application/pdf")

def get_divisions_combo(request):

    cursor = connection.cursor()

    sql = """
        SELECT
        MIN(loc.id) AS id,
        loc.division
        FROM location__infos loc
        GROUP BY loc.division
        ORDER BY loc.division;
    """
    params = []

    cursor.execute(sql, params)
    data = dictfetchall(cursor)
    print("DEBUG",data)

    return JsonResponse({
        "divisions_combo": data
    }, safe=False)

# def get_supplier_combo(request):

#     cursor = connection.cursor()

#     sql = """
#         SELECT
#         m.id AS id,
#         m.manufacturer_name
#         FROM item__manufacturers m
#         ORDER BY m.manufacturer_name;
#     """
#     params = []

#     cursor.execute(sql, params)
#     data = dictfetchall(cursor)
#     print("DEBUG",data)

#     return JsonResponse({
#         "supplier_combo": data
#     })

# def get_transaction_with_users_combo(request):

#     data = UserInfos.objects.filter(
#         tran_user_type__tran_type=1,
#         tran_user_type__tran_method='payment'
#     ).values(
#         'id',
#         'user_name',
#         'tran_user_type_id'
#     ).order_by('user_name')

#     return JsonResponse(list(data), safe=False)
def get_transaction_with_combo_p(request):
    data = TransactionWiths.objects.filter(
        tran_type=1,
        tran_method='payment',
        status=1
    ).values('id', 'tran_with_name')

    return JsonResponse(list(data), safe=False)





@csrf_exempt
@transaction.atomic
def save_general_payment(request):

    if request.method != "POST":
        return JsonResponse({"success": False}, status=405)

    try:
        data = json.loads(request.body)

        # ======================
        # SAFE INPUT (FIXED)
        # ======================
        store_id = data.get("store")
        location_id = data.get("location")
        user_info_id = data.get("supplier")   # ✔ FIXED: supplier = user_id
        user_name = data.get("user_name")
        tran_type_with = data.get("tran_type_with")
        tran_group_id = data.get("tran_group_id")
        payment_method = data.get("payment_method")
        edit_id = data.get("edit_id")

        bill_amount = float(data.get("bill_amount") or 0)
        discount = float(data.get("discount") or 0)
        net_amount = float(data.get("net_amount") or 0)
        payment = float(data.get("payment") or 0)
        due = float(data.get("due") or 0)

        products = data.get("products") or []

        # ======================
        # VALIDATION (FIXED)
        # ======================
        if not user_info_id:
            return JsonResponse({"success": False, "message": "User required"}, status=400)  # ✔ FIXED message match frontend

        if not tran_type_with:
            return JsonResponse({"success": False, "message": "Transaction With required"}, status=400)

        # ======================
        # DATE HANDLING
        # ======================
        tran_date = data.get("tran_date")

        tran_date = get_local_tran_datetime(tran_date)

        # ======================
        # TRAN ID GENERATION
        # ======================
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT tran_id
                FROM transaction__mains
                WHERE tran_id LIKE 'GPA%'
                ORDER BY tran_id DESC
                LIMIT 1
            """)
            row = cursor.fetchone()

            last_number = int(row[0][3:]) if row else 0
            tran_id = "GPA" + str(last_number + 1).zfill(9)
            invoice = tran_id

        user_name = ""

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT user_name
                FROM user__infos
                WHERE user_id = %s OR CAST(id AS CHAR) = %s
                LIMIT 1
            """, [user_info_id, user_info_id])

            row = cursor.fetchone()

            if row:
                user_name = row[0]
            else:
                user_name = "UNKNOWN"   # ✔ FIX added for debugging
                print("⚠️ user_id not found in user__infos:", user_info_id)

        print("DEBUG USER_ID:", user_info_id)
        print("DEBUG USER_NAME:", user_name)

        if edit_id:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT tran_id, invoice_ref
                    FROM transaction__mains
                    WHERE id = %s
                    LIMIT 1
                """, [edit_id])
                row = cursor.fetchone()

            if not row:
                return JsonResponse({
                    "success": False,
                    "error": "Transaction not found"
                }, status=404)

            tran_id = row[0]
            invoice = data.get("invoice") or row[1] or tran_id

            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE transaction__mains
                    SET tran_type = %s,
                        tran_method = %s,
                        tran_user = %s,
                        user_name = %s,
                        tran_type_with = %s,
                        store_id = %s,
                        loc_id = %s,
                        tran_date = %s,
                        invoice_ref = %s,
                        bill_amount = %s,
                        discount = %s,
                        net_amount = %s,
                        payment = %s,
                        due = %s
                    WHERE id = %s
                """, [
                    1,
                    payment_method,
                    user_info_id,
                    user_name,
                    tran_type_with,
                    store_id,
                    location_id,
                    tran_date,
                    invoice,
                    bill_amount,
                    discount,
                    net_amount,
                    payment,
                    due,
                    edit_id
                ])

                cursor.execute("""
                    DELETE FROM transaction__details
                    WHERE tran_id = %s
                """, [tran_id])

            details_data = []

            for r in products:

                product_id = r[0] if len(r) > 0 else None
                qty = float(r[1] or 0) if len(r) > 1 else 0
                cp = float(r[2] or 0) if len(r) > 2 else 0
                mrp = float(r[3] or 0) if len(r) > 3 else 0
                expiry = r[4] if len(r) > 4 else None
                total = float(r[5] or 0) if len(r) > 5 else 0

                details_data.append([
                    tran_id,
                    1,
                    payment_method,
                    invoice,
                    location_id,
                    tran_type_with,
                    tran_group_id,

                    product_id,
                    1,
                    qty,
                    0,
                    0,

                    cp,
                    mrp,
                    total,

                    expiry,
                    user_name,
                    store_id,
                    tran_date,
                    1,
                    discount,
                    0,
                    payment,
                    due
                ])

            query = """
                INSERT INTO transaction__details
                (tran_id, tran_type, tran_method, invoice_ref, loc_id,
                tran_type_with, tran_groupe_id, tran_head_id, quantity_actual,
                quantity, quantity_issue, quantity_return, cp, mrp, amount,
                expiry_date, user_name, store_id,
                tran_date, status, discount, receive, payment, due)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """

            with connection.cursor() as cursor:
                cursor.executemany(query, details_data)

            return JsonResponse({
                "success": True,
                "tran_id": tran_id,
                "updated": True
            })

        # ======================
        # MAIN INSERT (FIXED ORDER ISSUE)
        # ======================
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO transaction__mains
                (tran_id, tran_type, tran_method, tran_user, user_name,
                 tran_type_with, store_id, loc_id, tran_date, status,
                 invoice_ref, bill_amount, discount, net_amount, payment, due)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, [
                tran_id,
                1,
                payment_method,
                user_info_id,
                user_name,  # ✔ FIXED (earlier blank issue solved here)
                tran_type_with,
                store_id,
                location_id,
                tran_date,
                1,
                invoice,
                bill_amount,
                discount,
                net_amount,
                payment,
                due
            ])

                # ======================
        # PARTY PAYMENT SNAPSHOT INSERT
        # ======================
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO transaction__party__payments
                (
                    tran_id,
                    tran_type,
                    tran_method,
                    tran_user,
                    user_name,
                    tran_type_with,
                    store_id,
                    loc_id,
                    tran_date,
                    status,
                    invoice_ref,
                    bill_amount,
                    discount,
                    net_amount,
                    payment,
                    due
                )
                VALUES (
                    %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                    %s,%s,%s,%s,%s,%s
                )
            """, [
                tran_id,
                1,
                payment_method,
                user_info_id,
                user_name,
                tran_type_with,
                store_id,
                location_id,
                tran_date,
                1,
                invoice,
                bill_amount,
                discount,
                net_amount,
                payment,
                due
            ])

        # ======================
        # DETAILS BUILD (FIXED INDEX SAFE)
        # ======================
        details_data = []

        for r in products:

            product_id = r[0] if len(r) > 0 else None
            qty = float(r[1] or 0) if len(r) > 1 else 0
            cp = float(r[2] or 0) if len(r) > 2 else 0
            mrp = float(r[3] or 0) if len(r) > 3 else 0
            expiry = r[4] if len(r) > 4 else None
            total = float(r[5] or 0) if len(r) > 5 else 0

            details_data.append([
                tran_id,
                1,
                payment_method,
                invoice,
                location_id,
                tran_type_with,
                tran_group_id,

                product_id,
                1,
                qty,
                0,
                0,

                cp,        # ✔ cp only once
                mrp,       # ✔ mrp only once
                total,

                expiry,
                user_name,
                store_id,
                tran_date,
                1,
                discount,
                0,
                payment,
                due
            ])

        # ======================
        # DETAILS INSERT (FIXED COLUMN COUNT ISSUE)
        # ======================
        query = """
            INSERT INTO transaction__details
            (tran_id, tran_type, tran_method, invoice_ref, loc_id,
            tran_type_with, tran_groupe_id, tran_head_id, quantity_actual,
            quantity, quantity_issue, quantity_return, cp, mrp, amount,
            expiry_date, user_name, store_id,
            tran_date, status, discount, receive, payment, due)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """

        # ✔ FIXED: column mismatch + formatting error resolved
        with connection.cursor() as cursor:
            cursor.executemany(query, details_data)

        return JsonResponse({
            "success": True,
            "tran_id": tran_id
        })

    except Exception as e:
        print("🔥 ERROR:", e)
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)
    


def add_receive_page(request):
    return render(request, 'general_transaction/receive.html')
def receive_list(request):
    # return render(request, 'pharmacy/medicine_list.html')
    return render(request, 'general_transaction/receive_list.html')

def receive_list_load(request):
    q = request.GET.get('q', '').strip()
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    offset = int(request.GET.get('offset', 0))
    limit = 50

    sql = """
        SELECT 
            m.id,
            m.tran_id AS tran_id,
            m.tran_date AS tran_date,
            COALESCE(tw.tran_with_name, m.tran_type_with) AS tran_type_with,
            COALESCE(ui.user_name, m.user_name, m.tran_user) AS tran_user,
            m.bill_amount AS bill_total,
            m.discount AS discount,
            m.net_amount AS net_total,
            m.receive AS advance,
            m.due_col AS due_collection,
            m.due_disc AS due_discount,
            m.due AS due
        FROM transaction__mains m
        LEFT JOIN transaction__withs tw ON tw.id = m.tran_type_with
        LEFT JOIN user__infos ui
            ON ui.user_id = m.tran_user
            OR CAST(ui.id AS CHAR) = m.tran_user
        WHERE 1=1
    """

    params = []

    # 🔥 SEARCH (optional)
    if q:
        sql += """
            AND (
                m.tran_id LIKE %s
                OR m.invoice_ref LIKE %s
                OR m.tran_user LIKE %s
                OR m.user_name LIKE %s
                OR ui.user_name LIKE %s
            )
        """
        params.extend([f"%{q}%"] * 5)
    sql += " AND m.tran_id LIKE %s"
    params.append("GRE%")

    # 🔥 DATE FILTER (ALWAYS WORKS)
    if start_date:
        sql += " AND DATE(m.tran_date) >= %s"
        params.append(start_date)

    if end_date:
        sql += " AND DATE(m.tran_date) <= %s"
        params.append(end_date)

    sql += " ORDER BY m.id ASC LIMIT %s OFFSET %s"
    params.extend([limit, offset])

    cursor = connection.cursor()
    cursor.execute(sql, params)
    data = dictfetchall(cursor)

    return JsonResponse({'results': data})



def receive_report_pdf(request):

    q = request.GET.get('q', '')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    sql = """
        SELECT 
            m.tran_id,
            m.tran_date,
            COALESCE(tw.tran_with_name, m.tran_type_with) AS tran_type_with,
            COALESCE(ui.user_name, m.user_name, m.tran_user) AS tran_user,
            m.bill_amount,
            m.discount,
            m.net_amount,
            m.receive,
            m.due_col,
            m.due_disc,
            m.due
        FROM transaction__mains m
        LEFT JOIN transaction__withs tw ON tw.id = m.tran_type_with
        LEFT JOIN user__infos ui
            ON ui.user_id = m.tran_user
            OR CAST(ui.id AS CHAR) = m.tran_user
        WHERE 1=1
    """

    params = []

    if q:
        sql += """
            AND (
                m.tran_id LIKE %s
                OR m.invoice_ref LIKE %s
                OR m.tran_user LIKE %s
                OR m.user_name LIKE %s
                OR ui.user_name LIKE %s
            )
        """
        params += [f"%{q}%"] * 5
    sql += " AND m.tran_id LIKE %s"
    params.append("GRE%")

    if start_date:
        sql += " AND DATE(m.tran_date) >= %s"
        params.append(start_date)

    if end_date:
        sql += " AND DATE(m.tran_date) <= %s"
        params.append(end_date)

    sql += " ORDER BY m.id ASC"
    

    cursor = connection.cursor()
    cursor.execute(sql, params)
    data = dictfetchall(cursor)

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)

    styles = getSampleStyleSheet()
    title_style = styles["Title"]
    normal_style = styles["Normal"]

    elements = []

    # =========================
    # HEADER
    # =========================
    title = Paragraph("Receive List Report", title_style)
    elements.append(title)
    elements.append(Spacer(1, 10))

    date_text = f"""
    <b>Start Date:</b> {start_date if start_date else '-'}  
    <b>End Date:</b> {end_date if end_date else '-'}
    """

    date_para = Paragraph(date_text, normal_style)
    elements.append(date_para)
    elements.append(Spacer(1, 20))

    # =========================
    # TABLE DATA
    # =========================
    table_data = [
        ["SL","Tran ID","Date","Supplier","Tran User","Bill","Disc","Net","Adv","Due Col","Due Disc","Due"]
    ]

    for i, p in enumerate(data, 1):
        table_data.append([
            i,
            p["tran_id"],
            str(p["tran_date"]),
            p["tran_type_with"],
            p["tran_user"],
            
            p["bill_amount"],
            p["discount"],
            p["net_amount"],
            p["receive"],
            p["due_col"],
            p["due_disc"],
            p["due"]
        ])

    table = Table(table_data)

    table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
    ]))

    elements.append(table)

    # =========================
    # BUILD PDF
    # =========================
    doc.build(elements)

    buffer.seek(0)
    return HttpResponse(buffer, content_type="application/pdf")

@csrf_exempt
@transaction.atomic
def save_general_receive(request):

    if request.method != "POST":
        return JsonResponse({"success": False}, status=405)

    try:
        data = json.loads(request.body)

        # ---- Form Data ----
        store_id = data.get("store")
        location_id = data.get("location")
        user_info_id = data.get("supplier")
        tran_type_with = data.get("tran_type_with")

        if not tran_type_with:
            return JsonResponse({"success": False, "message": "Transaction With required"}, status=400)

        invoice = data.get("invoice")
        payment_method = data.get("payment_method")
        tran_method = payment_method
        bill_amount = data.get("bill_amount") or 0
        discount = data.get("discount") or 0
        net_amount = data.get("net_amount") or 0
        receive = data.get("receive") or 0   # always 0 from frontend
        payment =  0
        due = data.get("due") or 0

        tran_date = data.get("tran_date")

        tran_date = get_local_tran_datetime(tran_date)

        products = data.get("products", [])

        # ---- Generate ID ----
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT tran_id 
                FROM transaction__mains
                WHERE tran_id LIKE 'GRE%'
                ORDER BY tran_id DESC
                LIMIT 1
            """)
            row = cursor.fetchone()

            last_number = int(row[0][3:]) if row else 0
            tran_id = "GRE" + str(last_number + 1).zfill(9)

        tran_type = 1   # ✅ GENERAL
        status = 1

        # ---- MAIN TABLE ----
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO transaction__mains
                (tran_id, tran_type, tran_method, tran_user, tran_type_with,
                 store_id, loc_id, tran_date, status, invoice_ref,
                 bill_amount, discount, net_amount, payment, due)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, [
                tran_id, tran_type, tran_method, user_info_id, tran_type_with,
                store_id, location_id, tran_date, status, invoice,
                bill_amount, discount, net_amount, payment, due
            ])

        # ---- DETAILS ----
        details_data = []

        for row in products:
            details_data.append([
                tran_id,
                tran_type,
                tran_method,
                invoice,
                location_id,
                tran_type_with,
                row[0],   # product id
                1,   # qty
                row[1],
                0,
                0,
                0,
                row[2],   # amount
                row[5],   # total
                0,   # cp
                0,   # mrp
                row[4],   # expiry
                store_id,
                tran_date,
                status,
                discount,
                receive,
                0,
                due
            ])

        query = """
            INSERT INTO transaction__details
            (tran_id, tran_type, tran_method, invoice_ref, loc_id, tran_type_with,
             tran_head_id, quantity_actual, quantity, quantity_issue, quantity_return,
             unit_id, amount, tot_amount, cp, mrp, expiry_date, store_id,
             tran_date, status, discount, receive, payment, due)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """

        with connection.cursor() as cursor:
            cursor.executemany(query, details_data)  

        return JsonResponse({"success": True, "tran_id": tran_id})

    except Exception as e:
        print("🔥 GENERAL PAYMENT ERROR:", e)
        return JsonResponse({"success": False, "error": str(e)}, status=500)
    
# def get_transaction_with_users_combo_p(request):

#         data = UserInfos.objects.filter(
#             tran_user_type__tran_type=1,
#             tran_user_type__tran_method='receive'
#         ).values(
#             'id',
#             'user_name',
#             'tran_user_type_id'
#         ).order_by('user_name')

#         return JsonResponse(list(data), safe=False)



def get_transaction_with_combo_r(request):
    data = TransactionWiths.objects.filter(
        tran_type=1,
        tran_method='receive',
        status=1
    ).values('id', 'tran_with_name')

    return JsonResponse(list(data), safe=False)

def get_supplier_by_tran_with_g(request):
    tran_with_id = request.GET.get('tran_with_id')

    if not tran_with_id:
        return JsonResponse([], safe=False)

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                user_id AS id,
                user_name
            FROM user__infos
            WHERE status = 1
            AND (
                tran_user_type = %s
                OR tran_with_id = %s
            )
            ORDER BY user_name
        """, [tran_with_id, tran_with_id])
        data = dictfetchall(cursor)

    print("tran_with_id:", tran_with_id, type(tran_with_id))
    return JsonResponse(data, safe=False)


# office bazar



def payment_list_ob(request):
    # return render(request, 'pharmacy/medicine_list.html')
    return render(request, 'general_transaction/office_bazar/payment_list.html')

def payment_list_load_ob(request):
    q = request.GET.get('q', '').strip()
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    offset = int(request.GET.get('offset', 0))
    limit = 50

    sql = """
        SELECT 
            m.id,
            m.tran_id AS tran_id,
            m.tran_date AS tran_date,
            COALESCE(tw.tran_with_name, m.tran_type_with) AS tran_type_with,
            COALESCE(ui.user_name, m.user_name, m.tran_user) AS tran_user,
            m.bill_amount AS bill_total,
            m.discount AS discount,
            m.net_amount AS net_total,
            m.receive AS advance,
            m.due_col AS due_collection,
            m.due_disc AS due_discount,
            m.due AS due
        FROM transaction__mains m
        LEFT JOIN transaction__withs tw ON tw.id = m.tran_type_with
        LEFT JOIN user__infos ui
            ON ui.user_id = m.tran_user
            OR CAST(ui.id AS CHAR) = m.tran_user
        WHERE 1=1
    """

    params = []

    # 🔥 SEARCH (optional)
    if q:
        sql += """
            AND (
                m.tran_id LIKE %s
                OR m.invoice_ref LIKE %s
                OR m.tran_user LIKE %s
                OR m.user_name LIKE %s
                OR ui.user_name LIKE %s
            )
        """
        params.extend([f"%{q}%"] * 5)
    sql += " AND m.tran_id LIKE %s"
    params.append("OBZ%")

    # 🔥 DATE FILTER (ALWAYS WORKS)
    if start_date:
        sql += " AND DATE(m.tran_date) >= %s"
        params.append(start_date)

    if end_date:
        sql += " AND DATE(m.tran_date) <= %s"
        params.append(end_date)

    sql += " ORDER BY m.id ASC LIMIT %s OFFSET %s"
    params.extend([limit, offset])

    cursor = connection.cursor()
    cursor.execute(sql, params)
    data = dictfetchall(cursor)

    return JsonResponse({'results': data})

def get_transaction_with_combo_ob(request):
    data = TransactionWiths.objects.filter(
        tran_type=1,
        tran_method='payment',
        status=1
    ).values('id', 'tran_with_name')

    return JsonResponse(list(data), safe=False)

def get_supplier_by_tran_with_ob(request):
    tran_with_id = request.GET.get('tran_with_id')

    if not tran_with_id:
        return JsonResponse([], safe=False)

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                user_id AS id,
                user_name
            FROM user__infos
            WHERE status = 1
            AND (
                tran_user_type = %s
                OR tran_with_id = %s
            )
            ORDER BY user_name
        """, [tran_with_id, tran_with_id])
        data = dictfetchall(cursor)

    print("tran_with_id:", tran_with_id, type(tran_with_id))
    return JsonResponse(data, safe=False)

@csrf_exempt
@transaction.atomic
def save_general_payment_ob(request):

    if request.method != "POST":
        return JsonResponse({"success": False}, status=405)

    try:
        data = json.loads(request.body)

        # ---- Form Data ----
        store_id = data.get("store")
        location_id = data.get("location")
        user_id = data.get("supplier")
        tran_type_with = data.get("tran_type_with")

        if not tran_type_with:
            return JsonResponse({"success": False, "message": "Transaction With required"}, status=400)

        invoice = data.get("invoice")
        payment_method = data.get("payment_method")

        bill_amount = data.get("bill_amount") or 0
        discount = data.get("discount") or 0
        net_amount = data.get("net_amount") or 0
        receive = 0   # always 0 from frontend
        payment = data.get("payment") or 0 
        due = data.get("due") or 0

        tran_date = data.get("tran_date")

        tran_date = get_local_tran_datetime(tran_date)

        products = data.get("products", [])

        # ---- Generate ID ----
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT tran_id 
                FROM transaction__mains
                WHERE tran_id LIKE 'OBZ%'
                ORDER BY tran_id DESC
                LIMIT 1
            """)
            row = cursor.fetchone()

            last_number = int(row[0][3:]) if row else 0
            tran_id = "OBZ" + str(last_number + 1).zfill(9)

        tran_type = 1   # ✅ GENERAL
        status = 1

        # ---- MAIN TABLE ----
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO transaction__mains
                (tran_id, tran_type, tran_method, tran_user, tran_type_with,
                 store_id, loc_id, tran_date, status, invoice_ref,
                 bill_amount, discount, net_amount, payment, due)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, [
                tran_id, tran_type, payment_method, user_id, tran_type_with,
                store_id, location_id, tran_date, status, invoice,
                bill_amount, discount, net_amount, payment, due
            ])

        # ---- DETAILS ----
        details_data = []

        for row in products:
            details_data.append([
                tran_id,
                tran_type,
                payment_method,
                invoice,
                location_id,
                tran_type_with,
                row[0],   # product id
                1,   # qty
                row[1],
                0,
                0,
                0,
                row[2],   # amount
                row[5],   # total
                0,   # cp
                0,   # mrp
                row[4],   # expiry
                store_id,
                tran_date,
                status,
                discount,
                0,
                payment,
                due
            ])

        query = """
            INSERT INTO transaction__details
            (tran_id, tran_type, tran_method, invoice_ref, loc_id, tran_type_with,
             tran_head_id, quantity_actual, quantity, quantity_issue, quantity_return,
             unit_id, amount, tot_amount, cp, mrp, expiry_date, store_id,
             tran_date, status, discount, receive, payment, due)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """

        with connection.cursor() as cursor:
            cursor.executemany(query, details_data)

        return JsonResponse({"success": True, "tran_id": tran_id})

    except Exception as e:
        print("🔥 GENERAL PAYMENT ERROR:", e)
        return JsonResponse({"success": False, "error": str(e)}, status=500)





def get_page_init_add_payment(request):
    
    page_id = request.GET.get('page_id')

    print("DEBUG======>>>>>>>>>>>>", page_id)

    cursor = connection.cursor()

    sql = """
        SELECT
            s.tran_main_head_id AS tran_main_head_id,
            s.user_tran_method AS user_tran_method,
            s.user_tran_with_id AS user_tran_with_id,

            CASE
                WHEN s.tran_method = 0 THEN 'Receive'
                WHEN s.tran_method = 1 THEN 'Payment'
                ELSE s.tran_method
            END AS tran_method,

            s.tran_group_id AS tran_group_id

        FROM page_init s
        WHERE s.page_id = %s
    """

    params = [page_id]

    cursor.execute(sql, params)

    data = [
        {
            "tran_main_head_id": row[0],
            "user_tran_method": row[1],
            "user_tran_with_id": row[2],
            "tran_method": row[3],
            "tran_group_id": row[4]
        }
        for row in cursor.fetchall()
    ]

    return JsonResponse({
        "get_page_init_data": data
    })


def party_payment_list(request):
    return render(request,'general_transaction/party_payment/payment_list.html')

def party_payment_list_load(request):

    q = request.GET.get('q', '').strip()
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    tran_main_head = request.GET.get('tran_main_head')
    tran_with = request.GET.get('tran_with')
    supplier = request.GET.get('supplier')

    offset = int(request.GET.get('offset', 0))
    limit = 50

    sql = """
        SELECT 
            m.id,
            m.tran_id AS tran_id,
            m.invoice_ref AS invoice_ref,
            m.tran_date AS tran_date,
            m.tran_type_with AS supplier_name,

            m.user_name AS user_name,

            m.bill_amount AS bill_total,
            m.discount AS discount,
            m.net_amount AS net_total,
            m.payment AS advance,
            m.due_col AS due_collection,
            m.due_disc AS due_discount,
            m.due AS due
        FROM transaction__mains m
        WHERE 1=1
    """
    total_sql = """
        SELECT COALESCE(SUM(m.due), 0)
        FROM transaction__mains m
        WHERE 1=1
    """

    params = []
    total_params = []

    # 🔍 optional search
    if q:
        sql += """
            AND (
                m.tran_id LIKE %s
                OR m.tran_user LIKE %s
            )
        """
        params.append(f"%{q}%")
        params.append(f"%{q}%")

        total_sql += """
            AND (
                m.tran_id LIKE %s
                OR m.tran_user LIKE %s
            )
        """
        total_params.append(f"%{q}%")
        total_params.append(f"%{q}%")

    # 🔥 filters (core logic for party payment)

    
    if tran_main_head:
        sql += " AND m.tran_main_head_id = %s"
        params.append(tran_main_head)

        total_sql += " AND m.tran_main_head_id = %s"
        total_params.append(tran_main_head)

    if tran_with:
        sql += " AND m.tran_type_with = %s"
        params.append(tran_with)
        total_sql += " AND m.tran_type_with = %s"
        total_params.append(tran_with)

    # USER FILTER (transaction_with_user)
    if supplier:
        sql += " AND m.tran_user = %s"
        params.append(supplier)

        total_sql += " AND m.tran_user = %s"
        total_params.append(supplier)

    # OB prefix (if needed like your OBZ)
    sql += " AND m.tran_id LIKE %s"
    params.append("GPA%")

    total_sql += " AND m.tran_id LIKE %s"
    total_params.append("GPA%")

    # sql += " AND m.due > 0"

    # date filters
    if start_date:
        sql += " AND DATE(m.tran_date) >= %s"
        params.append(start_date)
        total_sql += " AND DATE(m.tran_date) >= %s"
        total_params.append(start_date)

    if end_date:
        sql += " AND DATE(m.tran_date) <= %s"
        params.append(end_date)
        total_sql += " AND DATE(m.tran_date) <= %s"
        total_params.append(end_date)

    sql += " ORDER BY m.id ASC LIMIT %s OFFSET %s"
    params.extend([limit, offset])

    cursor = connection.cursor()

    # list data
    cursor.execute(sql, params)
    data = dictfetchall(cursor)

    # total due
    cursor.execute(total_sql, total_params)
    total_due = cursor.fetchone()[0] or 0

    return JsonResponse({
        'results': data,
        'total_due': float(total_due)
    })

def get_tran_main_heads(request):

    heads = TransactionMainHeads.objects.filter(
        status=1
    ).order_by("type_name")

    data = []

    for h in heads:
        data.append({
            "id": h.id,
            "name": h.type_name   # 🔥 IMPORTANT MATCH JS EXPECTATION
        })

    return JsonResponse({
        "transaction_main_heads_combo": data
    })

def get_tran_withs(request):

    main_head_id = request.GET.get('main_head_id')

    sql = """
        SELECT 
            id,
            tran_with_name,
            tran_type,
            tran_method
        FROM transaction__withs
        WHERE status = 1
    """

    params = []

    if main_head_id:
        sql += " AND tran_type = %s"
        params.append(main_head_id)

    sql += " ORDER BY tran_with_name ASC"

    cursor = connection.cursor()
    cursor.execute(sql, params)
    rows = dictfetchall(cursor)

    return JsonResponse({'results': rows})

def get_tran_users(request):

    with_id = request.GET.get('with_id')

    sql = """
        SELECT 
            id,
            user_id,
            user_name,
            user_email,
            user_phone
        FROM user__infos
        WHERE status = 1
    """

    params = []

    if with_id:
        sql += " AND tran_user_type = %s"
        params.append(with_id)

    sql += " ORDER BY user_name ASC"

    cursor = connection.cursor()
    cursor.execute(sql, params)
    rows = dictfetchall(cursor)

    return JsonResponse({'results': rows})

def party_payment_details(request, id):

    sql = """
        SELECT
            id,
            tran_id,
            invoice_ref,
            tran_date,
            tran_type_with,
            tran_user,
            bill_amount,
            discount,
            net_amount,
            payment,
            receive,
            due_col,
            due_disc,
            due
        FROM transaction__mains
        WHERE id = %s
    """

    cursor = connection.cursor()
    cursor.execute(sql, [id])

    row = dictfetchall(cursor)

    return JsonResponse(row)

def party_payment_form(request, id):

    sql = """
        SELECT
            id,
            tran_id,
            invoice_ref,
            tran_date,
            tran_type_with,
            tran_user,
            bill_amount,
            discount,
            net_amount,
            payment,
            receive,
            due_col,
            due_disc,
            due
        FROM transaction__mains
        WHERE id = %s
        LIMIT 1
    """

    cursor = connection.cursor()
    cursor.execute(sql, [id])

    row = dictfetchall(cursor)

    transaction = row[0] if row else None

    return render(
        request,
        'general_transaction/party_payment/payment_form.html',
        {
            'transaction': transaction
        }
    )


@csrf_exempt
@transaction.atomic
def process_party_payment(request, id):

    if request.method != "POST":
        return JsonResponse({
            "success": False,
            "error": "Invalid request method"
        }, status=405)

    try:
        pay_amount = float(request.POST.get("pay_amount", 0))
        due_discount = float(request.POST.get("due_discount", 0))

    except:
        return JsonResponse({
            "success": False,
            "error": "Invalid amount"
        }, status=400)

    # ================= VALIDATION =================
    if pay_amount <= 0:
        return JsonResponse({
            "success": False,
            "error": "Payment must be greater than 0"
        }, status=400)

    cursor = connection.cursor()

    # ================= FETCH MAIN =================
    cursor.execute("""
        SELECT 
            tran_id,
            invoice_ref,
            tran_type,
            tran_method,
            tran_user,
            user_name,
            tran_type_with,
            store_id,
            loc_id,
            tran_date,
            status,
            bill_amount,
            discount,
            net_amount,
            payment,
            due,
            due_col,
            due_disc

        FROM transaction__mains
        WHERE id = %s
    """, [id])

    row = cursor.fetchone()

    if not row:
        return JsonResponse({
            "success": False,
            "error": "Transaction not found"
        }, status=404)

    (
        old_tran_id,
        invoice_ref,
        tran_type,
        tran_method,
        tran_user,
        user_name,
        tran_type_with,
        store_id,
        loc_id,
        tran_date,
        status,
        bill_amount,
        discount,
        net_amount,
        old_payment,
        current_due,
        old_due_col,
        old_due_disc
    ) = row

    current_due = float(current_due or 0)
    old_payment = float(old_payment or 0)
    old_due_col = float(old_due_col or 0)
    old_due_disc = float(old_due_disc or 0)

    # ================= VALIDATION =================
    if (pay_amount + due_discount) > current_due:
        return JsonResponse({
            "success": False,
            "error": "Payment + Discount exceeds due"
        }, status=400)

    # ================= CALCULATION =================
    new_due = current_due - pay_amount - due_discount

    new_due_col = old_due_col + pay_amount

    new_due_disc = old_due_disc + due_discount

    # ================= UPDATE MAIN ONLY =================
    cursor.execute("""
        UPDATE transaction__mains
        SET
            due = %s,
            due_col = %s,
            due_disc = %s
        WHERE id = %s
    """, [
        new_due,
        new_due_col,
        new_due_disc,
        id
    ])

    # ================= INSERT PARTY PAYMENT HISTORY =================
    cursor.execute("""
        INSERT INTO transaction__party__payments
        (
            tran_id,
            invoice_ref,
            tran_type,
            tran_method,
            tran_user,
            user_name,
            tran_type_with,
            store_id,
            loc_id,
            tran_date,
            status,
            bill_amount,
            discount,
            net_amount,
            payment,
            due,
            due_col,
            due_disc
        )
        VALUES (
            %s,%s,%s,%s,%s,%s,%s,%s,%s,
            %s,%s,%s,%s,%s,%s,%s,%s,%s
        )
    """, [
        old_tran_id,     # same tran_id
        old_tran_id,     # same invoice_ref

        tran_type,
        tran_method,
        tran_user,
        user_name,
        tran_type_with,
        store_id,
        loc_id,
        tran_date,
        status,
        bill_amount,
        discount,
        net_amount,

        pay_amount,
        new_due,
        pay_amount,
        due_discount
    ])

    return JsonResponse({
        "success": True,
        "paid": pay_amount,
        "due_discount": due_discount,
        "new_due": new_due,
        "new_due_col": new_due_col,
        "new_due_disc": new_due_disc,
        "redirect_url": "/general/party-payment/"
    })

def party_payment_report_pdf(request):

    q = request.GET.get('q', '')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    main_head = request.GET.get("main_head")
    tran_with = request.GET.get("tran_with")
    supplier = request.GET.get("supplier")

    sql = """
        SELECT 
            m.tran_id,
            m.invoice_ref,
            m.tran_date,

            mh.type_name AS main_head,
            tw.tran_with_name AS tran_with,

            m.tran_user,
            m.user_name,

            m.bill_amount,
            m.discount,
            m.net_amount,
            m.payment,
            m.due_col,
            m.due_disc,
            m.due

        FROM transaction__mains m

        LEFT JOIN transaction__main__heads mh 
            ON mh.id = m.tran_type

        LEFT JOIN transaction__withs tw 
            ON tw.id = m.tran_type_with

        WHERE 1=1
    """

    params = []

    # GPA FILTER
    sql += " AND m.tran_id LIKE %s"
    params.append("GPA%")

    print(sql)
    print(params)

    # SEARCH
    if q:
        sql += """
            AND (
                m.tran_id LIKE %s
                OR m.tran_user LIKE %s
                OR m.user_name LIKE %s
            )
        """

        params += [
            f"%{q}%",
            f"%{q}%",
            f"%{q}%"
        ]

    # DATE FILTER
    if start_date:
        sql += " AND DATE(m.tran_date) >= %s"
        params.append(start_date)

    if end_date:
        sql += " AND DATE(m.tran_date) <= %s"
        params.append(end_date)

    # MAIN HEAD
    if main_head:
        sql += " AND m.tran_type = %s"
        params.append(main_head)

    # TRANSACTION WITH
    if tran_with:
        sql += " AND m.tran_type_with = %s"
        params.append(tran_with)
    

    # TRANSACTION USER FILTER
    # DEFAULT
    supplier_text = "All"

    # ONLY FILTER WHEN USER IS SELECTED
    if supplier and supplier != "":

        cursor = connection.cursor()

        cursor.execute(
            "SELECT user_name FROM user__infos WHERE id = %s",
            [supplier]
        )

        supplier_row = cursor.fetchone()

        if supplier_row:

            supplier_text = supplier_row[0]

            sql += " AND m.user_name = %s"
            params.append(supplier_text)

    sql += " ORDER BY m.id ASC"

    cursor = connection.cursor()

    cursor.execute(sql, params)

    data = dictfetchall(cursor)

    # ================= TOTAL =================
    total_due = sum(float(r["due"] or 0) for r in data)

    # ================= PDF SETUP =================
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=30,
        rightMargin=30,
        topMargin=30,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()

    title_style = styles["Title"]
    normal_style = styles["Normal"]

    elements = []

    # ================= TITLE =================
    elements.append(Paragraph("Party Payment Report", title_style))
    elements.append(Spacer(1, 10))


    main_head_text = "All"
    tran_with_text = "All"

    # MAIN HEAD NAME
    if main_head and main_head != "null":

        cursor.execute(
            "SELECT type_name FROM transaction__main__heads WHERE id = %s",
            [main_head]
        )

        row = cursor.fetchone()

        if row:
            main_head_text = row[0]

    # TRANSACTION WITH NAME
    if tran_with and tran_with != "null":

        cursor.execute(
            "SELECT tran_with_name FROM transaction__withs WHERE id = %s",
            [tran_with]
        )

        row = cursor.fetchone()

        if row:
            tran_with_text = row[0]

    # ================= HEADER INFO =================
    header_text = f"""
    <b>Start Date:</b> {start_date or '-'} &nbsp;&nbsp;&nbsp;
    <b>End Date:</b> {end_date or '-'}<br/><br/>

    <b>Main Head:</b> {main_head_text} &nbsp;&nbsp;&nbsp;
    <b>Transaction With:</b> {tran_with_text}<br/><br/>

    <b>Transaction User:</b> {supplier_text}
    """

    elements.append(Paragraph(header_text, normal_style))
    elements.append(Spacer(1, 15))

    # ================= TABLE =================
    table_data = [[
        "SL",
        "Tran ID",
        "Invoice Ref",
        "Date",
        "Supplier",
        "Tran User",
        "Bill",
        "Discount",
        "Net",
        "Advance",
        "Due Col",
        "Due Disc",
        "Due"
    ]]

    for i, p in enumerate(data, 1):

        table_data.append([
            i,
            p["tran_id"],
            p["invoice_ref"],
            p["tran_date"].strftime("%Y-%m-%d") if p["tran_date"] else "",
            p["tran_with"],
            p["user_name"],
            p["bill_amount"],
            p["discount"],
            p["net_amount"],
            p["payment"],
            p["due_col"],
            p["due_disc"],
            p["due"]
        ])

    table = Table(table_data, colWidths=[
        25,
        55,
        55,
        55,
        70,
        50,
        40,
        40,
        40,
        40,
        40,
        40,
        40
    ])

    table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTSIZE', (0,0), (-1,-1), 7),
    ]))

    elements.append(table)

    # ================= TOTAL =================
    elements.append(Spacer(1, 12))

    elements.append(Paragraph(
        f"<b>Total Due:</b> {total_due:.2f}",
        normal_style
    ))

    doc.build(elements)

    buffer.seek(0)

    return HttpResponse(
        buffer,
        content_type="application/pdf"
    )

@csrf_exempt
@transaction.atomic
def process_fifo_payment(request):

    payment_amount = float(request.POST.get("payment", 0))
    ids = json.loads(request.POST.get("ids", "[]"))

    if payment_amount <= 0 or not ids:
        return JsonResponse({"success": False})

    remaining = payment_amount
    updated_rows = []

    with connection.cursor() as cursor:

        placeholders = ",".join(["%s"] * len(ids))

        # ================= GET MAIN =================
        cursor.execute(f"""
            SELECT id, invoice_ref, bill_amount, payment, due
            FROM transaction__mains
            WHERE id IN ({placeholders})
            ORDER BY tran_date ASC, id ASC
        """, ids)

        rows = cursor.fetchall()

        for row in rows:

            row_id, invoice_ref, bill_amount, old_payment, due = row

            bill_amount = float(bill_amount or 0)
            old_payment = float(old_payment or 0)
            due = float(due or 0)

            if remaining <= 0:
                break

            if due <= 0:
                continue

            pay = min(remaining, due)

            new_payment = old_payment + pay
            new_due = bill_amount - new_payment

            # ================= UPDATE MAIN =================
            cursor.execute("""
                UPDATE transaction__mains
                SET payment = %s,
                    due = %s
                WHERE id = %s
            """, [new_payment, new_due, row_id])

            # ================= UPDATE DETAILS =================
            cursor.execute("""
                UPDATE transaction__details
                SET payment = payment + %s,
                    due = due - %s
                WHERE invoice_ref = %s
            """, [pay, pay, invoice_ref])

            updated_rows.append(row_id)
            remaining -= pay

    return JsonResponse({
        "success": True,
        "paid": payment_amount - remaining,
        "updated_rows": updated_rows
    })


# report

def transaction_summary_page(request):
    return render(request, "general_transaction/reports/transaction_summary/transaction_summary_list.html")

def transaction_summary_list(request):

    q = request.GET.get('q', '').strip()
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    tran_with = request.GET.get('tran_with')

    offset = int(request.GET.get('offset', 0))
    limit = 50

    # =========================
    # DEFAULT DATE (LIKE PARTY PAYMENT STYLE)
    # =========================
    if not start_date:
        start_date = date.today().strftime("%Y-%m-%d")

    if not end_date:
        end_date = date.today().strftime("%Y-%m-%d")

    sql = """
        SELECT
            m.id,
            m.tran_id,
            m.invoice_ref,
            m.tran_date,
            tw.tran_with_name AS tran_type_with,
            m.tran_user,
            m.bill_amount,
            m.discount,
            m.net_amount,
            m.payment,
            m.due_col,
            m.due_disc,
            m.due
        FROM transaction__mains m
        LEFT JOIN transaction__withs tw
            ON tw.id = m.tran_type_with
        WHERE 1=1
    """

    params = []

    # =========================
    # FIXED: General A/C always (tran_type = 1)
    # =========================
    sql += " AND m.tran_type = %s "
    params.append(1)

    # =========================
    # SEARCH
    # =========================
    if q:
        sql += """
            AND (
                m.tran_id LIKE %s
                OR m.tran_user LIKE %s
            )
        """
        params.extend([f"%{q}%", f"%{q}%"])

    # =========================
    # TRANSACTION WITH FILTER
    # =========================
    if tran_with:
        sql += " AND m.tran_type_with = %s "
        params.append(tran_with)

    # =========================
    # DATE FILTER (IMPORTANT - SAME STYLE AS PARTY PAYMENT)
    # =========================
    sql += " AND DATE(m.tran_date) >= %s "
    params.append(start_date)

    sql += " AND DATE(m.tran_date) <= %s "
    params.append(end_date)

    # =========================
    # ORDER + LIMIT
    # =========================
    sql += " ORDER BY m.id ASC LIMIT %s OFFSET %s "
    params.extend([limit, offset])

    cursor = connection.cursor()
    cursor.execute(sql, params)
    data = dictfetchall(cursor)

    return JsonResponse({
        "results": data
    })
