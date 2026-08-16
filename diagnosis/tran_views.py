from datetime import timezone
from io import BytesIO
import json
import traceback
from django.http import HttpResponse, JsonResponse
from django.forms import model_to_dict
from django.shortcuts import get_object_or_404, redirect, render
from core.models import TransactionDetails, TransactionMains,UserInfos, TransactionWiths, TransactionHeads, Stores, ItemManufacturers, LocationInfos, TransactionMainsTemps, TransactionDetailsTemps, TransactionMainHeads
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
from django.contrib.sessions.models import Session  # #codex


def dictfetchall(cursor):
    """Return all rows from a cursor as a list of dicts."""
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

def get_recent_session_user():  # #codex
    for session in Session.objects.filter(expire_date__gt=timezone.now()).order_by("-expire_date")[:20]:  # #codex
        data = session.get_decoded()  # #codex
        if data.get("user_id") and data.get("user_name"):  # #codex
            return data  # #codex
    return {}  # #codex

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

def add_diagnosis_payment_page(request):
    fixed_location_id, fixed_location_name = get_login_location(request)  # #codex
    return render(request, 'diagnosis/transaction.html', {  # #codex
        "fixed_location_id": fixed_location_id or "",  # #codex
        "fixed_location_name": fixed_location_name or "",  # #codex
    })  # #codex

def edit_diagnosis_payment_page(request, id):  # codex change
    cursor = connection.cursor()  # codex change
    cursor.execute("""  # codex change
        SELECT  # codex change
            m.id, m.tran_id, m.invoice_ref, m.loc_id, m.store_id,  # codex change
            m.tran_type, m.tran_method, m.tran_type_with,  # codex change
            tw.tran_method AS tran_with_method,  # codex change
            m.tran_user, COALESCE(m.user_name, m.tran_user, '') AS user_name,  # codex change
            loc.division AS location_name,  # codex change
            m.bill_amount, m.discount, m.net_amount, m.payment, m.due, m.tran_date,  # codex change
            m.doctor_id, COALESCE(doc.name, '') AS doctor_name,  # codex change
            COALESCE(doc.specialization, '') AS doctor_speciality, COALESCE(doc.chamber, '') AS doctor_chamber,  # codex change
            m.sr_id, COALESCE(sr.name, '') AS sr_name,  # codex change
            m.patient_id, COALESCE(patient_user.title, '') AS patient_title, COALESCE(p.patient_name, m.user_name, '') AS patient_name,  # codex change
            COALESCE(p.age_y, 0) AS patient_age_y, COALESCE(p.age_m, 0) AS patient_age_m, COALESCE(p.age_d, 0) AS patient_age_d,  # codex change
            COALESCE(p.gender, '') AS patient_gender, COALESCE(p.present_mobile, '') AS patient_phone, COALESCE(p.present_address, '') AS patient_address  # codex change
        FROM transaction__mains m  # codex change
        LEFT JOIN transaction__withs tw ON tw.id = m.tran_type_with  # codex change
        LEFT JOIN location__infos loc ON loc.id = m.loc_id  # codex change
        LEFT JOIN doctors_info doc ON doc.custom_doc_id COLLATE utf8mb4_unicode_ci = m.doctor_id COLLATE utf8mb4_unicode_ci  # codex change
        LEFT JOIN item__sr_agents sr ON sr.custom_sr_id COLLATE utf8mb4_unicode_ci = m.sr_id COLLATE utf8mb4_unicode_ci  # codex change
        LEFT JOIN patient_info p ON p.user_info_id COLLATE utf8mb4_unicode_ci = m.patient_id COLLATE utf8mb4_unicode_ci  # codex change
        LEFT JOIN user__infos patient_user ON patient_user.user_id COLLATE utf8mb4_unicode_ci = m.patient_id COLLATE utf8mb4_unicode_ci  # codex change
        WHERE m.id = %s AND m.tran_type = 10  # codex change
        LIMIT 1  # codex change
    """, [id])  # codex change
    rows = dictfetchall(cursor)  # codex change
    transaction = rows[0] if rows else None  # codex change
    if not transaction:  # codex change
        return redirect('diag_payment_list')  # codex change
    cursor.execute("""  # codex change
        SELECT  # codex change
            d.id, d.tran_head_id AS product_id, h.tran_head_name AS product_name,  # codex change
            d.quantity, d.cp, d.mrp, d.tot_amount AS total, d.expiry_date,  # codex change
            COALESCE(d.tran_groupe_id, h.groupe_id) AS tran_groupe_id, g.tran_method AS tran_group_method  # codex change
        FROM transaction__details d  # codex change
        LEFT JOIN transaction__heads h ON h.id = d.tran_head_id  # codex change
        LEFT JOIN transaction__groupes g ON g.id = COALESCE(d.tran_groupe_id, h.groupe_id)  # codex change
        WHERE d.tran_id = %s  # codex change
        ORDER BY d.id ASC  # codex change
    """, [transaction["tran_id"]])  # codex change
    details = dictfetchall(cursor)  # codex change
    transaction["tran_group_id"] = details[0].get("tran_groupe_id") if details else ""  # codex change
    transaction["tran_group_method"] = details[0].get("tran_group_method") if details else ""  # codex change
    transaction["tran_date"] = transaction["tran_date"].strftime("%Y-%m-%d") if transaction.get("tran_date") else ""  # codex change
    for item in details:  # codex change
        item["expiry_date"] = item["expiry_date"].strftime("%Y-%m-%d") if item.get("expiry_date") else ""  # codex change
    return render(request, 'diagnosis/transaction.html', {  # codex change
        "edit_transaction": transaction,  # codex change
        "edit_details": details,  # codex change
        "edit_transaction_json": json.dumps(transaction, default=str),  # codex change
        "edit_details_json": json.dumps(details, default=str),  # codex change
        "edit_mode": True,  # codex change
        "fixed_location_id": transaction.get("loc_id") or "",  # codex change
        "fixed_location_name": transaction.get("location_name") or "",  # codex change
    })  # codex change



def diag_payment_list(request):
    # return render(request, 'pharmacy/medicine_list.html')
    return render(request, 'diagnosis/transaction_list.html')

def insert_diagnosis_detail_rows(products, tran_id, tran_type, payment_method, invoice_ref, location_id, tran_type_with, user_id, tran_by, store_id, tran_date, status, discount, receive, payment, due, doctor_custom_id, patient_id, sr_id):  # codex change
    details_data = []  # codex change
    for row in products:  # codex change
        product_id = row[0]  # codex change
        qty = row[1] or 0  # codex change
        cp = row[2] or 0  # codex change
        mrp = row[3] or 0  # codex change
        expiry = row[4] or None  # codex change
        total = row[5] or 0  # codex change
        details_data.append([  # codex change
            tran_id, tran_type, payment_method, invoice_ref, location_id, tran_type_with, user_id, tran_by,  # codex change
            product_id, 1, qty, 0, 0,  # codex change
            0, cp, total, cp, mrp, expiry,  # codex change
            store_id, tran_date, status,  # codex change
            discount, receive, payment, due,  # codex change
            doctor_custom_id, patient_id, sr_id  # codex change
        ])  # codex change
    details_query = """  # codex change
        INSERT INTO transaction__details  # codex change
        (  # codex change
            tran_id, tran_type, tran_method, invoice_ref,  # codex change
            loc_id, tran_type_with, tran_user, tran_by,  # codex change
            tran_head_id, quantity_actual, quantity,  # codex change
            quantity_issue, quantity_return,  # codex change
            unit_id, amount, tot_amount, cp, mrp, expiry_date,  # codex change
            store_id, tran_date, status,  # codex change
            discount, receive, payment, due,  # codex change
            doctor_id, patient_id, sr_id  # codex change
        )  # codex change
        VALUES  # codex change
        (  # codex change
            %s, %s, %s, %s,  # codex change
            %s, %s, %s, %s,  # codex change
            %s, %s, %s,  # codex change
            %s, %s,  # codex change
            %s, %s, %s, %s, %s, %s,  # codex change
            %s, %s, %s,  # codex change
            %s, %s, %s, %s,  # codex change
            %s, %s, %s  # codex change
        )  # codex change
    """  # codex change
    if details_data:  # codex change
        with connection.cursor() as cursor:  # codex change
            cursor.executemany(details_query, details_data)  # codex change

