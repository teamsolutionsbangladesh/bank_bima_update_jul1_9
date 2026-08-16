from django.shortcuts import render
from django.utils import timezone
from django.http import JsonResponse
from django.db import connection


def transaction_with_user_form(request):
    return render(request, 'transaction_with_user/transaction_with_user_form.html')

def load_transaction_with_user(request):

    cursor = connection.cursor()
    sql = """
        select         
        a.tran_type as tran_type,
        b.type_name as type_name,
        a.id as id,
        a.tran_with_name as tran_with_name,
        a.tran_method as method
        from transaction__withs a
        LEFT JOIN transaction__main__heads b ON a.tran_type = b.id
        ORDER BY a.tran_type, b.id
    """

    params = []

    cursor.execute(sql, params)

    transaction_with_list = [
        {
            "tran_type": row[0],
            "type_name": row[1],
            "id": row[2],
            "tran_with_name": row[3],
            "method": row[4]
        }
        for row in cursor.fetchall()
    ]

    print(transaction_with_list);

    return JsonResponse({
        "transaction_with_list": transaction_with_list,
    })


def transaction_with_user_fetch_data(request):
    tran_with_id = request.GET.get('tran_with_id')

    cursor = connection.cursor()
    sql = """
        SELECT
        a.id as id,
        a.tran_with_name as name,
        a.tran_method as method
        FROM transaction__withs a
        WHERE a.id = %s
    """

    params = [tran_with_id]

    cursor.execute(sql, params)

    data = [
        {
            "id": row[0],
            "name": row[1],
            "method": row[2]
        }
        for row in cursor.fetchall()
    ]
    return JsonResponse({
        "data": data,
    })

def save_transaction_with_user(request):
    if request.method == "POST":
        transactionmainheads_id = request.POST.get('transactionmainheads_id')
        tran_method = request.POST.get('tran_method')
        tran_with = request.POST.get('tran_with')

        cursor = connection.cursor()
        sql = """
            INSERT INTO transaction__withs (tran_type, tran_method, tran_with_name)
            VALUES (%s, %s, %s)
        """
        params = [transactionmainheads_id, tran_method, tran_with]

        cursor.execute(sql, params)

        return JsonResponse({"status":"success","message":"Save Successfull!"})
    
    return JsonResponse({"status":"faield","message":"Invalid entry!"})

def update_transaction_with_user(request):
    if request.method == "POST":      
        transactionmainheads_id = request.POST.get('transactionmainheads_id')
        tran_method = request.POST.get('tran_method')
        tran_with_id = request.POST.get('tran_with_id') # WHERE
        tran_with = request.POST.get('tran_with')

        cursor = connection.cursor()
        sql = """
            UPDATE transaction__withs 
            SET tran_type = %s, tran_method = %s, tran_with_name = %s
            WHERE id = %s
        """
        params = [transactionmainheads_id, tran_method, tran_with, tran_with_id]

        cursor.execute(sql, params)

        return JsonResponse({"status":"success","message":"Updated Successfull!"})
    
    return JsonResponse({"status":"faield","message":"Invalid entry!"})

def delete_transaction_with_user(request):
    tran_with_id = request.POST.get('tran_with_id')

    print(tran_with_id);
    cursor = connection.cursor()
    sql = """
        DELETE 
        FROM transaction__withs
        WHERE id = %s
    """

    params = [tran_with_id]

    cursor.execute(sql, params)

    return JsonResponse({"status":"remove","message":"Remove Successfull!"})
