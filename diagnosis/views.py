from datetime import datetime
from io import BytesIO  # #codex
import json
import traceback  # CRITICAL FIX: Explicitly imported to avoid NameError
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse  # #codex
from django.db import connection, transaction
from django.utils import timezone
from reportlab.lib import colors  # #codex
from reportlab.lib.pagesizes import A4, landscape  # #codex
from reportlab.lib.styles import getSampleStyleSheet  # #codex
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle  # #codex

from administrator.views import dictfetchall

from django.http import JsonResponse
from django.db.models import Q
from doctors.models import Doctor
from sr.models import SalesRepresentative # Apnar model framework accurate mapping check korben
from django.views.decorators.csrf import csrf_exempt

# =========================================================================
# 🛠️ CORE DICTIONARY DATA FETCH ROW WRAPPERS (RAW SQL)
# =========================================================================
def dict_fetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def dict_fetchone(cursor):
    columns = [col[0] for col in cursor.description]
    row = cursor.fetchone()
    if row:
        return dict(zip(columns, row))
    return None


DIAGNOSIS_MAIN_HEAD_ID = 10  # #codex


def referral_setup_page(request):  # #codex
    with connection.cursor() as cursor:  # #codex
        cursor.execute("""  # #codex
            SELECT id, COALESCE(custom_doc_id, CONCAT('DOC', LPAD(id, 9, '0'))) AS code, name, specialization AS meta, chamber AS extra  # #codex
            FROM doctors_info  # #codex
            WHERE is_active = 1  # #codex
            ORDER BY name ASC  # #codex
        """)  # #codex
        doctors = dict_fetchall(cursor)  # #codex
    return render(request, 'diagnosis/referral_setup.html', {  # #codex
        'providers': doctors,  # #codex
        'provider_label': 'Doctor',  # #codex
        'provider_meta_label': 'Specialization',  # #codex
        'provider_extra_label': 'Chamber',  # #codex
        'referral_tests_url': '/diagnosis/referral/tests/',  # #codex
        'referral_saved_groups_url': '/diagnosis/referral/saved-groups/',  # #codex
        'referral_save_url': '/diagnosis/referral/save/',  # #codex
        'referral_copy_url': '/diagnosis/referral/copy/',  # #codex
        'referral_success_message': 'Doctor referral setup updated successfully',  # #codex
        'referral_copy_success_message': 'Doctor referral setup copied successfully',  # #codex
    })  # #codex


def referral_sr_setup_page(request):  # #codex
    with connection.cursor() as cursor:  # #codex
        cursor.execute("""  # #codex
            SELECT id, COALESCE(custom_sr_id, CONCAT('SR', LPAD(id, 10, '0'))) AS code, name, company_name AS meta, commission_percentage AS extra  # #codex
            FROM item__sr_agents  # #codex
            WHERE is_active = 1  # #codex
            ORDER BY name ASC  # #codex
        """)  # #codex
        sr_agents = dict_fetchall(cursor)  # #codex
    return render(request, 'diagnosis/referral_setup.html', {  # #codex
        'providers': sr_agents,  # #codex
        'provider_label': 'SR',  # #codex
        'provider_meta_label': 'Company',  # #codex
        'provider_extra_label': 'Commission',  # #codex
        'referral_tests_url': '/diagnosis/referral/sr/tests/',  # #codex
        'referral_saved_groups_url': '/diagnosis/referral/sr/saved-groups/',  # #codex
        'referral_save_url': '/diagnosis/referral/sr/save/',  # #codex
        'referral_copy_url': '/diagnosis/referral/sr/copy/',  # #codex
        'referral_success_message': 'SR referral setup updated successfully',  # #codex
        'referral_copy_success_message': 'SR referral setup copied successfully',  # #codex
    })  # #codex


def referral_group_combo(request):  # #codex
    with connection.cursor() as cursor:  # #codex
        cursor.execute("""  # #codex
            SELECT id, tran_groupe_name AS name  # #codex
            FROM transaction__groupes  # #codex
            WHERE tran_groupe_type = %s AND status = 1  # #codex
            ORDER BY tran_groupe_name ASC  # #codex
        """, [DIAGNOSIS_MAIN_HEAD_ID])  # #codex
        groups = dict_fetchall(cursor)  # #codex
    return JsonResponse({'groups': groups})  # #codex


def referral_tests_by_group(request):  # #codex
    doc_id = request.GET.get('doc_id')  # #codex
    group_id = request.GET.get('group_id')  # #codex
    if not group_id:  # #codex
        return JsonResponse({'success': False, 'message': 'Group required'}, status=400)  # #codex
    with connection.cursor() as cursor:  # #codex
        cursor.execute("""  # #codex
            SELECT h.id, h.tran_head_name AS name, h.mrp,  # #codex
                   COALESCE(r.ref_type, 'tk') AS ref_type,  # #codex
                   COALESCE(r.ref_rate, 0) AS ref_rate,  # #codex
                   COALESCE(r.status, 0) AS selected  # #codex
            FROM transaction__heads h  # #codex
            LEFT JOIN referral_setup r  # #codex
              ON r.tran_head_id = h.id AND r.group_id = h.groupe_id AND r.doc_id = %s  # #codex
            WHERE h.groupe_id = %s AND h.status = 1  # #codex
            ORDER BY h.tran_head_name ASC  # #codex
        """, [doc_id or 0, group_id])  # #codex
        tests = dict_fetchall(cursor)  # #codex
    return JsonResponse({'success': True, 'tests': tests})  # #codex


