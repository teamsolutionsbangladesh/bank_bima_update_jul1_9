from datetime import datetime
import json
from zoneinfo import ZoneInfo

from django.contrib.sessions.models import Session
from django.db import connection, transaction
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from general_transaction.models import LocationInfos, TransactionWiths, UserInfos


LOCAL_TIMEZONE = ZoneInfo("Asia/Dhaka")


def get_local_tran_datetime(date_value=None):
    now = datetime.now(LOCAL_TIMEZONE).replace(tzinfo=None)
    if date_value:
        return datetime.combine(
            datetime.strptime(date_value, "%Y-%m-%d").date(),
            now.time()
        )
    return now


def get_recent_session_user():
    for session in Session.objects.filter(expire_date__gt=datetime.now(LOCAL_TIMEZONE)).order_by("-expire_date")[:20]:
        data = session.get_decoded()
        if data.get("user_id") and data.get("user_name"):
            return data
    return {}


def get_login_location(request):
    if not request.session.get("user_id") or not request.session.get("user_name"):
        recent_user = get_recent_session_user()
        request.session["user_id"] = recent_user.get("user_id", request.session.get("user_id", ""))
        request.session["user_name"] = recent_user.get("user_name", request.session.get("user_name", ""))
    location_id = request.session.get("loc_id")
    location_name = request.session.get("location_name")
    if not location_id and request.session.get("user_id"):
        user_info = UserInfos.objects.filter(user_id=request.session.get("user_id")).first() or UserInfos.objects.filter(login_user_id=request.session.get("user_id")).first()
        location_id = user_info.loc_id if user_info else None
    if not location_id and request.session.get("user_name"):
        user_info = UserInfos.objects.filter(user_name=request.session.get("user_name"), loc_id__isnull=False).order_by("-id").first()
        location_id = user_info.loc_id if user_info else None
    location = LocationInfos.objects.filter(id=location_id, status=1).first() if location_id else None
    if location:
        request.session["loc_id"] = location.id
        request.session["location_name"] = location.division
        return location.id, location.division
    return "", ""


def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def advertisement_sales_add(request):
    fixed_location_id, fixed_location_name = get_login_location(request)
    return render(request, "bank_bima/advertisement_sales_payment.html", {
        "fixed_location_id": fixed_location_id or "",
        "fixed_location_name": fixed_location_name or "",
        "page_title": "Advertisement Sales",
        "page_id": request.GET.get("page_id") or "",
    })


def printing_sales_add(request):
    fixed_location_id, fixed_location_name = get_login_location(request)
    return render(request, "bank_bima/printing_sales_payment.html", {
        "fixed_location_id": fixed_location_id or "",
        "fixed_location_name": fixed_location_name or "",
        "page_title": "Printing Sale",
        "page_id": request.GET.get("page_id") or "",
    })


def office_bazar_add(request):
    fixed_location_id, fixed_location_name = get_login_location(request)
    return render(request, "bank_bima/office_bazar_payment.html", {
        "fixed_location_id": fixed_location_id or "",
        "fixed_location_name": fixed_location_name or "",
        "page_title": "Office Bazar",
        "page_id": request.GET.get("page_id") or "",
    })


def advertisement_sales_list(request):
    page_id = request.GET.get("page_id") 
    return render(request, "bank_bima/advertisement_sales_list.html", {
        "page_title": "Advertisement Sales",
        "list_title": "Advertisement Sales List",
        "page_id": page_id,
        "payment_list_url": "/bank-bima/advertisement-sales/load/",
        "payment_edit_url": "/bank-bima/advertisement-sales/edit/",
    })


def printing_sales_list(request):
    page_id = request.GET.get("page_id")
    return render(request, "bank_bima/printing_sales_list.html", {
        "page_title": "Printing Sale",
        "list_title": "Printing Sale List",
        "page_id": page_id,
        "payment_list_url": "/bank-bima/printing-sales/load/",
        "payment_edit_url": "/bank-bima/printing-sales/edit/",
    })