def product_search(request):
    q = request.GET.get('q', '').strip()
    offset = int(request.GET.get('offset', 0))
    tran_main_head_id = request.GET.get('tran_main_head_id').strip()
    tran_group_id = request.GET.get('tran_group_id')
    limit = 10

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
            m.tran_type_with AS tran_type_with,
            m.tran_user AS tran_user,
            m.bill_amount AS bill_total,
            m.discount AS discount,
            m.net_amount AS net_total,
            m.receive AS advance,
            m.due_col AS due_collection,
            m.due_disc AS due_discount,
            m.due AS due
        FROM transaction__mains m
        WHERE 1=1
    """

    params = []

    # 🔥 SEARCH (optional)
    if q:
        sql += " AND (m.tran_id LIKE %s OR m.tran_user LIKE %s)"
        params.append(f"%{q}%")
        params.append(f"%{q}%")
    sql += " AND m.tran_id LIKE %s"
    params.append("GPA%")

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


def payment_report_pdf(request):

    q = request.GET.get('q', '')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    sql = """
        SELECT 
            m.tran_id,
            m.tran_date,
            m.tran_type_with,
            m.tran_user,
            m.bill_amount,
            m.discount,
            m.net_amount,
            m.receive,
            m.due_col,
            m.due_disc,
            m.due
        FROM transaction__mains m
        WHERE 1=1
    """

    params = []

    if q:
        sql += " AND (m.tran_id LIKE %s OR m.tran_user LIKE %s)"
        params += [f"%{q}%", f"%{q}%"]
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
        tran_type=10,
        tran_method='receive',
        status=1
    ).values('id', 'tran_with_name')

    return JsonResponse(list(data), safe=False)




# @csrf_exempt
# @transaction.atomic
# def save_general_payment(request):

#     if request.method != "POST":
#         return JsonResponse({"success": False}, status=405)

#     try:
#         data = json.loads(request.body)

#         # ---- Form Data ----
#         store_id = data.get("store")
#         location_id = data.get("location")
#         user_id = data.get("supplier")
#         tran_type_with = data.get("tran_type_with")

#         if not tran_type_with:
#             return JsonResponse({"success": False, "message": "Transaction With required"}, status=400)

#         invoice = data.get("invoice")
#         payment_method = data.get("payment_method")

#         bill_amount = data.get("bill_amount") or 0
#         discount = data.get("discount") or 0
#         net_amount = data.get("net_amount") or 0
#         receive = 0   # always 0 from frontend
#         payment = data.get("payment") or 0 
#         due = data.get("due") or 0

#         tran_date = data.get("tran_date")

#         if tran_date:
#             tran_date = datetime.combine(
#                 datetime.strptime(tran_date, "%Y-%m-%d").date(),
#                 timezone.localtime().time()
#             )
#         else:
#             tran_date = timezone.localtime()

#         products = data.get("products", [])

#         # ---- Generate ID ----
#         with connection.cursor() as cursor:
#             cursor.execute("""
#                 SELECT tran_id 
#                 FROM transaction__mains
#                 WHERE tran_id LIKE 'GPA%'
#                 ORDER BY tran_id DESC
#                 LIMIT 1
#             """)
#             row = cursor.fetchone()

#             last_number = int(row[0][3:]) if row else 0
#             tran_id = "GPA" + str(last_number + 1).zfill(9)

#         tran_type = 1   # ✅ GENERAL
#         status = 1

#         # ---- MAIN TABLE ----
#         with connection.cursor() as cursor:
#             cursor.execute("""
#                 INSERT INTO transaction__mains
#                 (tran_id, tran_type, tran_method, tran_user, tran_type_with,
#                  store_id, loc_id, tran_date, status, invoice,
#                  bill_amount, discount, net_amount, payment, due)
#                 VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
#             """, [
#                 tran_id, tran_type, payment_method, user_id, tran_type_with,
#                 store_id, location_id, tran_date, status, invoice,
#                 bill_amount, discount, net_amount, payment, due
#             ])

#         # ---- DETAILS ----
#         details_data = []

#         for row in products:
#             details_data.append([
#                 tran_id,
#                 tran_type,
#                 payment_method,
#                 invoice,
#                 location_id,
#                 tran_type_with,
#                 row[0],   # product id
#                 1,   # qty
#                 row[1],
#                 0,
#                 0,
#                 0,
#                 row[2],   # amount
#                 row[5],   # total
#                 0,   # cp
#                 0,   # mrp
#                 row[4],   # expiry
#                 store_id,
#                 tran_date,
#                 status,
#                 discount,
#                 0,
#                 payment,
#                 due
#             ])

#         query = """
#             INSERT INTO transaction__details
#             (tran_id, tran_type, tran_method, invoice, loc_id, tran_type_with,
#              tran_head_id, quantity_actual, quantity, quantity_issue, quantity_return,
#              unit_id, amount, tot_amount, cp, mrp, expiry_date, store_id,
#              tran_date, status, discount, receive, payment, due)
#             VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
#         """

#         with connection.cursor() as cursor:
#             cursor.executemany(query, details_data)

#         return JsonResponse({"success": True, "tran_id": tran_id})