def referral_saved_groups(request):  # #codex
    doc_id = request.GET.get('doc_id')  # #codex
    if not doc_id:  # #codex
        return JsonResponse({'success': False, 'message': 'Doctor required'}, status=400)  # #codex
    with connection.cursor() as cursor:  # #codex
        cursor.execute("""  # #codex
            SELECT DISTINCT r.group_id, g.tran_groupe_name AS group_name  # #codex
            FROM referral_setup r  # #codex
            JOIN transaction__groupes g ON g.id = r.group_id  # #codex
            WHERE r.doc_id = %s AND r.status = 1  # #codex
            ORDER BY g.tran_groupe_name ASC  # #codex
        """, [doc_id])  # #codex
        groups = dict_fetchall(cursor)  # #codex
    return JsonResponse({'success': True, 'groups': groups})  # #codex


def referral_sr_tests_by_group(request):  # #codex
    sr_id = request.GET.get('doc_id')  # #codex
    group_id = request.GET.get('group_id')  # #codex
    if not group_id:  # #codex
        return JsonResponse({'success': False, 'message': 'Group required'}, status=400)  # #codex
    with connection.cursor() as cursor:  # #codex
        cursor.execute("""  # #codex
            SELECT h.id, h.tran_head_name AS name, h.mrp,  # #codex
                   COALESCE(r.ref_type, 'tk') AS ref_type,  # #codex
                   COALESCE(r.ref_rate, 0) AS ref_rate,  # #codex
                   COALESCE(r.status, 0) AS selected  # #codex
            FROM transaction__heads h  # #codex
            LEFT JOIN referral_setup_sr r  # #codex
              ON r.tran_head_id = h.id AND r.group_id = h.groupe_id AND r.sr_id = %s  # #codex
            WHERE h.groupe_id = %s AND h.status = 1  # #codex
            ORDER BY h.tran_head_name ASC  # #codex
        """, [sr_id or '', group_id])  # #codex
        tests = dict_fetchall(cursor)  # #codex
    return JsonResponse({'success': True, 'tests': tests})  # #codex


def referral_sr_saved_groups(request):  # #codex
    sr_id = request.GET.get('doc_id')  # #codex
    if not sr_id:  # #codex
        return JsonResponse({'success': False, 'message': 'SR required'}, status=400)  # #codex
    with connection.cursor() as cursor:  # #codex
        cursor.execute("""  # #codex
            SELECT DISTINCT r.group_id, g.tran_groupe_name AS group_name  # #codex
            FROM referral_setup_sr r  # #codex
            JOIN transaction__groupes g ON g.id = r.group_id  # #codex
            WHERE r.sr_id = %s AND r.status = 1  # #codex
            ORDER BY g.tran_groupe_name ASC  # #codex
        """, [sr_id])  # #codex
        groups = dict_fetchall(cursor)  # #codex
    return JsonResponse({'success': True, 'groups': groups})  # #codex


@csrf_exempt  # #codex
def save_referral_setup(request):  # #codex
    if request.method != "POST":  # #codex
        return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)  # #codex
    try:  # #codex
        payload = json.loads(request.body.decode('utf-8') or '{}')  # #codex
        doc_id = payload.get('doc_id')  # #codex
        group_id = payload.get('group_id')  # #codex
        rows = payload.get('rows', [])  # #codex
        if not doc_id or not group_id:  # #codex
            return JsonResponse({'success': False, 'message': 'Doctor and group required'}, status=400)  # #codex
        with transaction.atomic():  # #codex
            with connection.cursor() as cursor:  # #codex
                cursor.execute("UPDATE referral_setup SET status = 0 WHERE doc_id = %s AND group_id = %s", [doc_id, group_id])  # #codex
                for row in rows:  # #codex
                    tran_head_id = row.get('tran_head_id')  # #codex
                    ref_type = row.get('ref_type') if row.get('ref_type') in ['tk', 'percent'] else 'tk'  # #codex
                    ref_rate = row.get('ref_rate') or 0  # #codex
                    status = 1 if row.get('selected') else 0  # #codex
                    if not tran_head_id:  # #codex
                        continue  # #codex
                    cursor.execute("""  # #codex
                        INSERT INTO referral_setup (doc_id, group_id, tran_head_id, ref_type, ref_rate, status)  # #codex
                        VALUES (%s, %s, %s, %s, %s, %s)  # #codex
                        ON DUPLICATE KEY UPDATE ref_type = VALUES(ref_type), ref_rate = VALUES(ref_rate), status = VALUES(status)  # #codex
                    """, [doc_id, group_id, tran_head_id, ref_type, ref_rate, status])  # #codex
        return JsonResponse({'success': True})  # #codex
    except Exception as exc:  # #codex
        traceback.print_exc()  # #codex
        return JsonResponse({'success': False, 'message': str(exc)}, status=400)  # #codex