def office_bazar_list(request):
    page_id = request.GET.get("page_id")
    return render(request, "bank_bima/office_bazar_list.html", {
        "page_title": "Office Bazar",
        "list_title": "Office Bazar List",
        "page_id": page_id,
        "payment_list_url": "/bank-bima/office-bazar/load/",
        "payment_edit_url": "/bank-bima/office-bazar/edit/",
    })


def _page_init_data(page_id):
    cursor = connection.cursor()
    cursor.execute("""
        SELECT
            s.tran_main_head_id AS tran_main_head_id,
            s.user_tran_method AS user_tran_method,
            s.user_tran_with_id AS user_tran_with_id,
            s.tran_method AS tran_method,
            s.tran_group_id AS tran_group_id
        FROM page_init s
        WHERE s.page_id = %s
    """, [page_id])
    return [
        {
            "tran_main_head_id": row[0],
            "user_tran_method": row[1],
            "user_tran_with_id": row[2],
            "tran_method": row[3],
            "tran_group_id": row[4],
        }
        for row in cursor.fetchall()
    ]


def advertisement_sales_page_init(request):
    page_id = request.GET.get("page_id")
    return JsonResponse({"get_page_init_data": _page_init_data(page_id)})


def printing_sales_page_init(request):
    page_id = request.GET.get("page_id")
    return JsonResponse({"get_page_init_data": _page_init_data(page_id)})


def office_bazar_page_init(request):
    page_id = request.GET.get("page_id")
    return JsonResponse({"get_page_init_data": _page_init_data(page_id)})


def advertisement_sales_load(request):
    q = (request.GET.get("q") or request.GET.get("search") or "").strip()
    status_filter = request.GET.get("status", "").strip()
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    page_id = request.GET.get("page_id")
    tran_main_head = request.GET.get("tran_main_head") or request.GET.get("transactionmainheads")
    tran_with_method = request.GET.get("tran_with_method") or request.GET.get("transaction_with_method")
    tran_with = request.GET.get("tran_with") or request.GET.get("transaction_with")
    supplier = request.GET.get("supplier") or request.GET.get("transaction_with_user")
    tran_group = request.GET.get("tran_group") or request.GET.get("tran_group_id")

    if page_id:
        page_rows = _page_init_data(page_id)
        if page_rows:
            tran_main_head = page_rows[0].get("tran_main_head_id")
            tran_with_method = page_rows[0].get("user_tran_method")
            tran_with = page_rows[0].get("user_tran_with_id")
            tran_group = page_rows[0].get("tran_group_id")

    try:
        offset = int(request.GET.get("offset", 0))
    except (TypeError, ValueError):
        offset = 0

    try:
        limit = int(request.GET.get("limit") or request.GET.get("per_page") or 50)
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
            m.tran_type_with AS tran_type_with_id,
            COALESCE(tw.tran_with_name, CAST(m.tran_type_with AS CHAR)) AS tran_type_with,
            m.tran_user AS tran_user_id,
            COALESCE(NULLIF(m.user_name, ''), ui.user_name, m.tran_user) AS tran_user,
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
        sql += """
            AND (
                m.tran_type = %s
                OR EXISTS (
                    SELECT 1
                    FROM transaction__details d
                    JOIN transaction__groupes g ON g.id = d.tran_groupe_id
                    WHERE d.tran_id = m.tran_id
                    AND g.tran_groupe_type = %s
                )
            )
        """
        params.extend([tran_main_head, tran_main_head])
        total_sql += """
            AND (
                m.tran_type = %s
                OR EXISTS (
                    SELECT 1
                    FROM transaction__details d
                    JOIN transaction__groupes g ON g.id = d.tran_groupe_id
                    WHERE d.tran_id = m.tran_id
                    AND g.tran_groupe_type = %s
                )
            )
        """
        total_params.extend([tran_main_head, tran_main_head])

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

    if tran_group:
        sql += """
            AND EXISTS (
                SELECT 1
                FROM transaction__details d
                WHERE d.tran_id = m.tran_id
                AND d.tran_groupe_id = %s
            )
        """
        params.append(tran_group)
        total_sql += """
            AND EXISTS (
                SELECT 1
                FROM transaction__details d
                WHERE d.tran_id = m.tran_id
                AND d.tran_groupe_id = %s
            )
        """
        total_params.append(tran_group)

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
        "results": data,
        "total_due": float(total_due),
    })


