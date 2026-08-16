from datetime import timezone
import json
from django.http import JsonResponse
from django.forms import model_to_dict
from django.shortcuts import get_object_or_404, redirect, render
from django.db import connection
from django.db import transaction
from django.db.models import F, Q
from django.db.models import Count, Case, When, IntegerField, Q
from datetime import datetime
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt



def transaction_head_page(request):
    # Add Medicine modal/page
    return render(request, 'transaction_heads/transaction_heads.html')

def transaction_head_form(request):
    # Add Medicine modal/page
    return render(request, 'transaction_heads/transaction_head_form.html')

def load_transaction_head(request):

    page = int(request.GET.get('page', 1))
    limit = int(request.GET.get('limit', 10))
    search_tran_main_head = request.GET.get('search_tran_main_head', '').strip()
    search_tran_head = request.GET.get('search_tran_head', '').strip()

    offset = (page - 1) * limit

    search_sql = ""
    params = []

    print(search_tran_main_head);
    params.append(search_tran_main_head)

    # search filter
    if search_tran_head:
        search_sql += " AND a.tran_head_name LIKE %s "
        params.append(f"%{search_tran_head}%")


    cursor = connection.cursor()
    sql = f"""
        SELECT        
            a.tran_main_head_id,
            a.tran_method,
            a.groupe_id,
            a.id,
            a.tran_head_name,
            a.cp,
            a.mrp,
            a.status
        FROM transaction__heads a
        WHERE a.tran_main_head_id = %s
        {search_sql}
        ORDER BY 
            a.tran_main_head_id,
            a.tran_method,
            a.tran_head_name
        LIMIT %s OFFSET %s
    """

    params.extend([limit, offset])

    cursor.execute(sql, params)

    transaction_head_list = [
        {
            "tran_main_head_id": row[0],
            "tran_method": row[1],
            "group_id": row[2],
            "id": row[3],
            "tran_head_name": row[4],
            "cp": row[5],
            "mrp": row[6],
            "status": row[7],
        }
        for row in cursor.fetchall()
    ]

    # print(transaction_head_list);

    return JsonResponse({
        "transaction_head_list": transaction_head_list,
    })

def save_transaction_heads(request):
    if request.method == "POST":
        tran_main_head_id = request.POST.get('tran_main_head_id')
        tran_method = request.POST.get('tran_method')
        tran_group_id = request.POST.get('tran_group_id')
        tran_head = request.POST.get('tran_head')
        tran_head_cp = request.POST.get('tran_head_cp')
        tran_head_mrp = request.POST.get('tran_head_mrp')
        created_at = timezone.now().date()
        updated_at = timezone.now().date()

        print("DEBUG>>>>>>>>> tran_main_head_id ",tran_main_head_id)
        print("DEBUG>>>>>>>>> tran_method ",tran_method)
        print("DEBUG>>>>>>>>> tran_group_id ",tran_group_id)
        print("DEBUG>>>>>>>>> tran_head ",tran_head)

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
                INSERT INTO transaction__heads (tran_main_head_id, tran_method, groupe_id, tran_head_name, cp, mrp, added_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            params = [tran_main_head_id, tran_method, tran_group_id, tran_head, tran_head_cp, tran_head_mrp, created_at, updated_at]

            print("PARAMS >>>>", params)

            cursor.execute(sql, params)

            return JsonResponse({"status": "success", "message": "Saved successfully!!"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})

    return JsonResponse({"status": "failed", "message": "Invalid request"})

def update_transaction_heads(request):
    if request.method == "POST":      
        tran_head_id = request.POST.get('tran_head_id')
        tran_head = request.POST.get('tran_head')
        tran_head_cp = request.POST.get('tran_head_cp')
        tran_head_mrp = request.POST.get('tran_head_mrp')

        cursor = connection.cursor()
        sql = """
            UPDATE transaction__heads 
            SET tran_head_name = %s, cp = %s, mrp = %s
            WHERE id = %s
        """
        params = [tran_head, tran_head_cp, tran_head_mrp, tran_head_id]

        cursor.execute(sql, params)

        return JsonResponse({"status":"success","message":"Updated Successfull!"})
    
    return JsonResponse({"status":"faield","message":"Invalid entry!"})