@csrf_exempt  # #codex
def copy_referral_setup(request):  # #codex
    if request.method != "POST":  # #codex
        return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)  # #codex
    try:  # #codex
        payload = json.loads(request.body.decode('utf-8') or '{}')  # #codex
        source_doc_id = payload.get('source_doc_id')  # #codex
        target_doc_id = payload.get('target_doc_id')  # #codex
        if not source_doc_id or not target_doc_id or str(source_doc_id) == str(target_doc_id):  # #codex
            return JsonResponse({'success': False, 'message': 'Valid source and target doctor required'}, status=400)  # #codex
        with transaction.atomic():  # #codex
            with connection.cursor() as cursor:  # #codex
                cursor.execute("UPDATE referral_setup SET status = 0 WHERE doc_id = %s", [target_doc_id])  # #codex
                cursor.execute("""  # #codex
                    INSERT INTO referral_setup (doc_id, group_id, tran_head_id, ref_type, ref_rate, status)  # #codex
                    SELECT %s, group_id, tran_head_id, ref_type, ref_rate, status  # #codex
                    FROM referral_setup  # #codex
                    WHERE doc_id = %s AND status = 1  # #codex
                    ON DUPLICATE KEY UPDATE ref_type = VALUES(ref_type), ref_rate = VALUES(ref_rate), status = VALUES(status)  # #codex
                """, [target_doc_id, source_doc_id])  # #codex
        return JsonResponse({'success': True})  # #codex
    except Exception as exc:  # #codex
        traceback.print_exc()  # #codex
        return JsonResponse({'success': False, 'message': str(exc)}, status=400)  # #codex


@csrf_exempt  # #codex
def save_referral_sr_setup(request):  # #codex
    if request.method != "POST":  # #codex
        return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)  # #codex
    try:  # #codex
        payload = json.loads(request.body.decode('utf-8') or '{}')  # #codex
        sr_id = payload.get('doc_id')  # #codex
        group_id = payload.get('group_id')  # #codex
        rows = payload.get('rows', [])  # #codex
        if not sr_id or not group_id:  # #codex
            return JsonResponse({'success': False, 'message': 'SR and group required'}, status=400)  # #codex
        with transaction.atomic():  # #codex
            with connection.cursor() as cursor:  # #codex
                cursor.execute("UPDATE referral_setup_sr SET status = 0 WHERE sr_id = %s AND group_id = %s", [sr_id, group_id])  # #codex
                for row in rows:  # #codex
                    tran_head_id = row.get('tran_head_id')  # #codex
                    ref_type = row.get('ref_type') if row.get('ref_type') in ['tk', 'percent'] else 'tk'  # #codex
                    ref_rate = row.get('ref_rate') or 0  # #codex
                    status = 1 if row.get('selected') else 0  # #codex
                    if not tran_head_id:  # #codex
                        continue  # #codex
                    cursor.execute("""  # #codex
                        INSERT INTO referral_setup_sr (sr_id, group_id, tran_head_id, ref_type, ref_rate, status)  # #codex
                        VALUES (%s, %s, %s, %s, %s, %s)  # #codex
                        ON DUPLICATE KEY UPDATE ref_type = VALUES(ref_type), ref_rate = VALUES(ref_rate), status = VALUES(status)  # #codex
                    """, [sr_id, group_id, tran_head_id, ref_type, ref_rate, status])  # #codex
        return JsonResponse({'success': True})  # #codex
    except Exception as exc:  # #codex
        traceback.print_exc()  # #codex
        return JsonResponse({'success': False, 'message': str(exc)}, status=400)  # #codex


@csrf_exempt  # #codex
def copy_referral_sr_setup(request):  # #codex
    if request.method != "POST":  # #codex
        return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)  # #codex
    try:  # #codex
        payload = json.loads(request.body.decode('utf-8') or '{}')  # #codex
        source_sr_id = payload.get('source_doc_id')  # #codex
        target_sr_id = payload.get('target_doc_id')  # #codex
        if not source_sr_id or not target_sr_id or str(source_sr_id) == str(target_sr_id):  # #codex
            return JsonResponse({'success': False, 'message': 'Valid source and target SR required'}, status=400)  # #codex
        with transaction.atomic():  # #codex
            with connection.cursor() as cursor:  # #codex
                cursor.execute("UPDATE referral_setup_sr SET status = 0 WHERE sr_id = %s", [target_sr_id])  # #codex
                cursor.execute("""  # #codex
                    INSERT INTO referral_setup_sr (sr_id, group_id, tran_head_id, ref_type, ref_rate, status)  # #codex
                    SELECT %s, group_id, tran_head_id, ref_type, ref_rate, status  # #codex
                    FROM referral_setup_sr  # #codex
                    WHERE sr_id = %s AND status = 1  # #codex
                    ON DUPLICATE KEY UPDATE ref_type = VALUES(ref_type), ref_rate = VALUES(ref_rate), status = VALUES(status)  # #codex
                """, [target_sr_id, source_sr_id])  # #codex
        return JsonResponse({'success': True})  # #codex
    except Exception as exc:  # #codex
        traceback.print_exc()  # #codex
        return JsonResponse({'success': False, 'message': str(exc)}, status=400)  # #codex