def printing_sales_load(request):
    return advertisement_sales_load(request)


def advertisement_sales_edit(request, id):
    return JsonResponse({"success": False, "message": "Edit not wired yet"}, status=501)


def printing_sales_edit(request, id):
    return advertisement_sales_edit(request, id)


def add_payment_page(request):
    return advertisement_sales_add(request)


def advertisement_sales_edit(request, id):
    return JsonResponse({"success": False, "message": "Edit not wired yet"}, status=501)


def advertisement_sales_product_search(request):
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
    return JsonResponse({'results': dictfetchall(cursor)})


def printing_sales_product_search(request):
    return advertisement_sales_product_search(request)


@csrf_exempt
@transaction.atomic
def advertisement_sales_save(request):
    if request.method != "POST":
        return JsonResponse({"success": False}, status=405)

    try:
        data = json.loads(request.body)
        store_id = data.get("store")
        location_id = data.get("location")
        user_info_id = data.get("supplier")
        user_name = data.get("user_name")
        tran_type_with = data.get("tran_type_with")
        tran_group_id = data.get("tran_group_id")
        tran_type = data.get("tran_type") or 1
        payment_method = data.get("payment_method")
        edit_id = data.get("edit_id")
        bill_amount = float(data.get("bill_amount") or 0)
        discount = float(data.get("discount") or 0)
        net_amount = float(data.get("net_amount") or 0)
        payment = float(data.get("payment") or 0)
        due = float(data.get("due") or 0)
        products = data.get("products") or []

        if not user_info_id:
            return JsonResponse({"success": False, "message": "User required"}, status=400)

        if not tran_type_with:
            return JsonResponse({"success": False, "message": "Transaction With required"}, status=400)

        tran_date = get_local_tran_datetime(data.get("tran_date"))

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

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT user_name
                FROM user__infos
                WHERE user_id = %s OR CAST(id AS CHAR) = %s
                LIMIT 1
            """, [user_info_id, user_info_id])
            row = cursor.fetchone()
            user_name = row[0] if row else "UNKNOWN"

        if edit_id:
            return JsonResponse({"success": False, "message": "Edit not wired yet"}, status=501)

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO transaction__mains
                (tran_id, tran_type, tran_method, tran_user, user_name,
                 tran_type_with, store_id, loc_id, tran_date, status,
                 invoice_ref, bill_amount, discount, net_amount, payment, due)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, [
                tran_id,
                tran_type,
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
                due,
            ])

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
                tran_type,
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
                due,
            ])

        with connection.cursor() as cursor:
            cursor.executemany("""
                INSERT INTO transaction__details
                (tran_id, tran_type, tran_method, invoice_ref, loc_id,
                tran_type_with, tran_groupe_id, tran_head_id, quantity_actual,
                quantity, quantity_issue, quantity_return, cp, mrp, amount,
                expiry_date, user_name, store_id,
                tran_date, status, discount, receive, payment, due)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, details_data)

        return JsonResponse({"success": True, "tran_id": tran_id})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


def printing_sales_save(request):
    return advertisement_sales_save(request)


def bank_bima_general_transaction_payment_list(request):
    return render(request, "general_transaction/payment_list.html", {
        "page_title": "Bank Bima General Transaction Payment",
        "list_title": "Bank Bima General Transaction Payment List",
        "page_id": request.GET.get("page_id") or "",
        "payment_list_url": "/general/payment/load/",
        "payment_edit_url": "/general/payment/edit/",
    })


def bank_bima_general_transaction_payment_add(request):
    fixed_location_id, fixed_location_name = get_login_location(request)
    return render(request, "general_transaction/payment.html", {
        "fixed_location_id": fixed_location_id or "",
        "fixed_location_name": fixed_location_name or "",
    })


def bank_bima_general_transaction_receive_list(request):
    return render(request, "general_transaction/receive_list.html", {
        "page_title": "Bank Bima General Transaction Receive",
    })


def bank_bima_general_transaction_receive_add(request):
    return render(request, "general_transaction/receive.html")