#     except Exception as e:
#         print("🔥 GENERAL PAYMENT ERROR:", e)
#         return JsonResponse({"success": False, "error": str(e)}, status=500)
    

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
            m.tran_type_with AS tran_type_with,
            m.tran_user AS tran_user,
            m.bill_amount AS bill_total,
            m.discount AS discount,
            m.net_amount AS net_total,
            m.receive AS advance,
            m.due_col AS due_collection,
            m.due_disc AS due_discount,
            m.due AS due
        FROM transaction__mains m
        WHERE 1=1
    """

    params = []

    # 🔥 SEARCH (optional)
    if q:
        sql += " AND (m.tran_id LIKE %s OR m.tran_user LIKE %s)"
        params.append(f"%{q}%")
        params.append(f"%{q}%")
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
            m.tran_type_with,
            m.tran_user,
            m.bill_amount,
            m.discount,
            m.net_amount,
            m.receive,
            m.due_col,
            m.due_disc,
            m.due
        FROM transaction__mains m
        WHERE 1=1
    """

    params = []

    if q:
        sql += " AND (m.tran_id LIKE %s OR m.tran_user LIKE %s)"
        params += [f"%{q}%", f"%{q}%"]
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
        user_id = data.get("supplier")
        tran_type_with = data.get("tran_type_with")

        if not tran_type_with:
            return JsonResponse({"success": False, "message": "Transaction With required"}, status=400)

        invoice_ref = data.get("invoice_ref")
        payment_method = data.get("payment_method")
        tran_method = payment_method
        bill_amount = data.get("bill_amount") or 0
        discount = data.get("discount") or 0
        net_amount = data.get("net_amount") or 0
        receive = data.get("receive") or 0   # always 0 from frontend
        payment =  0
        due = data.get("due") or 0

        tran_date = data.get("tran_date")

        if tran_date:
            tran_date = datetime.combine(
                datetime.strptime(tran_date, "%Y-%m-%d").date(),
                timezone.localtime().time()
            )
        else:
            tran_date = timezone.localtime()

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
                tran_id, tran_type, tran_method, user_id, tran_type_with,
                store_id, location_id, tran_date, status, invoice_ref,
                bill_amount, discount, net_amount, payment, due
            ])

        # ---- DETAILS ----
        details_data = []

        for row in products:
            details_data.append([
                tran_id,
                tran_type,
                tran_method,
                invoice_ref,
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

    data = list(UserInfos.objects.filter(
        tran_user_type_id=int(tran_with_id),   # 🔥 FIX HERE
        tran_user_type__tran_type=1
    ).values('id', 'user_name'))
    print("tran_with_id:", tran_with_id, type(tran_with_id))
    return JsonResponse(data, safe=False)


# office bazar

def add_payment_page_ob(request):
    return render(request, 'general_transaction/office_bazar/payment.html')

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
            m.tran_type_with AS tran_type_with,
            m.tran_user AS tran_user,
            m.bill_amount AS bill_total,
            m.discount AS discount,
            m.net_amount AS net_total,
            m.receive AS advance,
            m.due_col AS due_collection,
            m.due_disc AS due_discount,
            m.due AS due
        FROM transaction__mains m
        WHERE 1=1
    """

    params = []

    # 🔥 SEARCH (optional)
    if q:
        sql += " AND (m.tran_id LIKE %s OR m.tran_user LIKE %s)"
        params.append(f"%{q}%")
        params.append(f"%{q}%")
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

    data = list(UserInfos.objects.filter(
        tran_user_type_id=int(tran_with_id),   # 🔥 FIX HERE
        tran_user_type__tran_type=1
    ).values('id', 'user_name'))
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

        invoice_ref = data.get("invoice_ref")
        payment_method = data.get("payment_method")

        bill_amount = data.get("bill_amount") or 0
        discount = data.get("discount") or 0
        net_amount = data.get("net_amount") or 0
        receive = 0   # always 0 from frontend
        payment = data.get("payment") or 0 
        due = data.get("due") or 0

        tran_date = data.get("tran_date")

        if tran_date:
            tran_date = datetime.combine(
                datetime.strptime(tran_date, "%Y-%m-%d").date(),
                timezone.localtime().time()
            )
        else:
            tran_date = timezone.localtime()

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
                store_id, location_id, tran_date, status, invoice_ref,
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
            (tran_id, tran_type, tran_method, invoice, loc_id, tran_type_with,
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

    print("DEBUG======>>>>>>>>>>>>",page_id)

    cursor = connection.cursor()

    sql = """
        SELECT
        s.tran_main_head_id AS tran_main_head_id,
        s.user_tran_method AS user_tran_method,
        s.user_tran_with_id AS user_tran_with_id,
        s.tran_method AS tran_method,
        s.tran_group_id AS tran_group_id
        FROM page_init s
        WHERE s.page_id = %s

    """
    params = [page_id]

    cursor.execute(sql, params)
    # data = dictfetchall(cursor)

    data  = [
        {
            "tran_main_head_id": row[0],
            "user_tran_method": row[1],
            "user_tran_with_id": row[2],
            "tran_method": row[3],
            "tran_group_id": row[4]
        }
        for row in cursor.fetchall()
    ]    
    print("DEBUG-------<><><><><><><><>",data)

    return JsonResponse({
        "get_page_init_data": data
    })    

    # diagnosis


@csrf_exempt
@transaction.atomic
def save_diagnosis_payment(request):

    if request.method != "POST":
        return JsonResponse({
            "success": False,
            "message": "Invalid request method"
        }, status=405)

    try:
        data = json.loads(request.body)

        # TRANSACTION BY
        # logged-in user je transaction create korbe
        # =========================
        tran_by = None

        # 1) Django auth user
        if request.user.is_authenticated:
            tran_by = request.user.username or str(request.user.id)

        # 2) Custom session login fallback
        if not tran_by:
            tran_by = (
                request.session.get("username")
                or request.session.get("user_name")
                or request.session.get("name")
                or request.session.get("user_id")
                or request.session.get("id")
            )

        # 3) Final fallback
        if tran_by:
            tran_by = str(tran_by)
        else:
            tran_by = "Unknown"

        # =========================
        # FORM DATA
        # =========================
        store_id = data.get("store")
        location_id, _location_name = get_login_location(request)  # #codex
        location_id = location_id or data.get("location")  # #codex
        if not location_id:  # #codex
            return JsonResponse({"success": False, "message": "Login user location not found"}, status=400)  # #codex
        user_id = data.get("supplier")
        user_name = data.get("user_name")

        tran_type_with = data.get("tran_type_with")
        if not tran_type_with:
            return JsonResponse({
                "success": False,
                "message": "Transaction With required"
            }, status=400)

        invoice_ref = data.get("invoice_ref")
        edit_id = data.get("edit_id")  # codex change
        payment_method = data.get("payment_method") or "cash"

        bill_amount = data.get("bill_amount") or 0
        discount = data.get("discount") or 0
        net_amount = data.get("net_amount") or 0

        receive = data.get("receive") or 0
        payment = data.get("payment") or 0
        due = data.get("due") or 0

        products = data.get("products", [])

        if not products:
            return JsonResponse({
                "success": False,
                "message": "No products selected"
            }, status=400)

        # =========================
        # DATE
        # =========================
        tran_date = data.get("tran_date")

        if tran_date:
            tran_date = datetime.combine(
                datetime.strptime(tran_date, "%Y-%m-%d").date(),
                timezone.localtime().time()
            )
        else:
            tran_date = timezone.localtime()

        # =========================
        # DOCTOR CUSTOM DOC ID
        # frontend theke numeric doctor id ashleo
        # transaction table e custom_doc_id save hobe
        # =========================
        referred_doctor_id = data.get("referred_doctor_id")
        doctor_custom_id = None

        if referred_doctor_id:
            referred_doctor_id = str(referred_doctor_id).strip()

            with connection.cursor() as cursor:
                if referred_doctor_id.isdigit():
                    cursor.execute("""
                        SELECT custom_doc_id
                        FROM doctors_info
                        WHERE id = %s
                        LIMIT 1
                    """, [int(referred_doctor_id)])
                else:
                    cursor.execute("""
                        SELECT custom_doc_id
                        FROM doctors_info
                        WHERE custom_doc_id = %s
                        LIMIT 1
                    """, [referred_doctor_id])

                doc_row = cursor.fetchone()

            if doc_row and doc_row[0]:
                doctor_custom_id = doc_row[0]

        if not doctor_custom_id:
            return JsonResponse({
                "success": False,
                "message": "Doctor ID not found. Please select a valid doctor."
            }, status=400)

        print("REFERRED DOCTOR ID:", referred_doctor_id)
        print("DOCTOR CUSTOM ID:", doctor_custom_id)

        # =========================
        # PATIENT ENTRY
        # 1) user__infos e common data
        # 2) patient_info e patient data
        # 3) user__infos.user_id save hobe mains/details patient_id te
        # =========================
        patient_title = (data.get("patient_title") or "").strip()
        patient_name = (data.get("patient_name") or "").strip()

        patient_age_y = data.get("patient_age_y") or 0
        patient_age_m = data.get("patient_age_m") or 0
        patient_age_d = data.get("patient_age_d") or 0

        try:
            patient_age_y = int(patient_age_y)
        except Exception:
            patient_age_y = 0

        try:
            patient_age_m = int(patient_age_m)
        except Exception:
            patient_age_m = 0

        try:
            patient_age_d = int(patient_age_d)
        except Exception:
            patient_age_d = 0

        patient_gender = (data.get("patient_gender") or "").strip()
        patient_phone = (data.get("patient_phone") or "").strip()
        patient_address = (data.get("patient_address") or "").strip()

        if not patient_name:
            return JsonResponse({
                "success": False,
                "message": "Patient name required"
            }, status=400)

        patient_id = None
        patient_row = None
        incoming_patient_id = (data.get("patient_id") or "").strip() if data.get("patient_id") else ""  # codex change

        # user_role column bigint, tai patient role er actual numeric id dite hobe
        PATIENT_ROLE_ID = 2

        with connection.cursor() as cursor:

            # 1) Phone diye existing patient user__infos check
            if edit_id and incoming_patient_id:  # codex change
                patient_id = incoming_patient_id  # codex change
            elif patient_phone:
                cursor.execute("""
                    SELECT user_id
                    FROM user__infos
                    WHERE user_phone = %s
                    LIMIT 1
                """, [patient_phone])

                patient_row = cursor.fetchone()

            if patient_id:  # codex change
                pass  # codex change
            elif patient_row and patient_row[0]:
                patient_id = patient_row[0]

            else:
                # 2) New user__infos.user_id generate
                cursor.execute("""
                    SELECT user_id
                    FROM user__infos
                    WHERE user_id LIKE 'PAT%%'
                    ORDER BY user_id DESC
                    LIMIT 1
                """)

                last_patient = cursor.fetchone()

                if last_patient and last_patient[0]:
                    last_number = int(last_patient[0][3:])
                else:
                    last_number = 0

                patient_id = "PAT" + str(last_number + 1).zfill(9)

                # 3) Insert common patient data into user__infos
                cursor.execute("""
                    INSERT INTO user__infos
                    (
                        user_id,
                        title,
                        user_name,
                        user_phone,
                        gender,
                        loc_id,
                        user_role,
                        tran_method,
                        tran_with_id,
                        address,
                        store_id,
                        status,
                        added_at,
                        updated_at
                    )
                    VALUES
                    (
                        %s, %s, %s, %s,
                        %s, %s, %s, %s,
                        %s, %s, %s, %s,
                        NOW(), NOW()
                    )
                """, [
                    patient_id,
                    patient_title,
                    patient_name,
                    patient_phone,
                    patient_gender,
                    location_id,
                    PATIENT_ROLE_ID,
                    payment_method,
                    tran_type_with,
                    patient_address,
                    store_id,
                    1
                ])

            # 4) patient_info table e oi patient already ache kina check
            cursor.execute("""
                SELECT id
                FROM patient_info
                WHERE user_info_id = %s
                LIMIT 1
            """, [patient_id])

            diagnosis_patient_row = cursor.fetchone()

            if not diagnosis_patient_row:
                # 5) Insert patient-specific data into patient_info
                cursor.execute("""
                    INSERT INTO patient_info
                    (
                        patient_name,
                        age_y,
                        age_m,
                        age_d,
                        gender,
                        present_mobile,
                        present_address,
                        user_info_id,
                        created_at,
                        updated_at
                    )
                    VALUES
                    (
                        %s, %s, %s, %s,
                        %s, %s, %s, %s,
                        NOW(), NOW()
                    )
                """, [
                    patient_name,
                    patient_age_y,
                    patient_age_m,
                    patient_age_d,
                    patient_gender,
                    patient_phone,
                    patient_address,
                    patient_id
                ])

        print("PATIENT USER_INFO ID:", patient_id)

        if not patient_id:
            return JsonResponse({
                "success": False,
                "message": "Patient ID could not be generated."
            }, status=400)

        with connection.cursor() as cursor:  # codex change
            cursor.execute("""  # codex change
                UPDATE user__infos  # codex change
                SET title = %s, user_name = %s, user_phone = %s, gender = %s, loc_id = %s, tran_method = %s, tran_with_id = %s, address = %s, store_id = %s, updated_at = NOW()  # codex change
                WHERE user_id = %s  # codex change
            """, [patient_title, patient_name, patient_phone, patient_gender, location_id, payment_method, tran_type_with, patient_address, store_id, patient_id])  # codex change
            cursor.execute("""  # codex change
                UPDATE patient_info  # codex change
                SET patient_name = %s, age_y = %s, age_m = %s, age_d = %s, gender = %s, present_mobile = %s, present_address = %s, updated_at = NOW()  # codex change
                WHERE user_info_id = %s  # codex change
            """, [patient_name, patient_age_y, patient_age_m, patient_age_d, patient_gender, patient_phone, patient_address, patient_id])  # codex change

        # =========================
        # SR CUSTOM ID
        # item__sr_agents.custom_sr_id save hobe transaction table e
        # =========================
        referred_sr_id = data.get("referred_sr_id")
        sr_id = None
        sr_row = None

        if referred_sr_id:
            referred_sr_id = str(referred_sr_id).strip()

            with connection.cursor() as cursor:
                if referred_sr_id.isdigit():
                    cursor.execute("""
                        SELECT custom_sr_id
                        FROM item__sr_agents
                        WHERE id = %s
                        LIMIT 1
                    """, [int(referred_sr_id)])
                else:
                    cursor.execute("""
                        SELECT custom_sr_id
                        FROM item__sr_agents
                        WHERE custom_sr_id = %s
                        LIMIT 1
                    """, [referred_sr_id])

                sr_row = cursor.fetchone()

            if sr_row and sr_row[0]:
                sr_id = sr_row[0]

        print("REFERRED SR ID:", referred_sr_id)
        print("SR ROW:", sr_row)
        print("FINAL SR ID:", sr_id)

        tran_type = 10  # codex change
        status = 1  # codex change

        if edit_id:  # codex change
            with connection.cursor() as cursor:  # codex change
                cursor.execute("""  # codex change
                    SELECT tran_id, COALESCE(invoice_ref, tran_id)  # codex change
                    FROM transaction__mains  # codex change
                    WHERE id = %s AND tran_type = 10  # codex change
                    LIMIT 1  # codex change
                """, [edit_id])  # codex change
                edit_row = cursor.fetchone()  # codex change
                if not edit_row:  # codex change
                    return JsonResponse({"success": False, "message": "Diagnosis transaction not found"}, status=404)  # codex change
                tran_id = edit_row[0]  # codex change
                invoice_ref = edit_row[1] or tran_id  # codex change
                cursor.execute("""  # codex change
                    UPDATE transaction__mains  # codex change
                    SET tran_method = %s, invoice_ref = %s, loc_id = %s, tran_type_with = %s, tran_user = %s, tran_by = %s, user_name = %s,  # codex change
                        store_id = %s, tran_date = %s, status = %s, bill_amount = %s, discount = %s, net_amount = %s, receive = %s, payment = %s, due = %s,  # codex change
                        doctor_id = %s, patient_id = %s, sr_id = %s, updated_at = NOW()  # codex change
                    WHERE id = %s  # codex change
                """, [payment_method, invoice_ref, location_id, tran_type_with, user_id, tran_by, user_name, store_id, tran_date, status, bill_amount, discount, net_amount, receive, payment, due, doctor_custom_id, patient_id, sr_id, edit_id])  # codex change
                cursor.execute("DELETE FROM transaction__details WHERE tran_id = %s", [tran_id])  # codex change
            insert_diagnosis_detail_rows(products, tran_id, tran_type, payment_method, invoice_ref, location_id, tran_type_with, user_id, tran_by, store_id, tran_date, status, discount, receive, payment, due, doctor_custom_id, patient_id, sr_id)  # codex change
            return JsonResponse({  # codex change
                "success": True,  # codex change
                "updated": True,  # codex change
                "tran_id": tran_id,  # codex change
                "doctor_id": doctor_custom_id,  # codex change
                "patient_id": patient_id,  # codex change
                "sr_id": sr_id,  # codex change
                "tran_by": tran_by  # codex change
            })  # codex change

        # =========================
        # GENERATE TRANSACTION ID
        # Diagnosis Payment prefix: DPA
        # =========================
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT tran_id
                FROM transaction__mains
                WHERE tran_id LIKE 'DPA%%'
                ORDER BY tran_id DESC
                LIMIT 1
            """)

            row = cursor.fetchone()

        last_number = int(row[0][3:]) if row else 0
        tran_id = "DPA" + str(last_number + 1).zfill(9)
        invoice_ref = tran_id  # codex change

        # =========================
        # INSERT MAIN TABLE
        # tran_by tran_user er pore save hobe
        # =========================
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO transaction__mains
                (
                    tran_id, tran_type, tran_method, invoice_ref,
                    loc_id, tran_type_with, tran_user, tran_by, user_name,
                    store_id, tran_date, status,
                    bill_amount, discount, net_amount,
                    receive, payment, due,
                    doctor_id, patient_id, sr_id
                )
                VALUES
                (
                    %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s
                )
            """, [
                tran_id, tran_type, payment_method, invoice_ref,
                location_id, tran_type_with, user_id, tran_by, user_name,
                store_id, tran_date, status,
                bill_amount, discount, net_amount,
                receive, payment, due,
                doctor_custom_id, patient_id, sr_id
            ])

        insert_diagnosis_detail_rows(products, tran_id, tran_type, payment_method, invoice_ref, location_id, tran_type_with, user_id, tran_by, store_id, tran_date, status, discount, receive, payment, due, doctor_custom_id, patient_id, sr_id)  # codex change

        return JsonResponse({
            "success": True,
            "tran_id": tran_id,
            "doctor_id": doctor_custom_id,
            "patient_id": patient_id,
            "sr_id": sr_id,
            "tran_by": tran_by
        })

    except Exception as e:
        print("🔥 DIAGNOSIS PAYMENT SAVE ERROR")
        traceback.print_exc()

        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)

def diagnosis_payment_list_load(request):
    q = request.GET.get("q", "").strip()

    start_date = request.GET.get("start_date", "").strip()
    end_date = request.GET.get("end_date", "").strip()

    status = request.GET.get("status", "").strip()

    # support both names
    transactionmainheads = (
        request.GET.get("transactionmainheads")
        or request.GET.get("tran_main_head")
        or ""
    ).strip()

    doctor_id = request.GET.get("doctor_id", "").strip()  # codex change
    sr_id = request.GET.get("sr_id", "").strip()  # codex change
    patient_id = request.GET.get("patient_id", "").strip()  # codex change
    tran_by = request.GET.get("tran_by", "").strip()  # codex change

    try:
        offset = int(request.GET.get("offset", 0))
    except (TypeError, ValueError):
        offset = 0

    try:
        limit = int(request.GET.get("limit", 50))
    except (TypeError, ValueError):
        limit = 50

    if limit <= 0:
        limit = 50

    if limit > 500:
        limit = 500

    sql = """
        SELECT
            m.id,
            m.tran_id AS tran_id,
            COALESCE(m.invoice_ref, '') AS invoice_ref,
            DATE_FORMAT(m.tran_date, '%%Y-%%m-%%d') AS tran_date,

            COALESCE(tw.tran_with_name, m.tran_type_with, '') AS supplier_name,
            m.tran_user AS tran_user,
            COALESCE(m.tran_by, '') AS tran_by,  -- codex change
            COALESCE(m.user_name, m.tran_user, '') AS user_name,
            COALESCE(d.name, m.doctor_id, '') AS doctor_name,  -- codex change
            COALESCE(sr.name, m.sr_id, '') AS sr_name,  -- codex change
            COALESCE(p.patient_name, m.patient_id, '') AS patient_name,  -- codex change

            COALESCE(m.bill_amount, 0) AS bill_total,
            COALESCE(m.discount, 0) AS discount,
            COALESCE(m.net_amount, 0) AS net_total,
            COALESCE(m.payment, 0) AS advance,
            COALESCE(m.due_col, 0) AS due_collection,
            COALESCE(m.due_disc, 0) AS due_discount,
            COALESCE(m.due, 0) AS due,
            m.status AS status

        FROM transaction__mains m
        LEFT JOIN transaction__withs tw ON tw.id = m.tran_type_with
        LEFT JOIN doctors_info d ON d.custom_doc_id COLLATE utf8mb4_unicode_ci = m.doctor_id COLLATE utf8mb4_unicode_ci  -- codex change
        LEFT JOIN item__sr_agents sr ON sr.custom_sr_id COLLATE utf8mb4_unicode_ci = m.sr_id COLLATE utf8mb4_unicode_ci  -- codex change
        LEFT JOIN patient_info p ON p.user_info_id COLLATE utf8mb4_unicode_ci = m.patient_id COLLATE utf8mb4_unicode_ci  -- codex change
        WHERE 1=1
    """

    total_sql = """
        SELECT COALESCE(SUM(m.due), 0)
        FROM transaction__mains m
        LEFT JOIN transaction__withs tw ON tw.id = m.tran_type_with
        LEFT JOIN doctors_info d ON d.custom_doc_id COLLATE utf8mb4_unicode_ci = m.doctor_id COLLATE utf8mb4_unicode_ci  -- codex change
        LEFT JOIN item__sr_agents sr ON sr.custom_sr_id COLLATE utf8mb4_unicode_ci = m.sr_id COLLATE utf8mb4_unicode_ci  -- codex change
        LEFT JOIN patient_info p ON p.user_info_id COLLATE utf8mb4_unicode_ci = m.patient_id COLLATE utf8mb4_unicode_ci  -- codex change
        WHERE 1=1
    """

    params = []
    total_params = []

    # Diagnosis only
    sql += " AND m.tran_type = %s"
    params.append(10)

    total_sql += " AND m.tran_type = %s"
    total_params.append(10)

    # Search
    if q:
        sql += """
            AND (
                m.tran_id LIKE %s
                OR m.invoice_ref LIKE %s
                OR m.tran_user LIKE %s
                OR m.tran_by LIKE %s  -- codex change
                OR m.user_name LIKE %s
                OR d.name LIKE %s  -- codex change
                OR sr.name LIKE %s  -- codex change
                OR p.patient_name LIKE %s  -- codex change
            )
        """

        params.extend([
            f"%{q}%",
            f"%{q}%",
            f"%{q}%",
            f"%{q}%",  # codex change
            f"%{q}%",  # codex change
            f"%{q}%",  # codex change
            f"%{q}%",  # codex change
            f"%{q}%"
        ])

        total_sql += """
            AND (
                m.tran_id LIKE %s
                OR m.invoice_ref LIKE %s
                OR m.tran_user LIKE %s
                OR m.tran_by LIKE %s  -- codex change
                OR m.user_name LIKE %s
                OR d.name LIKE %s  -- codex change
                OR sr.name LIKE %s  -- codex change
                OR p.patient_name LIKE %s  -- codex change
            )
        """

        total_params.extend([
            f"%{q}%",
            f"%{q}%",
            f"%{q}%",
            f"%{q}%",  # codex change
            f"%{q}%",  # codex change
            f"%{q}%",  # codex change
            f"%{q}%",  # codex change
            f"%{q}%"
        ])

    # Status
    if status:
        sql += " AND m.status = %s"
        params.append(status)

        total_sql += " AND m.status = %s"
        total_params.append(status)

    # Main head
    # note: diagnosis already fixed as tran_type=10
    # tai same value 10 hole ok, different hole no data
    if transactionmainheads:
        sql += " AND m.tran_type = %s"
        params.append(transactionmainheads)

        total_sql += " AND m.tran_type = %s"
        total_params.append(transactionmainheads)

    # Doctor
    if doctor_id:  # codex change
        sql += " AND m.doctor_id = %s"  # codex change
        params.append(doctor_id)  # codex change

        total_sql += " AND m.doctor_id = %s"  # codex change
        total_params.append(doctor_id)  # codex change

    # SR
    if sr_id:  # codex change
        sql += " AND m.sr_id = %s"  # codex change
        params.append(sr_id)  # codex change

        total_sql += " AND m.sr_id = %s"  # codex change
        total_params.append(sr_id)  # codex change

    # Patient
    if patient_id:  # codex change
        sql += " AND m.patient_id = %s"  # codex change
        params.append(patient_id)  # codex change

        total_sql += " AND m.patient_id = %s"  # codex change
        total_params.append(patient_id)  # codex change

    # Transaction By
    if tran_by:  # codex change
        sql += " AND m.tran_by = %s"  # codex change
        params.append(tran_by)  # codex change

        total_sql += " AND m.tran_by = %s"  # codex change
        total_params.append(tran_by)  # codex change

    # Date
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

    sql += """
        ORDER BY m.id DESC
        LIMIT %s OFFSET %s
    """

    params.extend([limit, offset])

    print("DIAGNOSIS LIST SQL:", sql)
    print("DIAGNOSIS LIST PARAMS:", params)

    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        data = dictfetchall(cursor)

        cursor.execute(total_sql, total_params)
        total_due = cursor.fetchone()[0] or 0

    return JsonResponse({
        "results": data,
        "total_due": float(total_due)
    })

# =========================
# PARTY PAYMENTS
# =========================
def diagnosis_party_payment_list(request):  # codex change
    return render(request, "diagnosis/party_payment/payment_list.html")  # codex change

def diagnosis_party_payment_list_load(request):  # codex change
    return diagnosis_payment_list_load(request)  # codex change

def diagnosis_filter_doctor_combo(request):  # codex change
    q = request.GET.get("q", "").strip()  # codex change
    with connection.cursor() as cursor:  # codex change
        cursor.execute("""  -- codex change
            SELECT custom_doc_id AS id, CONCAT(custom_doc_id, ' - ', name) AS name  
            FROM doctors_info  
            WHERE (%s = '' OR name LIKE %s OR custom_doc_id LIKE %s)  
            ORDER BY name ASC  
            LIMIT 200  
        """, [q, f"%{q}%", f"%{q}%"])  # codex change
        data = dictfetchall(cursor)  # codex change
    return JsonResponse({"results": data})  # codex change

def diagnosis_filter_sr_combo(request):  # codex change
    q = request.GET.get("q", "").strip()  # codex change
    with connection.cursor() as cursor:  # codex change
        cursor.execute("""  
            SELECT custom_sr_id AS id, CONCAT(custom_sr_id, ' - ', name) AS name  
            FROM item__sr_agents  
            WHERE (%s = '' OR name LIKE %s OR custom_sr_id LIKE %s)  
            ORDER BY name ASC  
            LIMIT 200  
        """, [q, f"%{q}%", f"%{q}%"])  # codex change
        data = dictfetchall(cursor)  # codex change
    return JsonResponse({"results": data})  # codex change

def diagnosis_filter_patient_combo(request):  # codex change
    q = request.GET.get("q", "").strip()  # codex change
    with connection.cursor() as cursor:  # codex change
        cursor.execute("""  
            SELECT user_info_id AS id, CONCAT(user_info_id, ' - ', patient_name) AS name  
            FROM patient_info  
            WHERE user_info_id IS NOT NULL  
              AND (%s = '' OR patient_name LIKE %s OR user_info_id LIKE %s)  
            ORDER BY id DESC  
            LIMIT 200  
        """, [q, f"%{q}%", f"%{q}%"])  # codex change
        data = dictfetchall(cursor)  # codex change
    return JsonResponse({"results": data})  # codex change

def diagnosis_filter_tran_by_combo(request):  # codex change
    q = request.GET.get("q", "").strip()  # codex change
    with connection.cursor() as cursor:  # codex change
        cursor.execute(""" 
            SELECT DISTINCT tran_by AS id, tran_by AS name  
            FROM transaction__mains 
            WHERE tran_type = 10 
              AND tran_by IS NOT NULL  
              AND tran_by <> '' 
              AND (%s = '' OR tran_by LIKE %s)  
            ORDER BY tran_by ASC 
            LIMIT 200  
        """, [q, f"%{q}%"])  # codex change
        data = dictfetchall(cursor)  # codex change
    return JsonResponse({"results": data})  # codex change

def diagnosis_salesman_transaction_summary_page(request):  # codex change
    return render(request, "diagnosis/reports/salesman/transaction_summary.html")

def diagnosis_salesman_transaction_details_page(request):  # codex change
    return render(request, "diagnosis/reports/salesman/transaction_details.html")

def diagnosis_salesman_transaction_details_load(request):  # codex change
    q = request.GET.get("q", "").strip()
    start_date = request.GET.get("start_date", "").strip()
    end_date = request.GET.get("end_date", "").strip()
    status = request.GET.get("status", "").strip()
    transactionmainheads = (
        request.GET.get("transactionmainheads")
        or request.GET.get("tran_main_head")
        or ""
    ).strip()
    doctor_id = request.GET.get("doctor_id", "").strip()
    sr_id = request.GET.get("sr_id", "").strip()
    patient_id = request.GET.get("patient_id", "").strip()
    tran_by = request.GET.get("tran_by", "").strip()

    try:
        offset = int(request.GET.get("offset", 0))
    except (TypeError, ValueError):
        offset = 0

    try:
        limit = int(request.GET.get("limit", 50))
    except (TypeError, ValueError):
        limit = 50

    if limit <= 0:
        limit = 50

    if limit > 500:
        limit = 500

    sql = """
        SELECT
            d.id,
            d.tran_id,
            COALESCE(d.invoice_ref, '') AS invoice_ref,
            DATE_FORMAT(d.tran_date, '%%Y-%%m-%%d') AS tran_date,
            d.tran_type,
            d.tran_method,
            d.loc_id,
            COALESCE(tw.tran_with_name, d.tran_type_with, '') AS tran_type_with,
            d.tran_bank,
            d.tran_user,
            COALESCE(d.tran_by, '') AS tran_by,
            d.ptn_id,
            d.user_name,
            d.user_phone,
            d.user_address,
            d.tran_groupe_id,
            d.tran_head_id,
            COALESCE(h.tran_head_name, '') AS tran_head_name,
            d.quantity_actual,
            d.quantity,
            d.quantity_issue,
            d.quantity_return,
            d.unit_id,
            d.amount,
            d.tot_amount,
            d.discount,
            d.cp,
            d.mrp,
            d.receive,
            d.payment,
            d.due,
            d.due_col,
            d.due_disc,
            d.expiry_date,
            d.store_id,
            d.payment_mode,
            d.batch_id,
            d.booking_id,
            d.status,
            d.doctor_id,
            COALESCE(doc.name, d.doctor_id, '') AS doctor_name,
            d.patient_id,
            COALESCE(p.patient_name, d.patient_id, '') AS patient_name,
            d.sr_id,
            COALESCE(sr.name, d.sr_id, '') AS sr_name
        FROM transaction__details d
        LEFT JOIN transaction__heads h ON h.id = d.tran_head_id
        LEFT JOIN transaction__withs tw ON tw.id = d.tran_type_with
        LEFT JOIN doctors_info doc ON doc.custom_doc_id COLLATE utf8mb4_unicode_ci = d.doctor_id COLLATE utf8mb4_unicode_ci
        LEFT JOIN patient_info p ON p.user_info_id COLLATE utf8mb4_unicode_ci = d.patient_id COLLATE utf8mb4_unicode_ci
        LEFT JOIN item__sr_agents sr ON sr.custom_sr_id COLLATE utf8mb4_unicode_ci = d.sr_id COLLATE utf8mb4_unicode_ci
        WHERE d.tran_type = %s
    """

    params = [10]

    if q:
        sql += " AND h.tran_head_name LIKE %s"
        params.append(f"%{q}%")

    if status:
        sql += " AND d.status = %s"
        params.append(status)

    if transactionmainheads:
        sql += " AND d.tran_type = %s"
        params.append(transactionmainheads)

    if doctor_id:
        sql += " AND d.doctor_id = %s"
        params.append(doctor_id)

    if sr_id:
        sql += " AND d.sr_id = %s"
        params.append(sr_id)

    if patient_id:
        sql += " AND d.patient_id = %s"
        params.append(patient_id)

    if tran_by:
        sql += " AND d.tran_by = %s"
        params.append(tran_by)

    if start_date:
        sql += " AND DATE(d.tran_date) >= %s"
        params.append(start_date)

    if end_date:
        sql += " AND DATE(d.tran_date) <= %s"
        params.append(end_date)

    sql += """
        ORDER BY d.id DESC
        LIMIT %s OFFSET %s
    """
    params.extend([limit, offset])

    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        data = dictfetchall(cursor)

    return JsonResponse({
        "results": data
    })

def diagnosis_payment_form(request, id):

    sql = """
        SELECT
            m.id,  -- codex change
            m.tran_id,  -- codex change
            m.invoice_ref,  -- codex change
            m.tran_date,  -- codex change
            m.tran_type_with,  -- codex change
            m.tran_user,  -- codex change
            m.user_name,  -- codex change
            m.bill_amount,  -- codex change
            m.discount,  -- codex change
            m.net_amount,  -- codex change
            m.payment,  -- codex change
            m.receive,  -- codex change
            m.due_col,  -- codex change
            m.due_disc,  -- codex change
            m.due,  -- codex change
            m.patient_id,  -- codex change
            p.patient_name,  -- codex change
            CONCAT(COALESCE(p.age_y, 0), 'Y ', COALESCE(p.age_m, 0), 'M ', COALESCE(p.age_d, 0), 'D') AS patient_age,  -- codex change
            p.gender AS patient_gender,  -- codex change
            p.blood_group AS patient_blood_group,  -- codex change
            p.present_mobile AS patient_mobile,  -- codex change
            p.present_address AS patient_address  -- codex change
        FROM transaction__mains m  -- codex change
        LEFT JOIN patient_info p ON p.user_info_id COLLATE utf8mb4_unicode_ci = m.patient_id COLLATE utf8mb4_unicode_ci  -- codex change
        WHERE m.id = %s  -- codex change
          AND m.tran_type = 10  -- codex change
        LIMIT 1
    """

    with connection.cursor() as cursor:
        cursor.execute(sql, [id])
        row = dictfetchall(cursor)

    transaction_data = row[0] if row else None

    return render(
        request,
        "diagnosis/party_payment/payment_form.html",  # codex change
        {
            "transaction": transaction_data
        }
    )

def diagnosis_party_payment_form(request, id):  # codex change
    return diagnosis_payment_form(request, id)  # codex change

@csrf_exempt
@transaction.atomic
def process_diagnosis_payment(request, id):

    if request.method != "POST":
        return JsonResponse({
            "success": False,
            "error": "Invalid request method"
        }, status=405)

    try:
        pay_amount = float(request.POST.get("pay_amount", 0) or 0)
        due_discount = float(request.POST.get("due_discount", 0) or 0)

    except Exception:
        return JsonResponse({
            "success": False,
            "error": "Invalid amount"
        }, status=400)

    # ================= VALIDATION =================
    if pay_amount <= 0 and due_discount <= 0:
        return JsonResponse({
            "success": False,
            "error": "Payment or discount must be greater than 0"
        }, status=400)

    with connection.cursor() as cursor:

        # ================= FETCH MAIN =================
        cursor.execute("""
            SELECT 
                id,
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
                receive,
                due,
                due_col,
                due_disc,
                doctor_id,
                patient_id,
                sr_id
            FROM transaction__mains
            WHERE id = %s
              AND tran_type = 10
            LIMIT 1
        """, [id])

        row = cursor.fetchone()

        if not row:
            return JsonResponse({
                "success": False,
                "error": "Diagnosis transaction not found"
            }, status=404)

        (
            main_id,
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
            old_receive,
            current_due,
            old_due_col,
            old_due_disc,
            doctor_id,
            patient_id,
            sr_id
        ) = row

        current_due = float(current_due or 0)
        old_due_col = float(old_due_col or 0)
        old_due_disc = float(old_due_disc or 0)

        # ================= VALIDATION =================
        if current_due <= 0:
            return JsonResponse({
                "success": False,
                "error": "No due amount found"
            }, status=400)

        if (pay_amount + due_discount) > current_due:
            return JsonResponse({
                "success": False,
                "error": "Payment + Discount exceeds due"
            }, status=400)

        # ================= CALCULATION =================
        new_due = current_due - pay_amount - due_discount
        new_due_col = old_due_col + pay_amount
        new_due_disc = old_due_disc + due_discount

        # ================= UPDATE MAIN =================
        cursor.execute("""
            UPDATE transaction__mains
            SET
                due = %s,
                due_col = %s,
                due_disc = %s
            WHERE id = %s
              AND tran_type = 10
        """, [
            new_due,
            new_due_col,
            new_due_disc,
            id
        ])

        # ================= INSERT PARTY PAYMENT HISTORY =================  # codex change
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

            pay_amount,
            new_due,
            pay_amount,
            due_discount
        ])

        if new_due <= 0:  # codex change
            cursor.execute("""  # codex change
                UPDATE transaction__details  # codex change
                SET due = 0  # codex change
                WHERE tran_id = %s  # codex change
                  AND tran_type = 10  # codex change
            """, [old_tran_id])  # codex change

    return JsonResponse({
        "success": True,
        "paid": pay_amount,
        "due_discount": due_discount,
        "new_due": new_due,
        "new_due_col": new_due_col,
        "new_due_disc": new_due_disc,
        "redirect_url": "/diagnosis/party-payment/"  # codex change
    })

@csrf_exempt  # codex change
def process_diagnosis_party_payment(request, id):  # codex change
    return process_diagnosis_payment(request, id)  # codex change

@csrf_exempt
@transaction.atomic
def process_diagnosis_party_fifo_payment(request):  # codex change
    payment_amount = float(request.POST.get("payment", 0) or 0)  # codex change
    ids = json.loads(request.POST.get("ids", "[]"))  # codex change

    if payment_amount <= 0 or not ids:  # codex change
        return JsonResponse({"success": False, "error": "Invalid payment request"})  # codex change

    remaining = payment_amount  # codex change

    with connection.cursor() as cursor:  # codex change
        placeholders = ",".join(["%s"] * len(ids))  # codex change

        cursor.execute(f"""  -- codex change
            SELECT id, invoice_ref, bill_amount, payment, due
            FROM transaction__mains
            WHERE id IN ({placeholders})
              AND tran_type = 10
            ORDER BY tran_date ASC, id ASC
        """, ids)  # codex change

        rows = cursor.fetchall()  # codex change

        for row in rows:  # codex change
            row_id, invoice_ref, bill_amount, old_payment, due = row  # codex change
            bill_amount = float(bill_amount or 0)  # codex change
            old_payment = float(old_payment or 0)  # codex change
            due = float(due or 0)  # codex change

            if remaining <= 0:  # codex change
                break  # codex change

            if due <= 0:  # codex change
                continue  # codex change

            pay = min(remaining, due)  # codex change
            new_payment = old_payment + pay  # codex change
            new_due = bill_amount - new_payment  # codex change

            cursor.execute("""  -- codex change
                UPDATE transaction__mains
                SET payment = %s,
                    due = %s
                WHERE id = %s
                  AND tran_type = 10
            """, [new_payment, new_due, row_id])  # codex change

            cursor.execute("""  -- codex change
                UPDATE transaction__details
                SET payment = payment + %s,
                    due = due - %s
                WHERE invoice_ref = %s
                  AND tran_type = 10
            """, [pay, pay, invoice_ref])  # codex change

            if new_due <= 0:  # codex change
                cursor.execute("""  -- codex change
                    UPDATE transaction__details
                    SET due = 0
                    WHERE invoice_ref = %s
                      AND tran_type = 10
                """, [invoice_ref])  # codex change

            remaining -= pay  # codex change

    return JsonResponse({  # codex change
        "success": True,  # codex change
        "paid": payment_amount - remaining,  # codex change
    })  # codex change

from io import BytesIO

from django.db import connection
from django.http import HttpResponse

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer
)


def dictfetchall(cursor):
    columns = [
        column[0]
        for column in cursor.description
    ]

    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def diagnosis_payment_report_pdf(request):

    # =========================
    # REQUEST FILTERS
    # =========================
    q = (request.GET.get("q") or "").strip()

    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    main_head = (
        request.GET.get("transactionmainheads")
        or request.GET.get("main_head")
        or "10"
    )

    doctor_id = (
        request.GET.get("doctor_id")
        or ""
    )

    sr_id = (
        request.GET.get("sr_id")
        or ""
    )

    patient_id = (
        request.GET.get("patient_id")
        or ""
    )

    tran_by = (
        request.GET.get("tran_by")
        or ""
    )

    status = (
        request.GET.get("status")
        or ""
    )

    # =========================
    # BASE SQL
    # =========================
    sql = """
        SELECT
            m.id,
            m.tran_id,
            m.invoice_ref,
            m.tran_date,
            m.tran_type,
            m.tran_type_with,

            mh.type_name AS main_head_name,
            tw.tran_with_name AS tran_with_name,

            m.tran_user,
            m.user_name,
            m.tran_by,

            m.bill_amount,
            m.discount,
            m.net_amount,
            m.payment,
            m.due_col,
            m.due_disc,
            m.due,

            m.doctor_id,
            m.patient_id,
            m.sr_id,

            d.name AS doctor_name,

            patient_user.user_name AS patient_name,

            sr.agent_name AS sr_name

        FROM transaction__mains m

        LEFT JOIN transaction__main__heads mh
            ON mh.id = m.tran_type

        LEFT JOIN transaction__withs tw
            ON tw.id = m.tran_type_with

        LEFT JOIN doctors_info d
            ON d.custom_doc_id = m.doctor_id

        LEFT JOIN user__infos patient_user
            ON patient_user.user_id = m.patient_id

        LEFT JOIN item__sr_agents sr
            ON sr.custom_sr_id = m.sr_id

        WHERE 1 = 1
    """

    params = []

    # =========================
    # DIAGNOSIS PAYMENT ONLY
    # =========================
    sql += " AND m.tran_id LIKE %s"
    params.append("DPA%")

    # Diagnosis main head
    sql += " AND m.tran_type = %s"
    params.append(10)

    # =========================
    # SEARCH
    # =========================
    if q:
        search_value = f"%{q}%"

        sql += """
            AND (
                m.tran_id LIKE %s
                OR m.invoice_ref LIKE %s
                OR m.tran_user LIKE %s
                OR m.user_name LIKE %s
                OR m.tran_by LIKE %s
                OR m.doctor_id LIKE %s
                OR m.patient_id LIKE %s
                OR m.sr_id LIKE %s
                OR d.name LIKE %s
                OR patient_user.user_name LIKE %s
                OR sr.agent_name LIKE %s
            )
        """

        params.extend([
            search_value,
            search_value,
            search_value,
            search_value,
            search_value,
            search_value,
            search_value,
            search_value,
            search_value,
            search_value,
            search_value
        ])

    # =========================
    # DATE FILTER
    # =========================
    if start_date:
        sql += """
            AND DATE(m.tran_date) >= %s
        """
        params.append(start_date)

    if end_date:
        sql += """
            AND DATE(m.tran_date) <= %s
        """
        params.append(end_date)

    # =========================
    # MAIN HEAD FILTER
    # =========================
    if main_head and main_head != "null":
        sql += """
            AND m.tran_type = %s
        """
        params.append(main_head)

    # =========================
    # DOCTOR FILTER
    # Frontend numeric id/custom id
    # দুটোই handle করবে
    # =========================
    doctor_text = "All"

    if doctor_id and doctor_id != "null":

        with connection.cursor() as cursor:

            if str(doctor_id).isdigit():
                cursor.execute("""
                    SELECT custom_doc_id, name
                    FROM doctors_info
                    WHERE id = %s
                    LIMIT 1
                """, [doctor_id])
            else:
                cursor.execute("""
                    SELECT custom_doc_id, name
                    FROM doctors_info
                    WHERE custom_doc_id = %s
                    LIMIT 1
                """, [doctor_id])

            doctor_row = cursor.fetchone()

        if doctor_row:
            doctor_custom_id = doctor_row[0]
            doctor_text = doctor_row[1] or doctor_row[0]

            sql += """
                AND m.doctor_id = %s
            """
            params.append(doctor_custom_id)

    # =========================
    # SR FILTER
    # =========================
    sr_text = "All"

    if sr_id and sr_id != "null":

        with connection.cursor() as cursor:

            if str(sr_id).isdigit():
                cursor.execute("""
                    SELECT custom_sr_id, agent_name
                    FROM item__sr_agents
                    WHERE id = %s
                    LIMIT 1
                """, [sr_id])
            else:
                cursor.execute("""
                    SELECT custom_sr_id, agent_name
                    FROM item__sr_agents
                    WHERE custom_sr_id = %s
                    LIMIT 1
                """, [sr_id])

            sr_row = cursor.fetchone()

        if sr_row:
            sr_custom_id = sr_row[0]
            sr_text = sr_row[1] or sr_row[0]

            sql += """
                AND m.sr_id = %s
            """
            params.append(sr_custom_id)

    # =========================
    # PATIENT FILTER
    # =========================
    patient_text = "All"

    if patient_id and patient_id != "null":

        with connection.cursor() as cursor:

            if str(patient_id).isdigit():
                cursor.execute("""
                    SELECT user_id, user_name
                    FROM user__infos
                    WHERE id = %s
                    LIMIT 1
                """, [patient_id])
            else:
                cursor.execute("""
                    SELECT user_id, user_name
                    FROM user__infos
                    WHERE user_id = %s
                    LIMIT 1
                """, [patient_id])

            patient_row = cursor.fetchone()

        if patient_row:
            patient_custom_id = patient_row[0]
            patient_text = patient_row[1] or patient_row[0]

            sql += """
                AND m.patient_id = %s
            """
            params.append(patient_custom_id)

    # =========================
    # TRANSACTION BY FILTER
    # =========================
    tran_by_text = "All"

    if tran_by and tran_by != "null":
        tran_by_text = tran_by

        sql += """
            AND m.tran_by = %s
        """
        params.append(tran_by)

    # =========================
    # STATUS FILTER
    # =========================
    status_text = "All"

    if status not in ["", None, "null"]:
        sql += """
            AND m.status = %s
        """
        params.append(status)

        if str(status) == "1":
            status_text = "Pending"
        elif str(status) == "2":
            status_text = "Verified"
        elif str(status) == "0":
            status_text = "Deleted"
        else:
            status_text = str(status)

    # =========================
    # ORDER
    # =========================
    sql += """
        ORDER BY m.id ASC
    """

    # =========================
    # EXECUTE QUERY
    # =========================
    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        data = dictfetchall(cursor)

    # =========================
    # TOTALS
    # =========================
    total_bill = sum(
        float(row["bill_amount"] or 0)
        for row in data
    )

    total_discount = sum(
        float(row["discount"] or 0)
        for row in data
    )

    total_net = sum(
        float(row["net_amount"] or 0)
        for row in data
    )

    total_advance = sum(
        float(row["payment"] or 0)
        for row in data
    )

    total_due_collection = sum(
        float(row["due_col"] or 0)
        for row in data
    )

    total_due_discount = sum(
        float(row["due_disc"] or 0)
        for row in data
    )

    total_due = sum(
        float(row["due"] or 0)
        for row in data
    )

    # =========================
    # MAIN HEAD TEXT
    # =========================
    main_head_text = "All"

    if main_head and main_head != "null":

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT type_name
                FROM transaction__main__heads
                WHERE id = %s
                LIMIT 1
            """, [main_head])

            main_head_row = cursor.fetchone()

        if main_head_row:
            main_head_text = main_head_row[0]

    # =========================
    # PDF SETUP
    # Landscape used because
    # many columns are present
    # =========================
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        leftMargin=20,
        rightMargin=20,
        topMargin=25,
        bottomMargin=25
    )

    styles = getSampleStyleSheet()

    title_style = styles["Title"]
    normal_style = styles["Normal"]

    elements = []

    # =========================
    # TITLE
    # =========================
    report_title = "Diagnosis Party Payment Report" if "party-payment" in request.path else "Diagnosis Payment Report"  # codex change
    elements.append(
        Paragraph(
            report_title,  # codex change
            title_style
        )
    )

    elements.append(
        Spacer(1, 10)
    )

    # =========================
    # HEADER INFORMATION
    # =========================
    header_text = f"""
        <b>Start Date:</b> {start_date or "-"}
        &nbsp;&nbsp;&nbsp;

        <b>End Date:</b> {end_date or "-"}
        &nbsp;&nbsp;&nbsp;

        <b>Status:</b> {status_text}
        <br/><br/>

        <b>Main Head:</b> {main_head_text}
        &nbsp;&nbsp;&nbsp;

        <b>Doctor:</b> {doctor_text}
        &nbsp;&nbsp;&nbsp;

        <b>SR:</b> {sr_text}
        <br/><br/>

        <b>Patient:</b> {patient_text}
        &nbsp;&nbsp;&nbsp;

        <b>Transaction By:</b> {tran_by_text}
    """

    elements.append(
        Paragraph(
            header_text,
            normal_style
        )
    )

    elements.append(
        Spacer(1, 15)
    )

    # =========================
    # TABLE HEADER
    # =========================
    table_data = [[
        "SL",
        "Tran ID",
        "Invoice",
        "Date",
        "Tran With",
        "Doctor",
        "SR",
        "Patient",
        "Tran By",
        "Bill",
        "Discount",
        "Net",
        "Advance",
        "Due Col",
        "Due Disc",
        "Due"
    ]]

    # =========================
    # TABLE ROWS
    # =========================
    for index, row in enumerate(data, 1):

        tran_date_text = ""

        if row["tran_date"]:
            try:
                tran_date_text = (
                    row["tran_date"]
                    .strftime("%Y-%m-%d")
                )
            except Exception:
                tran_date_text = str(
                    row["tran_date"]
                )

        table_data.append([
            index,
            row["tran_id"] or "",
            row["invoice_ref"] or "",
            tran_date_text,
            row["tran_with_name"] or "",
            row["doctor_name"] or row["doctor_id"] or "",
            row["sr_name"] or row["sr_id"] or "",
            row["patient_name"] or row["patient_id"] or "",
            row["tran_by"] or "",
            f'{float(row["bill_amount"] or 0):.2f}',
            f'{float(row["discount"] or 0):.2f}',
            f'{float(row["net_amount"] or 0):.2f}',
            f'{float(row["payment"] or 0):.2f}',
            f'{float(row["due_col"] or 0):.2f}',
            f'{float(row["due_disc"] or 0):.2f}',
            f'{float(row["due"] or 0):.2f}'
        ])

    # =========================
    # EMPTY RESULT
    # =========================
    if not data:
        table_data.append([
            "",
            "No diagnosis payment data found",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            ""
        ])

    # =========================
    # TABLE
    # =========================
    table = Table(
        table_data,
        repeatRows=1,
        colWidths=[
            22,  # SL
            63,  # Tran ID
            63,  # Invoice
            52,  # Date
            62,  # Tran With
            65,  # Doctor
            55,  # SR
            65,  # Patient
            55,  # Tran By
            42,  # Bill
            42,  # Discount
            42,  # Net
            42,  # Advance
            42,  # Due Col
            42,  # Due Disc
            42   # Due
        ]
    )

    table.setStyle(
        TableStyle([
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.black
            ),

            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.grey
            ),

            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white
            ),

            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),

            (
                "ALIGN",
                (0, 0),
                (-1, -1),
                "CENTER"
            ),

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            ),

            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                6
            ),

            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                2
            ),

            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                2
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                4
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                4
            ),

            (
                "ALIGN",
                (9, 1),
                (-1, -1),
                "RIGHT"
            )
        ])
    )

    elements.append(table)

    # =========================
    # TOTAL SUMMARY
    # =========================
    elements.append(
        Spacer(1, 12)
    )

    total_text = f"""
        <b>Total Bill:</b> {total_bill:.2f}
        &nbsp;&nbsp;&nbsp;

        <b>Total Discount:</b> {total_discount:.2f}
        &nbsp;&nbsp;&nbsp;

        <b>Total Net:</b> {total_net:.2f}
        <br/><br/>

        <b>Total Advance:</b> {total_advance:.2f}
        &nbsp;&nbsp;&nbsp;

        <b>Total Due Collection:</b> {total_due_collection:.2f}
        &nbsp;&nbsp;&nbsp;

        <b>Total Due Discount:</b> {total_due_discount:.2f}
        &nbsp;&nbsp;&nbsp;

        <b>Total Due:</b> {total_due:.2f}
    """

    elements.append(
        Paragraph(
            total_text,
            normal_style
        )
    )

    # =========================
    # BUILD PDF
    # =========================
    doc.build(elements)

    buffer.seek(0)

    response = HttpResponse(
        buffer,
        content_type="application/pdf"
    )

    response[
        "Content-Disposition"
    ] = (
        'inline; '
        f'filename="{report_title.lower().replace(" ", "_")}.pdf"'  # codex change
    )

    return response

def diagnosis_party_payment_report_pdf(request):  # codex change
    return diagnosis_payment_report_pdf(request)  # codex change

# refferal