def referral_report_page(request):  # #codex
    return render(request, 'diagnosis/referral_report.html')  # #codex


def referral_report_providers(request):  # #codex
    report_type = request.GET.get('report_type')  # #codex
    if report_type == 'sr':  # #codex
        sql = """  # #codex
            SELECT COALESCE(custom_sr_id, CONCAT('SR', LPAD(id, 10, '0'))) AS code, name  # #codex
            FROM item__sr_agents WHERE is_active = 1 ORDER BY name ASC  # #codex
        """  # #codex
    else:  # #codex
        sql = """  # #codex
            SELECT COALESCE(custom_doc_id, CONCAT('DOC', LPAD(id, 9, '0'))) AS code, name  # #codex
            FROM doctors_info WHERE is_active = 1 ORDER BY name ASC  # #codex
        """  # #codex
    with connection.cursor() as cursor:  # #codex
        cursor.execute(sql)  # #codex
        providers = dict_fetchall(cursor)  # #codex
    return JsonResponse({'success': True, 'providers': providers})  # #codex


def _referral_report_rows(report_type, provider_id, start_date, end_date):  # #codex
    setup_table = 'referral_setup_sr' if report_type == 'sr' else 'referral_setup'  # #codex
    provider_column = 'td.sr_id' if report_type == 'sr' else 'td.doctor_id'  # #codex
    setup_provider_column = 'rs.sr_id' if report_type == 'sr' else 'rs.doc_id'  # #codex

    with connection.cursor() as cursor:  # #codex
        cursor.execute(f"""  # #codex
            SELECT  # #codex
                td.tran_id, DATE(td.tran_date) AS tran_date, COALESCE(td.tran_groupe_id, th.groupe_id) AS group_id,  # #codex
                COALESCE(tg.tran_groupe_name, '-') AS group_name,  # #codex
                th.tran_head_name, COALESCE(td.mrp, td.amount, 0) AS test_tk,  # #codex
                COALESCE(td.discount, 0) AS discount, COALESCE(rs.ref_type, '-') AS ref_type,  # #codex
                COALESCE(rs.ref_rate, 0) AS ref_rate,  # #codex
                CASE  # #codex
                    WHEN rs.ref_type = 'percent' THEN ROUND((COALESCE(td.mrp, td.amount, 0) * COALESCE(rs.ref_rate, 0)) / 100, 2)  # #codex
                    WHEN rs.ref_type = 'tk' THEN ROUND(COALESCE(rs.ref_rate, 0), 2)  # #codex
                    ELSE 0  # #codex
                END AS referral_amount  # #codex
            FROM transaction__details td  # #codex
            LEFT JOIN transaction__mains tm ON tm.tran_id = td.tran_id  # #codex
            LEFT JOIN transaction__heads th ON th.id = td.tran_head_id  # #codex
            LEFT JOIN transaction__groupes tg ON tg.id = COALESCE(td.tran_groupe_id, th.groupe_id)  # #codex
            LEFT JOIN {setup_table} rs ON {setup_provider_column} = {provider_column}  # #codex
                AND rs.group_id = COALESCE(td.tran_groupe_id, th.groupe_id)  # #codex
                AND rs.tran_head_id = td.tran_head_id  # #codex
                AND rs.status = 1  # #codex
            WHERE td.tran_type = %s  # #codex
              AND {provider_column} = %s  # #codex
              AND DATE(td.tran_date) BETWEEN %s AND %s  # #codex
              AND td.status = 1  # #codex
              AND COALESCE(td.due, 0) = 0  # #codex
              AND COALESCE(tm.due, 0) = 0  # #codex
            ORDER BY td.tran_date ASC, td.tran_id ASC  # #codex
        """, [DIAGNOSIS_MAIN_HEAD_ID, provider_id, start_date, end_date])  # #codex
        rows = dict_fetchall(cursor)  # #codex
    return rows  # #codex


def _referral_report_totals(rows):  # #codex
    return {  # #codex
        'total_referral': sum(float(row.get('referral_amount') or 0) for row in rows),  # #codex
        'total_test_tk': sum(float(row.get('test_tk') or 0) for row in rows),  # #codex
        'total_discount': sum(float(row.get('discount') or 0) for row in rows),  # #codex
    }  # #codex


