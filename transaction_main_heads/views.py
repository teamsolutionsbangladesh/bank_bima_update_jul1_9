from django.shortcuts import render
from django.db import connection

# Create your views here.
from django.utils import timezone
from django.http import JsonResponse


def get_transaction_main_heads_combo(request):

    cursor = connection.cursor()

    sql = """
        SELECT
        s.id AS id,
        s.type_name AS type_name
        FROM transaction__main__heads s
        ORDER BY s.type_name;
    """
    params = []

    cursor.execute(sql, params)
    # data = dictfetchall(cursor)

    data  = [
        {
            "id": row[0],
            "name": row[1]
        }
        for row in cursor.fetchall()
    ]    
    print("DEBUG",data)

    return JsonResponse({
        "transaction_main_heads_combo": data
    })

def set_transaction_main_head_id(request):
    
    page_main_head_id = request.GET.get('page_main_head_id')

    print("DEBUG-------======>>>>>>>>>>>>",page_main_head_id)

    cursor = connection.cursor()

    sql = """
        SELECT
        s.tran_main_head_id AS tran_main_head_id,
        s.user_tran_with_id AS user_tran_with_id,
        s.tran_group_id AS tran_group_id
        FROM page_init s
        WHERE s.page_id = %s

    """
    params = [page_main_head_id]

    cursor.execute(sql, params)
    # data = dictfetchall(cursor)

    data  = [
        {
            "tran_main_head_id": row[0],
            "user_tran_with_id": row[1],
            "tran_group_id": row[2]
        }
        for row in cursor.fetchall()
    ]    
    print("DEBUG------->>>>>>>>>>>>",data)

    return JsonResponse({
        "get_transaction_main_head_id": data
    })    
    