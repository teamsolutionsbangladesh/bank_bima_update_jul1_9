from django.db import connection
from django.http import JsonResponse
from django.shortcuts import render, redirect
import random
from django.shortcuts import render, redirect
# from .models import TransactionMainHeads, TransactionWiths, TransactionGroupes


# SUBJECT

def add_page_init(request):
    return render(request, 'page_init/page_init.html')

def save_page_init(request):
    if request.method == "POST":
        page_id = request.POST.get('page_id')        
        transactionmainheads = request.POST.get('transactionmainheads')
        load_head_all = request.POST.get('load_head_all')
        transaction_with_method = request.POST.get('transaction_with_method')
        transaction_with = request.POST.get('transaction_with')
        transaction_method = request.POST.get('transaction_method')
        tran_group = request.POST.get('tran_group')

        print("DEBUG >>>>>>>>>>>>>>>>>>>>>>>>>>> ", page_id);        
        print("DEBUG >>>>>>>>>>>>>>>>>>>>>>>>>>> ", transactionmainheads);
        print("DEBUG >>>>>>>>>>>>>>>>>>>>>>>>>>> ", load_head_all);
        print("DEBUG >>>>>>>>>>>>>>>>>>>>>>>>>>> ", transaction_with_method);
        print("DEBUG >>>>>>>>>>>>>>>>>>>>>>>>>>> ", transaction_with);
        print("DEBUG >>>>>>>>>>>>>>>>>>>>>>>>>>> ", transaction_method);
        print("DEBUG >>>>>>>>>>>>>>>>>>>>>>>>>>> ", tran_group);

        cursor = connection.cursor()
        sql = """
            INSERT INTO page_init 
            (page_id, 
            tran_main_head_id,
            load_head_all,
            user_tran_method,
            user_tran_with_id,
            tran_method,
            tran_group_id
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        params = [
            page_id, 
            transactionmainheads,
            load_head_all,
            transaction_with_method,
            transaction_with,
            transaction_method,
            tran_group,   
            ]

        cursor.execute(sql, params)

        return JsonResponse({"status":"success","message":"Save Successfull!"})
    
    return JsonResponse({"status":"faield","message":"Invalid entry!"})

def update_page_init(request):
    if request.method == "POST":
        page_id = request.POST.get('page_id')
        transactionmainheads = request.POST.get('transactionmainheads')
        transaction_with_method = request.POST.get('transaction_with_method')
        transaction_with = request.POST.get('transaction_with')
        transaction_method = request.POST.get('transaction_method')
        tran_group = request.POST.get('tran_group')

        cursor = connection.cursor()
        sql = """
            UPDATE page_init 
            SET 
            tran_main_head_id = %s,
            user_tran_method = %s,
            user_tran_with_id = %s,
            tran_method = %s,
            tran_group_id = %s
            WHERE page_id = %s

        """
        params = [             
            transactionmainheads,
            transaction_with_method,
            transaction_with,
            transaction_method,
            tran_group,
            page_id,   
            ]

        cursor.execute(sql, params)

        return JsonResponse({"status":"success","message":"Updated Successfull!"})
    
    return JsonResponse({"status":"faield","message":"Invalid entry!"})

def load_page_init_list(request):

    cursor = connection.cursor()
    sql = """
        select 
        a.id as id,
        a.page_id as page_id,
        a.tran_main_head_id as tran_main_head_id,
        a.user_tran_method as user_tran_method,
        a.user_tran_with_id as user_tran_with_id,
        a.tran_method as tran_method,
        a.tran_group_id as tran_group_id,
        a.status as status
        from page_init a
    """

    params = []

    cursor.execute(sql, params)

    page_init_list = [
        {
            "id": row[0],
            "page_id": row[1],
            "tran_main_head_id": row[2],
            "user_tran_method": row[3],
            "user_tran_with_id": row[4],
            "tran_method": row[5],
            "tran_group_id": row[6],
            "status": row[7],

        }
        for row in cursor.fetchall()
    ]
    return JsonResponse({
        "page_init_list": page_init_list,
    })

def fetch_data_for_edit(request):
    page_id = request.GET.get('page_id')

    cursor = connection.cursor()
    sql = """
        select 
        a.id as id,
        a.page_id as page_id,
        a.tran_main_head_id as tran_main_head_id,
        a.user_tran_method as user_tran_method,
        a.user_tran_with_id as user_tran_with_id,
        a.tran_method as tran_method,
        a.tran_group_id as tran_group_id,
        a.status as status
        from page_init a
        WHERE a.page_id = %s

    """

    params = [page_id]

    cursor.execute(sql, params)

    data = [
        {

            "id": row[0],
            "page_id": row[1],
            "tran_main_head_id": row[2],
            "user_tran_method": row[3],
            "user_tran_with_id": row[4],
            "tran_method": row[5],
            "tran_group_id": row[6],
            "status": row[7],

        }
        for row in cursor.fetchall()
    ]
    return JsonResponse({
        "data": data,
    })

def remove_subject(request):
    sub_id = request.POST.get('sub_id')

    print(sub_id);
    cursor = connection.cursor()
    sql = """
        DELETE 
        FROM school_subject
        WHERE id = %s
    """

    params = [sub_id]

    cursor.execute(sql, params)

    return JsonResponse({"status":"remove","message":"Remove Successfull!"})


def page_init(request):

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                id,
                page_id,
                location_id,
                company_id,
                tran_main_head_id,
                user_tran_method,
                user_tran_with_id,
                tran_method,
                tran_group_id,
                status
            FROM page_init
        """)

        rows = cursor.fetchall()

    # convert to dict (for template)
    data = []
    for row in rows:
        data.append({
            "id": row[0],
            "page_id": row[1],
            "location_id": row[2],
            "company_id": row[3],
            "tran_main_head_id": row[4],
            "user_tran_method": row[5],
            "user_tran_with_id": row[6],
            "tran_method": row[7],
            "tran_group_id": row[8],
            "status": row[9],
        })

    return render(request, 'page_init/page_init_list.html', {'data': data})





def generate_10_digit_id():
    return random.randint(1000000000, 9999999999)

def get_withs(request):

    head_id = request.GET.get('head_id')

    if not head_id:
        return JsonResponse([], safe=False)

    with connection.cursor() as cursor:

        cursor.execute("""
            SELECT id, tran_with_name
            FROM transaction__withs
            WHERE tran_type = %s
        """, [head_id])

        rows = cursor.fetchall()

    data = []

    for row in rows:
        data.append({
            "id": row[0],
            "tran_with_name": row[1]
        })

    return JsonResponse(data, safe=False)

def get_transaction_groups(request):

    head_id = request.GET.get('head_id')

    if not head_id:
        return JsonResponse([], safe=False)

    with connection.cursor() as cursor:

        cursor.execute("""
            SELECT id, tran_groupe_name
            FROM transaction__groupes
            WHERE tran_groupe_type = %s
        """, [head_id])

        rows = cursor.fetchall()

    data = []

    for row in rows:
        data.append({
            "id": row[0],
            "tran_groupe_name": row[1]
        })

    return JsonResponse(data, safe=False)