def _referral_provider_name(report_type, provider_id):  # #codex
    if report_type == 'sr':  # #codex
        sql = "SELECT name FROM item__sr_agents WHERE COALESCE(custom_sr_id, CONCAT('SR', LPAD(id, 10, '0'))) = %s LIMIT 1"  # #codex
    else:  # #codex
        sql = "SELECT name FROM doctors_info WHERE COALESCE(custom_doc_id, CONCAT('DOC', LPAD(id, 9, '0'))) = %s LIMIT 1"  # #codex
    with connection.cursor() as cursor:  # #codex
        cursor.execute(sql, [provider_id])  # #codex
        row = cursor.fetchone()  # #codex
    return row[0] if row else '-'  # #codex


def referral_report_data(request):  # #codex
    report_type = request.GET.get('report_type') or 'doctor'  # #codex
    provider_id = request.GET.get('provider_id')  # #codex
    start_date = request.GET.get('start_date')  # #codex
    end_date = request.GET.get('end_date')  # #codex
    if not provider_id or not start_date or not end_date:  # #codex
        return JsonResponse({'success': False, 'message': 'Report type, provider, start date and end date required'}, status=400)  # #codex

    rows = _referral_report_rows(report_type, provider_id, start_date, end_date)  # #codex
    totals = _referral_report_totals(rows)  # #codex
    return JsonResponse({'success': True, 'rows': rows, **totals})  # #codex


def referral_report_pdf(request):  # #codex
    report_type = request.GET.get('report_type') or 'doctor'  # #codex
    provider_id = request.GET.get('provider_id')  # #codex
    start_date = request.GET.get('start_date')  # #codex
    end_date = request.GET.get('end_date')  # #codex
    if not provider_id or not start_date or not end_date:  # #codex
        return HttpResponse("Report type, provider, start date and end date required", status=400)  # #codex
    rows = _referral_report_rows(report_type, provider_id, start_date, end_date)  # #codex
    totals = _referral_report_totals(rows)  # #codex
    provider_label = 'SR' if report_type == 'sr' else 'Doctor'  # #codex
    provider_name = _referral_provider_name(report_type, provider_id)  # #codex
    buffer = BytesIO()  # #codex
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), rightMargin=18, leftMargin=18, topMargin=22, bottomMargin=22)  # #codex
    styles = getSampleStyleSheet()  # #codex
    elements = []  # #codex
    elements.append(Paragraph("Diagnosis Referral Report", styles["Title"]))  # #codex
    elements.append(Paragraph(f"<b>Report Type:</b> {provider_label} &nbsp;&nbsp; <b>{provider_label}:</b> {provider_id} - {provider_name}", styles["Normal"]))  # #codex
    elements.append(Paragraph(f"<b>Start Date:</b> {start_date} &nbsp;&nbsp; <b>End Date:</b> {end_date}", styles["Normal"]))  # #codex
    elements.append(Spacer(1, 10))  # #codex
    table_data = [["SL", "Tran ID", "Date", "Group Name", "Tran Head", "Test Tk", "Discount", "Ref Type", "Ref Rate", "Referral"]]  # #codex
    for index, row in enumerate(rows, 1):  # #codex
        table_data.append([  # #codex
            index,  # #codex
            row.get('tran_id') or '-',  # #codex
            str(row.get('tran_date') or '-'),  # #codex
            row.get('group_name') or '-',  # #codex
            Paragraph(str(row.get('tran_head_name') or '-'), styles["BodyText"]),  # #codex
            f"{float(row.get('test_tk') or 0):.2f}",  # #codex
            f"{float(row.get('discount') or 0):.2f}",  # #codex
            row.get('ref_type') or '-',  # #codex
            f"{float(row.get('ref_rate') or 0):.2f}",  # #codex
            f"{float(row.get('referral_amount') or 0):.2f}",  # #codex
        ])  # #codex
    table_data.append(["", "", "", "", "Total", f"{totals['total_test_tk']:.2f}", f"{totals['total_discount']:.2f}", "", "", f"{totals['total_referral']:.2f}"])  # #codex
    table = Table(table_data, colWidths=[28, 82, 58, 78, 149, 58, 58, 55, 55, 60], repeatRows=1)  # #codex
    table.setStyle(TableStyle([  # #codex
        ('GRID', (0, 0), (-1, -1), 0.4, colors.black),  # #codex
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1f2327")),  # #codex
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),  # #codex
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#f1f3f5")),  # #codex
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),  # #codex
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # #codex
        ('ALIGN', (5, 1), (6, -1), 'RIGHT'),  # #codex
        ('ALIGN', (8, 1), (9, -1), 'RIGHT'),  # #codex
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # #codex
        ('FONTSIZE', (0, 0), (-1, -1), 8),  # #codex
    ]))  # #codex
    elements.append(table)  # #codex
    doc.build(elements)  # #codex
    buffer.seek(0)  # #codex
    response = HttpResponse(buffer, content_type="application/pdf")  # #codex
    response["Content-Disposition"] = 'attachment; filename="diagnosis_referral_report.pdf"'  # #codex
    return response  # #codex

