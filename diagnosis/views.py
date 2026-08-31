from datetime import datetime
from io import BytesIO  # #codex
import json
import traceback  # CRITICAL FIX: Explicitly imported to avoid NameError
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse  # #codex
from django.db import connection, transaction
from django.utils import timezone
from django.utils.html import escape  # #codex
from reportlab.lib import colors  # #codex
from reportlab.lib.pagesizes import A4, landscape  # #codex
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet  # #codex
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle  # #codex
from reportlab.lib.units import inch  # #codex
from reportlab.lib.enums import TA_CENTER  # #codex
from reportlab.graphics.barcode import code128  # #codex
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

    if not tran_group_id:
        return JsonResponse({'results': []})

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
                c.name AS category_name,
                t.quantity,
                t.mrp
            FROM transaction__heads t
            JOIN transaction__groupes tg ON t.groupe_id = tg.id
            JOIN transaction__main__heads tmh ON tmh.id = tg.tran_groupe_type
            LEFT JOIN item__manufacturers m ON t.manufacturer_id = m.id
            LEFT JOIN item__forms f ON t.form_id = f.id
            LEFT JOIN transaction__category c ON t.category_id = c.id
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
                c.name AS category_name,
                t.quantity,
                t.mrp
            FROM transaction__heads t
            JOIN transaction__groupes tg ON t.groupe_id = tg.id
            JOIN transaction__main__heads tmh ON tmh.id = tg.tran_groupe_type
            LEFT JOIN item__manufacturers m ON t.manufacturer_id = m.id
            LEFT JOIN item__forms f ON t.form_id = f.id
            LEFT JOIN transaction__category c ON t.category_id = c.id
            WHERE tmh.id = %s
            AND tg.id = %s
            ORDER BY t.id ASC
            LIMIT %s OFFSET %s
        """
        params = [tran_main_head_id, tran_group_id, limit, offset]


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


# lab report generation


def ensure_lab_parameters_table():  # #codex
    with connection.cursor() as cursor:  # #codex
        cursor.execute("""  # #codex
            CREATE TABLE IF NOT EXISTS lab_parameters (  # #codex
                id BIGINT AUTO_INCREMENT PRIMARY KEY,  # #codex
                group_id BIGINT NOT NULL,  # #codex
                category_id BIGINT NOT NULL,  # #codex
                head_id BIGINT NULL,  # #codex
                serial INT NOT NULL DEFAULT 0,  # #codex
                title VARCHAR(255) NOT NULL,  # #codex
                title_code VARCHAR(100) NULL,  # #codex
                investigation VARCHAR(255) NOT NULL,  # #codex
                investigation_code VARCHAR(100) NULL,  # #codex
                unit VARCHAR(100) NULL,  # #codex
                reff_range TEXT NULL,  # #codex
                added_at DATETIME NULL,  # #codex
                updated_at DATETIME NULL,  # #codex
                INDEX idx_lab_parameters_group (group_id),  # #codex
                INDEX idx_lab_parameters_category (category_id),  # #codex
                INDEX idx_lab_parameters_head (head_id)  # #codex
            )  # #codex
        """)  # #codex
        cursor.execute("ALTER TABLE lab_parameters ADD COLUMN IF NOT EXISTS title_code VARCHAR(100) NULL AFTER title")  # #codex
        cursor.execute("ALTER TABLE lab_parameters ADD COLUMN IF NOT EXISTS investigation_code VARCHAR(100) NULL AFTER investigation")  # #codex
        cursor.execute("""  # #codex
            CREATE TABLE IF NOT EXISTS lab_results (  # #codex
                id BIGINT AUTO_INCREMENT PRIMARY KEY,  # #codex
                invoice_id BIGINT NOT NULL,  # #codex
                group_id BIGINT NOT NULL,  # #codex
                category_id BIGINT NOT NULL,  # #codex
                head_id BIGINT NULL,  # #codex
                serial INT NOT NULL DEFAULT 0,  # #codex
                title VARCHAR(255) NOT NULL,  # #codex
                title_code VARCHAR(100) NULL,  # #codex
                investigation VARCHAR(255) NOT NULL,  # #codex
                investigation_code VARCHAR(100) NULL,  # #codex
                unit VARCHAR(100) NULL,  # #codex
                reff_range TEXT NULL,  # #codex
                result TEXT NULL,  # #codex
                added_at DATETIME NULL,  # #codex
                updated_at DATETIME NULL,  # #codex
                INDEX idx_lab_results_invoice (invoice_id),  # #codex
                INDEX idx_lab_results_category (category_id),  # #codex
                INDEX idx_lab_results_head (head_id)  # #codex
            )  # #codex
        """)  # #codex
        cursor.execute("ALTER TABLE lab_results ADD COLUMN IF NOT EXISTS selected_test_ids TEXT NULL AFTER invoice_id")  # #codex
        cursor.execute("ALTER TABLE lab_results ADD COLUMN IF NOT EXISTS selected_test_names TEXT NULL AFTER selected_test_ids")  # #codex


def _optional_int(value):  # #codex
    return int(value) if str(value or '').strip() else None  # #codex


def _positive_int(value, default=1):  # #codex
    try:  # #codex
        parsed = int(value)  # #codex
        return parsed if parsed > 0 else default  # #codex
    except (TypeError, ValueError):  # #codex
        return default  # #codex


def normalize_lab_parameter_serials(group_id, category_id, preferred_id=None, preferred_serial=None):  # #codex
    desired_serial = _positive_int(preferred_serial, 1)  # #codex
    with connection.cursor() as cursor:  # #codex
        cursor.execute("""  # #codex
            SELECT id, serial  # #codex
            FROM lab_parameters  # #codex
            WHERE group_id = %s AND category_id = %s  # #codex
            ORDER BY serial ASC, id ASC  # #codex
        """, [group_id, category_id])  # #codex
        rows = [{'id': row[0], 'serial': row[1]} for row in cursor.fetchall()]  # #codex
        target_row = None  # #codex
        other_rows = []  # #codex
        for row in rows:  # #codex
            if preferred_id and str(row['id']) == str(preferred_id):  # #codex
                target_row = row  # #codex
            else:  # #codex
                other_rows.append(row)  # #codex
        if target_row:  # #codex
            insert_index = max(0, min(desired_serial - 1, len(other_rows)))  # #codex
            ordered_rows = other_rows[:insert_index] + [target_row] + other_rows[insert_index:]  # #codex
        else:  # #codex
            ordered_rows = other_rows  # #codex
        for index, row in enumerate(ordered_rows, start=1):  # #codex
            cursor.execute("UPDATE lab_parameters SET serial = %s WHERE id = %s", [index, row['id']])  # #codex


def lab_parameter_setup_page(request):  # #codex
    ensure_lab_parameters_table()  # #codex
    with connection.cursor() as cursor:  # #codex
        cursor.execute("""  # #codex
            SELECT id, tran_groupe_name AS name  # #codex
            FROM transaction__groupes  # #codex
            WHERE tran_groupe_type = %s AND status = 1  # #codex
            ORDER BY tran_groupe_name ASC  # #codex
        """, [DIAGNOSIS_MAIN_HEAD_ID])  # #codex
        groups = dict_fetchall(cursor)  # #codex
    return render(request, 'diagnosis/lab_parameter_setup.html', {  # #codex
        'groups': groups,  # #codex
    })  # #codex


def lab_parameter_categories(request):  # #codex
    group_id = request.GET.get('group_id')  # #codex
    if not group_id:  # #codex
        return JsonResponse({'success': True, 'categories': []})  # #codex
    with connection.cursor() as cursor:  # #codex
        cursor.execute("""  # #codex
            SELECT DISTINCT c.id, c.name  # #codex
            FROM transaction__category c  # #codex
            JOIN transaction__groupes selected_group ON selected_group.id = %s  # #codex
            JOIN transaction__groupes category_group ON category_group.id = c.group_id  # #codex
            WHERE c.status = 1  # #codex
              AND (c.group_id = selected_group.id  # #codex
                   OR (category_group.tran_groupe_name = selected_group.tran_groupe_name  # #codex
                       AND category_group.tran_groupe_type = selected_group.tran_groupe_type))  # #codex
            ORDER BY c.name ASC  # #codex
        """, [group_id])  # #codex
        categories = dict_fetchall(cursor)  # #codex
    return JsonResponse({'success': True, 'categories': categories})  # #codex


def lab_parameter_heads(request):  # #codex
    group_id = request.GET.get('group_id')  # #codex
    if not group_id:  # #codex
        return JsonResponse({'success': True, 'heads': []})  # #codex
    params = [group_id]  # #codex
    with connection.cursor() as cursor:  # #codex
        cursor.execute(f"""  # #codex
            SELECT id, tran_head_name AS name  # #codex
            FROM transaction__heads  # #codex
            WHERE groupe_id = %s AND status = 1  # #codex
            ORDER BY tran_head_name ASC  # #codex
        """, params)  # #codex
        heads = dict_fetchall(cursor)  # #codex
    return JsonResponse({'success': True, 'heads': heads})  # #codex


def lab_parameter_list(request):  # #codex
    ensure_lab_parameters_table()  # #codex
    page = int(request.GET.get('page', 1) or 1)  # #codex
    limit = int(request.GET.get('limit', 20) or 20)  # #codex
    offset = (page - 1) * limit  # #codex
    group_id = request.GET.get('group_id')  # #codex
    category_id = request.GET.get('category_id')  # #codex
    head_id = request.GET.get('head_id')  # #codex
    search = (request.GET.get('search') or '').strip()  # #codex
    where_sql = []  # #codex
    params = []  # #codex
    if group_id:  # #codex
        where_sql.append("lp.group_id = %s")  # #codex
        params.append(group_id)  # #codex
    if category_id:  # #codex
        where_sql.append("lp.category_id = %s")  # #codex
        params.append(category_id)  # #codex
    if head_id:  # #codex
        where_sql.append("lp.head_id = %s")  # #codex
        params.append(head_id)  # #codex
    if search:  # #codex
        where_sql.append("(lp.title LIKE %s OR lp.investigation LIKE %s OR lp.unit LIKE %s OR lp.reff_range LIKE %s)")  # #codex
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%", f"%{search}%"])  # #codex
    where_clause = ("WHERE " + " AND ".join(where_sql)) if where_sql else ""  # #codex
    with connection.cursor() as cursor:  # #codex
        cursor.execute(f"""  # #codex
            SELECT lp.id, lp.group_id, g.tran_groupe_name AS group_name, lp.category_id, c.name AS category_name,  # #codex
                   lp.head_id, h.tran_head_name, lp.serial, lp.title, lp.title_code, lp.investigation, lp.investigation_code, lp.unit, lp.reff_range  # #codex
            FROM lab_parameters lp  # #codex
            LEFT JOIN transaction__groupes g ON g.id = lp.group_id  # #codex
            LEFT JOIN transaction__category c ON c.id = lp.category_id  # #codex
            LEFT JOIN transaction__heads h ON h.id = lp.head_id  # #codex
            {where_clause}  # #codex
            ORDER BY g.tran_groupe_name ASC, c.name ASC, lp.serial ASC, lp.id ASC  # #codex
            LIMIT %s OFFSET %s  # #codex
        """, params + [limit, offset])  # #codex
        rows = dict_fetchall(cursor)  # #codex
    return JsonResponse({'success': True, 'lab_parameters': rows})  # #codex


@csrf_exempt  # #codex
def lab_parameter_save(request):  # #codex
    if request.method != "POST":  # #codex
        return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)  # #codex
    try:  # #codex
        ensure_lab_parameters_table()  # #codex
        data = request.POST  # #codex
        group_id = data.get('group_id')  # #codex
        category_id = data.get('category_id')  # #codex
        title = (data.get('title') or '').strip()  # #codex
        investigation = (data.get('investigation') or '').strip()  # #codex
        if not group_id or not category_id or not title or not investigation:  # #codex
            return JsonResponse({'success': False, 'message': 'Group, category, title and investigation required'}, status=400)  # #codex
        desired_serial = _positive_int(data.get('serial'), 1)  # #codex
        with transaction.atomic():  # #codex
            with connection.cursor() as cursor:  # #codex
                cursor.execute("""  # #codex
                    INSERT INTO lab_parameters (group_id, category_id, head_id, serial, title, title_code, investigation, investigation_code, unit, reff_range, added_at, updated_at)  # #codex
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)  # #codex
                """, [  # #codex
                    group_id, category_id, _optional_int(data.get('head_id')), desired_serial,  # #codex
                    title, (data.get('title_code') or '').strip(), investigation, (data.get('investigation_code') or '').strip(),  # #codex
                    (data.get('unit') or '').strip(), (data.get('reff_range') or '').strip(),  # #codex
                    timezone.now(), timezone.now()  # #codex
                ])  # #codex
                new_id = cursor.lastrowid  # #codex
            normalize_lab_parameter_serials(group_id, category_id, new_id, desired_serial)  # #codex
        return JsonResponse({'success': True, 'message': 'Saved successfully'})  # #codex
    except Exception as exc:  # #codex
        traceback.print_exc()  # #codex
        return JsonResponse({'success': False, 'message': str(exc)}, status=400)  # #codex


@csrf_exempt  # #codex
def lab_parameter_update(request):  # #codex
    if request.method != "POST":  # #codex
        return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)  # #codex
    try:  # #codex
        ensure_lab_parameters_table()  # #codex
        data = request.POST  # #codex
        lab_parameter_id = data.get('id')  # #codex
        group_id = data.get('group_id')  # #codex
        category_id = data.get('category_id')  # #codex
        title = (data.get('title') or '').strip()  # #codex
        investigation = (data.get('investigation') or '').strip()  # #codex
        if not lab_parameter_id or not group_id or not category_id or not title or not investigation:  # #codex
            return JsonResponse({'success': False, 'message': 'Required data missing'}, status=400)  # #codex
        desired_serial = _positive_int(data.get('serial'), 1)  # #codex
        with transaction.atomic():  # #codex
            with connection.cursor() as cursor:  # #codex
                cursor.execute("SELECT group_id, category_id FROM lab_parameters WHERE id = %s", [lab_parameter_id])  # #codex
                old_scope = cursor.fetchone()  # #codex
                cursor.execute("""  # #codex
                    UPDATE lab_parameters  # #codex
                    SET group_id = %s, category_id = %s, head_id = %s, serial = %s, title = %s, title_code = %s, investigation = %s, investigation_code = %s,  # #codex
                        unit = %s, reff_range = %s, updated_at = %s  # #codex
                    WHERE id = %s  # #codex
                """, [  # #codex
                    group_id, category_id, _optional_int(data.get('head_id')), desired_serial, title, (data.get('title_code') or '').strip(), investigation, (data.get('investigation_code') or '').strip(),  # #codex
                    (data.get('unit') or '').strip(), (data.get('reff_range') or '').strip(), timezone.now(), lab_parameter_id  # #codex
                ])  # #codex
            if old_scope and (str(old_scope[0]) != str(group_id) or str(old_scope[1]) != str(category_id)):  # #codex
                normalize_lab_parameter_serials(old_scope[0], old_scope[1])  # #codex
            normalize_lab_parameter_serials(group_id, category_id, lab_parameter_id, desired_serial)  # #codex
        return JsonResponse({'success': True, 'message': 'Updated successfully'})  # #codex
    except Exception as exc:  # #codex
        traceback.print_exc()  # #codex
        return JsonResponse({'success': False, 'message': str(exc)}, status=400)  # #codex


@csrf_exempt  # #codex
def lab_parameter_delete(request):  # #codex
    if request.method != "POST":  # #codex
        return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)  # #codex
    try:  # #codex
        ensure_lab_parameters_table()  # #codex
        lab_parameter_id = request.POST.get('id')  # #codex
        if not lab_parameter_id:  # #codex
            return JsonResponse({'success': False, 'message': 'ID required'}, status=400)  # #codex
        with transaction.atomic():  # #codex
            with connection.cursor() as cursor:  # #codex
                cursor.execute("SELECT group_id, category_id FROM lab_parameters WHERE id = %s", [lab_parameter_id])  # #codex
                old_scope = cursor.fetchone()  # #codex
                cursor.execute("DELETE FROM lab_parameters WHERE id = %s", [lab_parameter_id])  # #codex
            if old_scope:  # #codex
                normalize_lab_parameter_serials(old_scope[0], old_scope[1])  # #codex
        return JsonResponse({'success': True, 'message': 'Deleted successfully'})  # #codex
    except Exception as exc:  # #codex
        traceback.print_exc()  # #codex
        return JsonResponse({'success': False, 'message': str(exc)}, status=400)  # #codex


def biochemistry_result_page(request):  # #codex
    ensure_lab_parameters_table()  # #codex
    with connection.cursor() as cursor:  # #codex
        cursor.execute("""  # #codex
            SELECT id, tran_groupe_name AS name  # #codex
            FROM transaction__groupes  # #codex
            WHERE tran_groupe_type = %s AND status = 1  # #codex
            ORDER BY tran_groupe_name ASC  # #codex
        """, [DIAGNOSIS_MAIN_HEAD_ID])  # #codex
        groups = dict_fetchall(cursor)  # #codex
    return render(request, 'diagnosis/biochemistry_result.html', {'groups': groups})  # #codex


def biochemistry_result_add_page(request):  # #codex
    ensure_lab_parameters_table()  # #codex
    return render(request, 'diagnosis/biochemistry_result_form.html')  # #codex


def _biochemistry_category_ids():  # #codex
    with connection.cursor() as cursor:  # #codex
        cursor.execute("""  # #codex
            SELECT id FROM transaction__category  # #codex
            WHERE LOWER(name) = 'biochemistry' AND status = 1  # #codex
        """)  # #codex
        return [row[0] for row in cursor.fetchall()]  # #codex


def _biochemistry_group_ids(category_ids):  # #codex
    if not category_ids:  # #codex
        return []  # #codex
    placeholders = ','.join(['%s'] * len(category_ids))  # #codex
    with connection.cursor() as cursor:  # #codex
        cursor.execute(f"""  # #codex
            SELECT DISTINCT matching_group.id  # #codex
            FROM transaction__category c  # #codex
            JOIN transaction__groupes category_group ON category_group.id = c.group_id  # #codex
            JOIN transaction__groupes matching_group  # #codex
              ON matching_group.id = category_group.id  # #codex
              OR (matching_group.tran_groupe_name = category_group.tran_groupe_name  # #codex
                  AND matching_group.tran_groupe_type = category_group.tran_groupe_type)  # #codex
            WHERE c.id IN ({placeholders}) AND c.status = 1  # #codex
        """, category_ids)  # #codex
        return [row[0] for row in cursor.fetchall()]  # #codex


def _invoice_info(invoice_id=None, search=None):  # #codex
    where_sql = "m.id = %s" if invoice_id else "(m.tran_id = %s OR m.invoice_ref = %s OR m.id = %s)"  # #codex
    params = [invoice_id] if invoice_id else [search, search, search if str(search or '').isdigit() else 0]  # #codex
    with connection.cursor() as cursor:  # #codex
        cursor.execute(f"""  # #codex
            SELECT m.id, m.tran_id, m.invoice_ref, m.tran_date, m.patient_id,  # #codex
                   COALESCE(p.patient_name, m.user_name, '') AS patient_name,  # #codex
                   COALESCE(p.age_y, 0) AS age_y, COALESCE(p.age_m, 0) AS age_m, COALESCE(p.age_d, 0) AS age_d,  # #codex
                   COALESCE(p.gender, '') AS gender, COALESCE(p.present_mobile, m.user_phone, '') AS phone,  # #codex
                   COALESCE(p.present_address, m.user_address, '') AS address,  # #codex
                   COALESCE(doc.name, '') AS doctor_name  # #codex
            FROM transaction__mains m  # #codex
            LEFT JOIN patient_info p ON p.user_info_id COLLATE utf8mb4_unicode_ci = m.patient_id COLLATE utf8mb4_unicode_ci  # #codex
            LEFT JOIN doctors_info doc ON doc.custom_doc_id COLLATE utf8mb4_unicode_ci = m.doctor_id COLLATE utf8mb4_unicode_ci  # #codex
            WHERE {where_sql} AND m.tran_type = %s  # #codex
            LIMIT 1  # #codex
        """, params + [DIAGNOSIS_MAIN_HEAD_ID])  # #codex
        return dict_fetchone(cursor)  # #codex


def biochemistry_invoice_autocomplete(request):  # #codex
    ensure_lab_parameters_table()  # #codex
    term = (request.GET.get('q') or '').strip()  # #codex
    if len(term) < 1:  # #codex
        return JsonResponse({'results': []})  # #codex
    like_term = f"%{term}%"  # #codex
    with connection.cursor() as cursor:  # #codex
        cursor.execute("""  # #codex
            SELECT m.id, m.tran_id, m.invoice_ref, COALESCE(p.patient_name, m.user_name, '') AS patient_name  # #codex
            FROM transaction__mains m  # #codex
            LEFT JOIN patient_info p ON p.user_info_id COLLATE utf8mb4_unicode_ci = m.patient_id COLLATE utf8mb4_unicode_ci  # #codex
            WHERE m.tran_type = %s AND (m.tran_id COLLATE utf8mb4_unicode_ci LIKE %s OR m.invoice_ref COLLATE utf8mb4_unicode_ci LIKE %s OR COALESCE(p.patient_name, m.user_name, '') COLLATE utf8mb4_unicode_ci LIKE %s)  # #codex
            ORDER BY m.id DESC  # #codex
            LIMIT 12  # #codex
        """, [DIAGNOSIS_MAIN_HEAD_ID, like_term, like_term, like_term])  # #codex
        rows = dict_fetchall(cursor)  # #codex
    results = [{'id': row['id'], 'tran_id': row['tran_id'], 'invoice_ref': row['invoice_ref'], 'patient_name': row['patient_name']} for row in rows]  # #codex
    return JsonResponse({'results': results})  # #codex


def biochemistry_invoice_load(request):  # #codex
    ensure_lab_parameters_table()  # #codex
    search = (request.GET.get('invoice') or '').strip()  # #codex
    invoice_id = request.GET.get('invoice_id')  # #codex
    selected_test_id = request.GET.get('test_id')  # #codex
    edit_mode = request.GET.get('edit') == '1'  # #codex
    if not search and not invoice_id:  # #codex
        return JsonResponse({'success': False, 'message': 'Transaction ID required'}, status=400)  # #codex
    category_ids = _biochemistry_category_ids()  # #codex
    if not category_ids:  # #codex
        return JsonResponse({'success': False, 'message': 'Biochemistry category setup not found'}, status=400)  # #codex
    invoice = _invoice_info(invoice_id=invoice_id, search=search)  # #codex
    if not invoice:  # #codex
        return JsonResponse({'success': False, 'message': 'Diagnosis transaction not found'}, status=404)  # #codex
    placeholders = ','.join(['%s'] * len(category_ids))  # #codex
    group_ids = _biochemistry_group_ids(category_ids)  # #codex
    with connection.cursor() as cursor:  # #codex
        test_where = "AND COALESCE(d.tran_groupe_id, h.groupe_id) IN ({})".format(','.join(['%s'] * len(group_ids))) if group_ids else ""  # #codex
        test_params = [invoice['tran_id'], DIAGNOSIS_MAIN_HEAD_ID] + group_ids  # #codex
        cursor.execute(f"""  # #codex
            SELECT DISTINCT d.tran_head_id AS id, h.tran_head_name AS name, COALESCE(d.tran_groupe_id, h.groupe_id) AS group_id  # #codex
            FROM transaction__details d  # #codex
            JOIN transaction__heads h ON h.id = d.tran_head_id  # #codex
            WHERE d.tran_id = %s AND d.tran_type = %s AND d.tran_head_id IS NOT NULL {test_where}  # #codex
              AND (%s = 1 OR NOT EXISTS (SELECT 1 FROM lab_results lr WHERE lr.invoice_id = %s AND lr.category_id IN ({placeholders})))  # #codex
            ORDER BY h.tran_head_name ASC  # #codex
        """, test_params + [1 if edit_mode else 0, invoice['id']] + category_ids)  # #codex
        tests = dict_fetchall(cursor)  # #codex
        if not tests:  # #codex
            cursor.execute(f"SELECT COUNT(*) AS saved_count FROM lab_results WHERE invoice_id = %s AND category_id IN ({placeholders})", [invoice['id']] + category_ids)  # #codex
            saved_row = dict_fetchone(cursor)  # #codex
            return JsonResponse({'success': True, 'invoice': invoice, 'tests': [], 'rows': [], 'already_added': (saved_row or {}).get('saved_count', 0) > 0})  # #codex
        params = category_ids[:]  # #codex
        cursor.execute(f"""  # #codex
            SELECT p.id AS parameter_id, p.group_id, p.category_id, p.head_id, h.tran_head_name, p.serial,  # #codex
                   p.title, p.title_code, p.investigation, p.investigation_code, p.unit, p.reff_range,  # #codex
                   COALESCE(r.result, '') AS result  # #codex
            FROM lab_parameters p  # #codex
            LEFT JOIN transaction__heads h ON h.id = p.head_id  # #codex
            LEFT JOIN lab_results r ON r.invoice_id = %s AND r.category_id = p.category_id AND COALESCE(r.investigation_code, '') = COALESCE(p.investigation_code, '') AND r.investigation = p.investigation  # #codex
            WHERE p.category_id IN ({placeholders})  # #codex
            ORDER BY p.serial ASC, p.id ASC  # #codex
        """, [invoice['id']] + params)  # #codex
        rows = dict_fetchall(cursor)  # #codex
        if not rows:  # #codex
            cursor.execute(f"""  # #codex
                SELECT p.id AS parameter_id, p.group_id, p.category_id, p.head_id, h.tran_head_name, p.serial,  # #codex
                       p.title, p.title_code, p.investigation, p.investigation_code, p.unit, p.reff_range, '' AS result  # #codex
                FROM lab_parameters p  # #codex
                LEFT JOIN transaction__heads h ON h.id = p.head_id  # #codex
                WHERE p.category_id IN ({placeholders})  # #codex
                ORDER BY p.serial ASC, p.id ASC  # #codex
            """, category_ids)  # #codex
            rows = dict_fetchall(cursor)  # #codex
        cursor.execute(f"SELECT selected_test_ids, selected_test_names FROM lab_results WHERE invoice_id = %s AND category_id IN ({placeholders}) LIMIT 1", [invoice['id']] + category_ids)  # #codex
        selected_row = dict_fetchone(cursor)  # #codex
    selected_ids = [item for item in str((selected_row or {}).get('selected_test_ids') or '').split(',') if item]  # #codex
    selected_names = [item.strip() for item in str((selected_row or {}).get('selected_test_names') or '').split(',') if item.strip()]  # #codex
    return JsonResponse({'success': True, 'invoice': invoice, 'tests': tests, 'rows': rows, 'selected_test_ids': selected_ids, 'selected_test_names': selected_names})  # #codex


@csrf_exempt  # #codex
def biochemistry_result_save(request):  # #codex
    if request.method != 'POST':  # #codex
        return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)  # #codex
    try:  # #codex
        ensure_lab_parameters_table()  # #codex
        payload = json.loads(request.body.decode('utf-8') or '{}')  # #codex
        invoice_id = payload.get('invoice_id')  # #codex
        selected_test_ids = ','.join([str(item) for item in (payload.get('selected_test_ids') or []) if str(item).strip()])  # #codex
        selected_test_names = ', '.join([str(item) for item in (payload.get('selected_test_names') or []) if str(item).strip()])  # #codex
        rows = [row for row in (payload.get('rows') or []) if str(row.get('result') or '').strip()]  # #codex
        if not invoice_id or not rows:  # #codex
            return JsonResponse({'success': False, 'message': 'At least one result value required'}, status=400)  # #codex
        with transaction.atomic():  # #codex
            category_ids = sorted({str(row.get('category_id')) for row in rows if row.get('category_id')})  # #codex
            with connection.cursor() as cursor:  # #codex
                if category_ids:  # #codex
                    cursor.execute("DELETE FROM lab_results WHERE invoice_id = %s AND category_id IN ({})".format(','.join(['%s'] * len(category_ids))), [invoice_id] + category_ids)  # #codex
                insert_rows = []  # #codex
                for row in rows:  # #codex
                    row_title = str(row.get('title') or '').strip()  # #codex
                    row_title = selected_test_names if not row_title or row_title == '-' else row_title  # #codex
                    insert_rows.append([  # #codex
                        invoice_id, selected_test_ids, selected_test_names, row.get('group_id'), row.get('category_id'), None, row.get('serial') or 0,  # #codex
                        row_title, row.get('title_code') or '', row.get('investigation') or '', row.get('investigation_code') or '',  # #codex
                        row.get('unit') or '', row.get('reff_range') or '', row.get('result') or '', timezone.now(), timezone.now()  # #codex
                    ])  # #codex
                cursor.executemany("""  # #codex
                    INSERT INTO lab_results (invoice_id, selected_test_ids, selected_test_names, group_id, category_id, head_id, serial, title, title_code, investigation, investigation_code, unit, reff_range, result, added_at, updated_at)  # #codex
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)  # #codex
                """, insert_rows)  # #codex
        return JsonResponse({'success': True, 'invoice_id': invoice_id, 'preview_url': f'/diagnosis/lab-report/biochemistry/preview/{invoice_id}/', 'download_url': f'/diagnosis/lab-report/biochemistry/pdf/{invoice_id}/?download=1'})  # #codex
    except Exception as exc:  # #codex
        traceback.print_exc()  # #codex
        return JsonResponse({'success': False, 'message': str(exc)}, status=400)  # #codex


def biochemistry_result_list(request):  # #codex
    ensure_lab_parameters_table()  # #codex
    search = (request.GET.get('search') or '').strip()  # #codex
    group_id = request.GET.get('group_id')  # #codex
    category_id = request.GET.get('category_id')  # #codex
    where_parts = []  # #codex
    params = []  # #codex
    if search:  # #codex
        where_parts.append("(m.tran_id LIKE %s OR m.invoice_ref LIKE %s OR p.patient_name LIKE %s OR m.user_name LIKE %s)")  # #codex
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%", f"%{search}%"])  # #codex
    if group_id:  # #codex
        where_parts.append("r.group_id = %s")  # #codex
        params.append(group_id)  # #codex
    if category_id:  # #codex
        where_parts.append("r.category_id = %s")  # #codex
        params.append(category_id)  # #codex
    where_parts.append("COALESCE(r.result, '') <> ''")  # #codex
    where_sql = "WHERE " + " AND ".join(where_parts) if where_parts else ""  # #codex
    with connection.cursor() as cursor:  # #codex
        cursor.execute(f"""  # #codex
            SELECT r.invoice_id, m.tran_id, m.invoice_ref, COALESCE(p.patient_name, m.user_name, '') AS patient_name,  # #codex
                   MAX(r.updated_at) AS updated_at, COUNT(*) AS total_rows  # #codex
            FROM lab_results r  # #codex
            JOIN transaction__mains m ON m.id = r.invoice_id  # #codex
            LEFT JOIN patient_info p ON p.user_info_id COLLATE utf8mb4_unicode_ci = m.patient_id COLLATE utf8mb4_unicode_ci  # #codex
            {where_sql}  # #codex
            GROUP BY r.invoice_id, m.tran_id, m.invoice_ref, patient_name  # #codex
            ORDER BY MAX(r.updated_at) DESC, r.invoice_id DESC  # #codex
            LIMIT 100  # #codex
        """, params)  # #codex
        results = dict_fetchall(cursor)  # #codex
    return JsonResponse({'success': True, 'results': results})  # #codex


def _biochemistry_report_rows(invoice_id):  # #codex
    ensure_lab_parameters_table()  # #codex
    invoice = _invoice_info(invoice_id=invoice_id)  # #codex
    if not invoice:  # #codex
        return None, []  # #codex
    with connection.cursor() as cursor:  # #codex
        cursor.execute("""  # #codex
            SELECT r.title, r.investigation, r.result, r.unit, r.reff_range, r.serial, r.head_id, r.selected_test_names,  # #codex
                   COALESCE(NULLIF(NULLIF(TRIM(r.title), ''), '-'), NULLIF(TRIM(r.selected_test_names), ''), r.investigation) AS test_name, COALESCE(c.name, 'Biochemistry') AS category_name  # #codex
            FROM lab_results r  # #codex
            LEFT JOIN transaction__category c ON c.id = r.category_id  # #codex
            WHERE r.invoice_id = %s AND COALESCE(r.result, '') <> ''  # #codex
            ORDER BY c.name ASC, r.serial ASC, r.id ASC  # #codex
        """, [invoice_id])  # #codex
        rows = dict_fetchall(cursor)  # #codex
    return invoice, rows  # #codex


def biochemistry_result_preview(request, invoice_id):  # #codex
    invoice, rows = _biochemistry_report_rows(invoice_id)  # #codex
    if not invoice:  # #codex
        return JsonResponse({'success': False, 'message': 'Invoice not found'}, status=404)  # #codex
    receipt_no = invoice.get('invoice_ref') or invoice.get('tran_id') or str(invoice_id)  # #codex
    age_text = f"{invoice.get('age_y') or 0}Y {invoice.get('age_m') or 0}M {invoice.get('age_d') or 0}D"  # #codex
    selected_names = rows[0].get('selected_test_names') if rows else ''  # #codex
    html = f"""<div class='bio-report-preview'>
        <div class='bio-report-head'>
            <div><b>Name</b> : {escape(invoice.get('patient_name') or '-')}</div>
            <div><b>Age</b> : {escape(age_text)} {escape(invoice.get('gender') or '')}</div>
            <div><b>Reg No.</b> : {escape(receipt_no)}</div>
            <div><b>Phone</b> : {escape(invoice.get('phone') or '-')}</div>
            <div><b>Ref. By</b> : {escape(invoice.get('doctor_name') or '-')}</div>
            <div><b>Reg. Date</b> : {escape(str(invoice.get('tran_date') or '')[:16])}</div>
            <div class='bio-full'><b>Address</b> : {escape(invoice.get('address') or '-')}</div>
            <div class='bio-full'><b>Investigation</b> : {escape(selected_names or '-')}</div>
        </div>"""  # #codex
    grouped = {}  # #codex
    for row in rows:  # #codex
        grouped.setdefault(row.get('category_name') or 'Biochemistry', {}).setdefault(row.get('test_name') or row.get('title') or 'Test', []).append(row)  # #codex
    if not grouped:  # #codex
        html += "<div class='text-center p-4'>No result data found</div>"  # #codex
    for category, tests in grouped.items():  # #codex
        html += f"<h4>{escape(str(category).upper())} REPORT</h4><table><colgroup><col style='width:45%'><col style='width:12%'><col style='width:15%'><col style='width:28%'></colgroup><thead><tr><th>Title</th><th>Result</th><th>Unit</th><th>Ref</th></tr></thead><tbody>"  # #codex
        for test_name, test_rows in tests.items():  # #codex
            html += f"<tr class='bio-test-title'><td colspan='4'>*{escape(test_name)}</td></tr>"  # #codex
            for row in test_rows:  # #codex
                html += f"<tr><td>{escape(row.get('investigation') or '')}</td><td>{escape(row.get('result') or '')}</td><td>{escape(row.get('unit') or '')}</td><td>{escape(row.get('reff_range') or '').replace(chr(10), '<br>')}</td></tr>"  # #codex
        html += "</tbody></table>"  # #codex
    html += "</div>"  # #codex
    return JsonResponse({'success': True, 'html': html, 'download_url': f'/diagnosis/lab-report/biochemistry/pdf/{invoice_id}/?download=1'})  # #codex


def biochemistry_result_pdf(request, invoice_id):  # #codex
    invoice, rows = _biochemistry_report_rows(invoice_id)  # #codex
    if not invoice:  # #codex
        return HttpResponse("Invoice not found", status=404)  # #codex
    buffer = BytesIO()  # #codex
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=34, leftMargin=34, topMargin=34, bottomMargin=28)  # #codex
    styles = getSampleStyleSheet()  # #codex
    normal = ParagraphStyle("BioNormal", parent=styles["Normal"], fontName="Helvetica", fontSize=9, leading=12)  # #codex
    small = ParagraphStyle("BioSmall", parent=styles["Normal"], fontName="Helvetica", fontSize=8, leading=10)  # #codex
    bold = ParagraphStyle("BioBold", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=9, leading=12)  # #codex
    center_title = ParagraphStyle("BioCenterTitle", parent=styles["Normal"], alignment=TA_CENTER, fontName="Helvetica-Bold", fontSize=11, leading=13)  # #codex
    center_section = ParagraphStyle("BioCenterSection", parent=styles["Normal"], alignment=TA_CENTER, fontName="Helvetica", fontSize=11, leading=13)  # #codex
    receipt_no = invoice.get('invoice_ref') or invoice.get('tran_id') or str(invoice_id)  # #codex
    tran_date = str(invoice.get('tran_date') or '')[:16]  # #codex
    age_text = f"{invoice.get('age_y') or 0} Year {invoice.get('gender') or ''}".strip()  # #codex
    barcode = code128.Code128(receipt_no, barHeight=0.28 * inch, barWidth=0.7)  # #codex
    story = []  # #codex
    header_data = [  # #codex
        [Paragraph("Name&nbsp;&nbsp;&nbsp;&nbsp;: " + (invoice.get('patient_name') or '-'), normal), Paragraph(age_text, normal), Paragraph("Reg No.&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;: " + receipt_no, normal), barcode],  # #codex
        [Paragraph("Ref. By&nbsp;: " + (invoice.get('doctor_name') or '-'), normal), "", Paragraph("Reg. Date&nbsp;&nbsp;: " + tran_date, normal), ""],  # #codex
        [Paragraph("Address&nbsp;: " + (invoice.get('address') or '-'), normal), "", Paragraph("Collected At&nbsp;: SECL", normal), ""],  # #codex
        [Paragraph("Phone&nbsp;&nbsp;&nbsp;: " + (invoice.get('phone') or '-'), normal), "", "", ""],  # #codex
        [Paragraph("Investigation&nbsp;: " + ((rows[0].get('selected_test_names') if rows else '') or '-'), normal), "", "", ""],  # #codex
    ]  # #codex
    header = Table(header_data, colWidths=[2.55*inch, 1.35*inch, 1.7*inch, 1.25*inch])  # #codex
    header.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("SPAN", (3, 0), (3, 2)), ("LINEBELOW", (0, 4), (-1, 4), 0.8, colors.black)]))  # #codex
    story.append(header)  # #codex
    story.append(Spacer(1, 0.08 * inch))  # #codex
    grouped = {}  # #codex
    for row in rows:  # #codex
        category = row.get('category_name') or 'Biochemistry'  # #codex
        test_name = row.get('test_name') or row.get('title') or 'Test'  # #codex
        grouped.setdefault(category, {}).setdefault(test_name, []).append(row)  # #codex
    for category, tests in grouped.items():  # #codex
        story.append(Paragraph(f"<u>{str(category).upper()} REPORT</u>", center_title))  # #codex
        table_data = [[Paragraph("<u>Title</u>", bold), Paragraph("<u>Result</u>", bold), Paragraph("<u>Unit</u>", bold), Paragraph("<u>Ref</u>", bold)]]  # #codex
        for test_name, test_rows in tests.items():  # #codex
            table_data.append([Paragraph(f"<b><u>*{test_name}</u></b>", bold), "", "", ""])  # #codex
            first_row = True  # #codex
            for row in test_rows:  # #codex
                label = (row.get('investigation') or row.get('title') or '')  # #codex
                display_label = f"<b>{label}</b>" if first_row and len(test_rows) == 1 else label  # #codex
                table_data.append([Paragraph(display_label, normal), Paragraph(row.get('result') or '', normal), Paragraph(row.get('unit') or '', normal), Paragraph((row.get('reff_range') or '').replace('\n', '<br/>'), small)])  # #codex
                first_row = False  # #codex
        result_table = Table(table_data, colWidths=[3.2*inch, 0.85*inch, 1.0*inch, 2.0*inch], repeatRows=1)  # #codex
        result_table.setStyle(TableStyle([  # #codex
            ("VALIGN", (0, 0), (-1, -1), "TOP"), ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),  # #codex
            ("ALIGN", (1, 0), (1, -1), "RIGHT"), ("ALIGN", (2, 0), (2, -1), "LEFT"), ("ALIGN", (3, 0), (3, -1), "LEFT"),  # #codex
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5), ("TOPPADDING", (0, 0), (-1, -1), 3),  # #codex
            ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 6), ("LEFTPADDING", (2, 0), (2, -1), 8),  # #codex
        ]))  # #codex
        story.append(result_table)  # #codex
        story.append(Spacer(1, 0.12 * inch))  # #codex
    if not rows:  # #codex
        story.append(Paragraph("No result data found", center_section))  # #codex
    doc.build(story)  # #codex
    pdf = buffer.getvalue()  # #codex
    buffer.close()  # #codex
    response = HttpResponse(pdf, content_type="application/pdf")  # #codex
    mode = "attachment" if request.GET.get("download") == "1" else "inline"  # #codex
    response["Content-Disposition"] = f'{mode}; filename="biochemistry_report_{invoice_id}.pdf"'  # #codex
    return response  # #codex



