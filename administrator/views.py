from datetime import timezone
from io import BytesIO
import json
from django.http import HttpResponse, JsonResponse
from django.forms import model_to_dict
from django.shortcuts import get_object_or_404, redirect, render
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


def dictfetchall(cursor):
    """Return all rows from a cursor as a list of dicts."""
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

def save_transaction_with_user(request):

    if request.method == "POST":

        tran_main_head_id = request.POST.get('tran_main_head_id')
        tran_with_method = request.POST.get('tran_with_method')
        tran_with = request.POST.get('tran_with')
        tran_user = request.POST.get('tran_user')
        created_at = timezone.now().date()
        updated_at = timezone.now().date()

        print("DEBUG>>>>>>>>>",tran_main_head_id)

        # ---- Generate USER ID ----
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT user_id 
                FROM user__infos
                WHERE user_id LIKE 'USR%'
                ORDER BY user_id DESC
                LIMIT 1
            """)
            
            row = cursor.fetchone()

            if row:
                last_number = int(row[0][3:])  # remove USR
            else:
                last_number = 0

            generated_user_id = "USR" + str(last_number + 1).zfill(9)
        # ---- END of Generate transaction ID ----

        try:
            ## Check for duplicates
            # exists = Subject.objects.filter(
            #     name= sub_name,
            #     description= sub_description,
            #     teachers= teacher_id,
            # ).exists()

            # if exists:
            #     return JsonResponse({"status": "exists", "message": "Attendance already exists."})

            # Save new record
            # Subject.objects.create(
            #     name= sub_name,
            #     description= sub_description,
            #     teachers= teacher_id,
            #     created_at= timezone.now().date(),
            #     updated_at= timezone.now().date(),
            # )

            cursor = connection.cursor()
            sql = """
                INSERT INTO user__infos (user_id, user_name, tran_user_type, tran_method, tran_with_id, added_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
                    
            params = [generated_user_id, tran_user, tran_main_head_id, tran_with_method, tran_with, created_at, updated_at]

            print("PARAMS >>>>", params)

            cursor.execute(sql, params)

            return JsonResponse({"status": "success", "message": "Saved successfully!!"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})

    return JsonResponse({"status": "failed", "message": "Invalid request"})
    