def product_search(request):
    q = request.GET.get('q', '').strip()
    offset = int(request.GET.get('offset', 0))
    tran_main_head_id = request.GET.get('tran_main_head_id').strip()
    tran_group_id = request.GET.get('tran_group_id')
    limit = 10

    print (tran_main_head_id);
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
            ORDER BY t.id ASC
            LIMIT %s OFFSET %s
        """
        # AND tg.id = %s
        # params = [f"{q}%", tran_main_head_id, tran_group_id, limit, offset]
        params = [f"{q}%", tran_main_head_id, limit, offset]
    
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
            ORDER BY t.id ASC
            LIMIT %s OFFSET %s
        """
        # AND tg.id = %s
        # params = [tran_main_head_id, tran_group_id, limit, offset]
        params = [tran_main_head_id, limit, offset]


    cursor.execute(sql, params)
    data = dictfetchall(cursor)

    return JsonResponse({'results': data})
# =========================================================================
# 📋 1. PATIENT MAIN LISTING GATEWAY VIEW (HTML VIEW 1)
# =========================================================================
def patient_list_view(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM patient_info ORDER BY id DESC")
        patients = dict_fetchall(cursor)
    return render(request, 'diagnosis/patient_list.html', {'patients': patients})


# =========================================================================
# 📝 2. SPLIT ENTRY & EDIT WORKSPACE VIEW (HTML VIEW 2)
# =========================================================================
def patient_form_view(request, pk=None):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM patient_info ORDER BY id DESC")
        patients = dict_fetchall(cursor)
    return render(request, 'diagnosis/patient_form.html', {
        'patients': patients,
        'edit_id': pk
    })


# =========================================================================
# 🔍 3. FETCH SINGLE PATIENT PROFILE ENGINE (AJAX GET)
# =========================================================================
def fetch_patient(request):
    patient_id = request.GET.get('id')
    if not patient_id:
        return JsonResponse({'error': 'Missing target context ID'}, status=400)
        
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM patient_info WHERE id = %s", [patient_id])
        patient = dict_fetchone(cursor)
        
    if patient:
        if patient.get('dob'):
            patient['dob'] = patient['dob'].strftime('%Y-%m-%d')
        return JsonResponse(patient)
    return JsonResponse({'error': 'Target patient records not found'}, status=404)


# =========================================================================
# 💾 4. STORE NEW PATIENT DATA ARCHITECTURE (AJAX POST)
# =========================================================================
def store_patient(request):
    if request.method != "POST":
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)
        
    try:
        data = request.POST
        current_now = timezone.now()

        with transaction.atomic():
            with connection.cursor() as cursor:
                
                # --- STEP A: DYNAMIC LOOKUP WITH MULTIPLE MATCHING OPTIONS ---
                # Search directly by specific name 'Diagnosis Patients' or 'Diagnosis' head
                cursor.execute("""
                    SELECT id, tran_method, user_role 
                    FROM transaction__withs 
                    WHERE (LOWER(tran_with_name) LIKE '%%diagnosis patients%%' 
                       OR LOWER(tran_with_name) LIKE '%%diagnosis%%') 
                       AND tran_type = 10 
                    LIMIT 1
                """)
                tran_with_meta = cursor.fetchone()
                
                if tran_with_meta:
                    tran_with_id_val = tran_with_meta[0]
                    extracted_tran_method = tran_with_meta[1] if tran_with_meta[1] is not None else "0"
                    # CRITICAL FIX: Ensure user_role from DB isn't Null, fallback to 4
                    extracted_user_role = tran_with_meta[2] if tran_with_meta[2] is not None else 4
                else:
                    # STRICT FALLBACK SAFETIES: If no rows matching in DB table yet
                    tran_with_id_val = None
                    extracted_tran_method = "0"
                    extracted_user_role = 4

                # --- STEP B: UNIQUE PATIENT ID (DP SEQUENCE) GENERATION ---
                cursor.execute("SELECT user_id FROM user__infos WHERE user_id LIKE 'DP%%' ORDER BY user_id DESC LIMIT 1")
                last_user = cursor.fetchone()
                
                if last_user and last_user[0]:
                    last_number = int(last_user[0][2:])
                    new_number = last_number + 1
                else:
                    new_number = 1
                generated_user_id = f"DP{new_number:09d}"

                # --- STEP C: INSERT INTO USER__INFOS ---
                user_sql = """
                    INSERT INTO user__infos (
                        user_id, user_name, user_email, user_phone, gender, dob, 
                        nationality, religion, address, passport, user_role, status, 
                        tran_with_id, tran_method, added_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(user_sql, [
                    generated_user_id, 
                    data.get('patient_name'), 
                    data.get('present_email') or None,
                    data.get('present_mobile') or None, 
                    data.get('gender') or None, 
                    data.get('dob') or None,
                    data.get('nationality') or None, 
                    data.get('religion') or None, 
                    data.get('present_address') or None,
                    data.get('passport_no') or None, 
                    extracted_user_role, # Guarantees non-null int 4 fallback
                    1,                   # Status active
                    tran_with_id_val,  
                    extracted_tran_method,
                    current_now
                ])

                # --- STEP D: INSERT INTO PRIMARY patient_info SCHEMA ---
                patient_sql = """
                    INSERT INTO patient_info (
                        patient_name, father_husband_name, mother_name, parent_spouse_name, dob, age,
                        gender, marital_status, nationality, passport_no, blood_group, country_of_birth,
                        religion, occupation, weight, height, bmi, cause_visit_dcc, referral_source,
                        referred_by, consulted_doctor, doctor_name, clinic_name, daily_routine, daily_diet,
                        food_preferences, avoid_foods, diagnostic_reports, physical_condition, family_history,
                        family_relation, physical_activity, diet, present_address, present_mobile, present_email,
                        permanent_address, permanent_mobile, permanent_email, emergency_name, emergency_relation,
                        emergency_phone, patient_signature, user_info_id, created_at, updated_at
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s
                    )
                """
                cursor.execute(patient_sql, [
                    data.get('patient_name'), data.get('father_husband_name') or None, data.get('mother_name') or None,
                    data.get('parent_spouse_name') or None, data.get('dob') or None, data.get('age') or None,
                    data.get('gender') or None, data.get('marital_status') or None, data.get('nationality') or None,
                    data.get('passport_no') or None, data.get('blood_group') or None, data.get('country_of_birth') or None,
                    data.get('religion') or None, data.get('occupation') or None, data.get('weight') or None,
                    data.get('height') or None, data.get('bmi') or None, data.get('cause_visit_dcc') or None,
                    data.get('referral_source') or None, data.get('referred_by') or None, data.get('consulted_doctor') or None,
                    data.get('doctor_name') or None, data.get('clinic_name') or None, data.get('daily_routine') or None,
                    data.get('daily_diet') or None, data.get('food_preferences') or None, data.get('avoid_foods') or None,
                    data.get('diagnostic_reports') or None, data.get('physical_condition') or None, data.get('family_history') or None,
                    data.get('family_relation') or None, data.get('physical_activity') or None, data.get('diet') or None,
                    data.get('present_address') or None, data.get('present_mobile') or None, data.get('present_email') or None,
                    data.get('permanent_address') or None, data.get('permanent_mobile') or None, data.get('permanent_email') or None,
                    data.get('emergency_name') or None, data.get('emergency_relation') or None, data.get('emergency_phone') or None,
                    data.get('patient_signature') or None, generated_user_id, current_now, current_now
                ])
                
                return JsonResponse({'success': True, 'id': cursor.lastrowid})
                
    except Exception as e:
        print("========!!! COREDATA CRASH TRACEBACK !!!========")
        traceback.print_exc()
        print("================================================")
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


# =========================================================================
# 🔄 5. UPDATE EXISTING PATIENT WORKFLOWS (AJAX POST)
# =========================================================================
def update_patient(request, pk):
    if request.method != "POST":
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)
        
    try:
        data = request.POST
        current_now = timezone.now()

        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("SELECT user_info_id FROM patient_info WHERE id = %s", [pk])
                current_patient = cursor.fetchone()
                if not current_patient:
                    return JsonResponse({'success': False, 'error': 'Patient profile not found'}, status=404)
                
                user_info_id = current_patient[0]

                # Update primary table data
                update_patient_sql = """
                    UPDATE patient_info SET 
                        patient_name=%s, father_husband_name=%s, mother_name=%s, parent_spouse_name=%s, dob=%s, age=%s,
                        gender=%s, marital_status=%s, nationality=%s, passport_no=%s, blood_group=%s, country_of_birth=%s,
                        religion=%s, occupation=%s, weight=%s, height=%s, bmi=%s, cause_visit_dcc=%s, referral_source=%s,
                        referred_by=%s, consulted_doctor=%s, doctor_name=%s, clinic_name=%s, daily_routine=%s, daily_diet=%s,
                        food_preferences=%s, avoid_foods=%s, diagnostic_reports=%s, physical_condition=%s, family_history=%s,
                        family_relation=%s, physical_activity=%s, diet=%s, present_address=%s, present_mobile=%s, present_email=%s,
                        permanent_address=%s, permanent_mobile=%s, permanent_email=%s, emergency_name=%s, emergency_relation=%s,
                        emergency_phone=%s, patient_signature=%s, updated_at=%s
                    WHERE id = %s
                """
                cursor.execute(update_patient_sql, [
                    data.get('patient_name'), data.get('father_husband_name') or None, data.get('mother_name') or None,
                    data.get('parent_spouse_name') or None, data.get('dob') or None, data.get('age') or None,
                    data.get('gender') or None, data.get('marital_status') or None, data.get('nationality') or None,
                    data.get('passport_no') or None, data.get('blood_group') or None, data.get('country_of_birth') or None,
                    data.get('religion') or None, data.get('occupation') or None, data.get('weight') or None,
                    data.get('height') or None, data.get('bmi') or None, data.get('cause_visit_dcc') or None,
                    data.get('referral_source') or None, data.get('referred_by') or None, data.get('consulted_doctor') or None,
                    data.get('doctor_name') or None, data.get('clinic_name') or None, data.get('daily_routine') or None,
                    data.get('daily_diet') or None, data.get('food_preferences') or None, data.get('avoid_foods') or None,
                    data.get('diagnostic_reports') or None, data.get('physical_condition') or None, data.get('family_history') or None,
                    data.get('family_relation') or None, data.get('physical_activity') or None, data.get('diet') or None,
                    data.get('present_address') or None, data.get('present_mobile') or None, data.get('present_email') or None,
                    data.get('permanent_address') or None, data.get('permanent_mobile') or None, data.get('permanent_email') or None,
                    data.get('emergency_name') or None, data.get('emergency_relation') or None, data.get('emergency_phone') or None,
                    data.get('patient_signature') or None, current_now, pk
                ])

                # Sync modification details inside user__infos context reference
                if user_info_id:
                    cursor.execute("""
                        SELECT id FROM transaction__withs 
                        WHERE LOWER(tran_with_name) LIKE '%%diagnosis%%' AND tran_type = 10 LIMIT 1
                    """)
                    u_with = cursor.fetchone()
                    u_with_id = u_with[0] if u_with else None

                    update_user_sql = """
                        UPDATE user__infos SET 
                            user_name=%s, user_email=%s, user_phone=%s, gender=%s, dob=%s, 
                            nationality=%s, religion=%s, address=%s, passport=%s, tran_with_id=%s, updated_at=%s
                        WHERE user_id = %s
                    """
                    cursor.execute(update_user_sql, [
                        data.get('patient_name'), data.get('present_email') or None, data.get('present_mobile') or None,
                        data.get('gender') or None, data.get('dob') or None, data.get('nationality') or None,
                        data.get('religion') or None, data.get('present_address') or None, data.get('passport_no') or None,
                        u_with_id, current_now, user_info_id
                    ])

                return JsonResponse({'success': True})
                
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


# =========================================================================
# ❌ 6. CRITICAL DELETE SYSTEM PIPELINE (AJAX POST)
# =========================================================================
def delete_patient(request, pk):
    if request.method != "POST":
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)
    try:
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("SELECT user_info_id FROM patient_info WHERE id = %s", [pk])
                row = cursor.fetchone()
                if row:
                    user_info_id = row[0]
                    cursor.execute("DELETE FROM patient_info WHERE id = %s", [pk])
                    if user_info_id:
                        cursor.execute("DELETE FROM user__infos WHERE user_id = %s", [user_info_id])
                return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
    

    from django.http import JsonResponse
from django.db import connection





def autocomplete_doctor(request):
    """🧠 Optimised Real-time Select2 autocomplete mapping using physical custom column"""
    q = request.GET.get('term', request.GET.get('q', '')).strip()
    with connection.cursor() as cursor:
        sql = """
            SELECT id, custom_doc_id, name, specialization, chamber 
            FROM doctors_info 
            WHERE name LIKE %s OR custom_doc_id LIKE %s
            LIMIT 20;
        """
        cursor.execute(sql, [f"%{q}%", f"%{q}%"])
        columns = [col[0] for col in cursor.description]
        raw_data = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    # 🔥 Direct extraction alignment from physical custom data string field container!
    results = [{
        'id': row['id'],
        'text': f"{row['custom_doc_id']} - {row['name']}",
        'speciality': row['specialization'] or 'General',
        'chamber': row['chamber'] or 'N/A'
    } for row in raw_data]
    
    return JsonResponse({"results": results}, safe=False)

# sr/views.py inside autocomplete_sr data object manipulation routing map handler:
def autocomplete_sr(request):
    """🧠 Optimised Real-time Select2 autocomplete mapping targeting physical custom code identity metrics"""
    q = request.GET.get('term', request.GET.get('q', '')).strip()
    
    with connection.cursor() as cursor:
        # 🔥 FIX: Query constraint array parsing variables values logic mapping structure 
        # Checking string tracking columns name matching exact parameters matching format structure:
        sql = """
            SELECT id, custom_sr_id, name 
            FROM item__sr_agents 
            WHERE (name LIKE %s OR custom_sr_id LIKE %s) 
              AND is_active = 1
            LIMIT 20;
        """
        # Exact string query character sequences boundary map criteria conditions checking arrays
        cursor.execute(sql, [f"%{q}%", f"%{q}%"])
        
        columns = [col[0] for col in cursor.description]
        raw_data = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
    results = [{
        'id': row['id'],
        'text': f"{row['custom_sr_id']} - {row['name']}",
        'name_display': row['name']
    } for row in raw_data]
    
    return JsonResponse({"results": results}, safe=False)





