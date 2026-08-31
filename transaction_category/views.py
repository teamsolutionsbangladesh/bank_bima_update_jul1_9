from datetime import timezone
import json
from django.http import JsonResponse
from django.forms import model_to_dict
from django.shortcuts import get_object_or_404, redirect, render
from django.db import connection
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

# Form Template View
def transaction_category_view(request):
    return render(request, 'transaction_category/transaction_category.html')

# Real-time AJAX Grid Loader Endpoint (Raw SQL, Offset-Limit Pagination & Sequence Flow)
def load_transaction_category(request):

    page = int(request.GET.get('page', 1))
    limit = int(request.GET.get('limit', 10))
    search_main_head = request.GET.get('search_main_head', '').strip()
    search_category = request.GET.get('search_category', '').strip()

    offset = (page - 1) * limit

    search_sql = ""
    params = []

    print(search_main_head);
    params.append(search_main_head)

    # search filter
    if search_category:
        search_sql += " AND a.name LIKE %s "
        params.append(f"%{search_category}%")


    cursor = connection.cursor()
    sql = """
        SELECT
            a.id,
            a.tran_main_head_id,
            a.group_id,
            a.name,
            a.status
        FROM transaction__category a
        ORDER BY
            a.tran_main_head_id,
            a.group_id,
            a.name
        LIMIT %s OFFSET %s
    """

    params = [limit, offset]
    
    cursor.execute(sql, params)

    transaction_category_list = [
        {
            "id": row[0],
            "tran_main_head_id": row[1],
            "group_id": row[2],
            "name": row[3],
            "status": row[4],
        }
        for row in cursor.fetchall()
    ]

    # print(transaction_category_list);

    return JsonResponse({
        "transaction_category_list": transaction_category_list,
    })

# Actual AJAX Save Endpoint (Separated View Pipeline)
@csrf_exempt
def save_transaction_category(request):
    if request.method == "POST":
        tran_main_head_id = request.POST.get('tran_main_head_id')
        tran_group_id = request.POST.get('tran_group_id')
        tran_category_name = request.POST.get('tran_category_name') # JS matches generic label map
        # status = 'Active'

        try:
            cursor = connection.cursor()
            
            # Raw SQL dynamic data persistence structure
            sql = """
                INSERT INTO transaction__category (tran_main_head_id, group_id, name)
                VALUES (%s, %s, %s)
            """
            params = [tran_main_head_id, tran_group_id, tran_category_name]
            cursor.execute(sql, params)

            return JsonResponse({"status": "success", "message": "Save successful"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})

    return JsonResponse({"status": "failed", "message": "Invalid request"})

# Actual AJAX Update Endpoint (Separated View Pipeline)
@csrf_exempt
def update_transaction_category(request):
    if request.method == "POST":    

            
         
        category_id = request.POST.get('category_id')
        tran_category_name = request.POST.get('tran_category_name')

        print(category_id, tran_category_name)
    
        # tran_head_id = request.POST.get('tran_head_id')
        # tran_head = request.POST.get('tran_head')

        try:
            cursor = connection.cursor()
            sql = """
                UPDATE transaction__category 
                SET name = %s
                WHERE id = %s
            """
            params = [tran_category_name, category_id]
            cursor.execute(sql, params)

            return JsonResponse({"status": "success", "message": "Update successful"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})
            
    return JsonResponse({"status": "failed", "message": "Invalid entry!"})

# Dynamic Truncation Layer (Delete)
@csrf_exempt
def delete_transaction_category(request):
    if request.method == 'POST':
        try:
            target_id = request.POST.get('id')
            
            cursor = connection.cursor()
            sql = "DELETE FROM transaction__category WHERE id = %s"
            cursor.execute(sql, [target_id])
            
            return JsonResponse({'status': 'success', 'message': 'Deleted successfully!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
            
    return JsonResponse({'status': 'error', 'message': 'Invalid Method Context'})