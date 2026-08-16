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

def transaction_method_combo(request):
    tran_main_head_id = request.GET.get('tran_main_head_id')
    cursor = connection.cursor()

    sql = """
        SELECT 
        distinct tran_method
        FROM transaction__groupes
        WHERE tran_groupe_type = %s
        AND status = 1;

    """
    params = [tran_main_head_id]

    cursor.execute(sql, params)
    # data = dictfetchall(cursor)

    data  = [
        {
            "method": row[0]
        }
        for row in cursor.fetchall()
    ]    
    print("DEBUG",data)

    return JsonResponse({
        "transaction_method_combo": data
    })

def transaction_group_combo(request):
    tran_main_head_id = request.GET.get('tran_main_head_id')
    transaction_method = request.GET.get('transaction_method')

    print(tran_main_head_id);
    print(transaction_method);
    
    cursor = connection.cursor()

    sql = """
        SELECT
        s.id AS id,
        s.tran_groupe_name AS name
        FROM transaction__groupes s
        WHERE s.tran_groupe_type = %s 
        AND s.tran_method = %s
        AND s.status = 1
        ORDER BY s.tran_groupe_name;
    """
    params = [tran_main_head_id, transaction_method]

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
        "transaction_group_combo": data
    })

def transaction_with_combo(request):
    tran_main_head_id = request.GET.get('tran_main_head_id')
    tran_with_method = request.GET.get('tran_with_method')

    cursor = connection.cursor()

    sql = """
        SELECT
        s.id AS id,
        s.tran_with_name AS name
        FROM transaction__withs s
        WHERE s.tran_type = %s AND tran_method = %s AND s.status = 1
        ORDER BY s.tran_with_name;

    """
    params = [tran_main_head_id, tran_with_method]

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
        "transaction_with_combo": data
    })


# def transaction_with_method_combo(request):
#     main_head_id = request.GET.get('main_head_id')
#     cursor = connection.cursor()

#     sql = """
#         SELECT distinct tran_method
#         FROM transaction__withs
#         WHERE tran_type = %s;

#     """
#     params = [main_head_id]

#     cursor.execute(sql, params)
#     # data = dictfetchall(cursor)

#     data  = [
#         {
#             "method": row[0]
#         }
#         for row in cursor.fetchall()
#     ]    
#     print("DEBUG",data)

#     return JsonResponse({
#         "transaction_with_method_combo": data
#     })

def transaction_with_method_combo(request):
    tran_main_head_id = request.GET.get('tran_main_head_id')
    cursor = connection.cursor()

    sql = """
        SELECT 
        distinct tran_method
        FROM transaction__withs
        WHERE tran_type = %s;

    """
    params = [tran_main_head_id]

    cursor.execute(sql, params)
    # data = dictfetchall(cursor)

    data  = [
        {
            "method": row[0]
        }
        for row in cursor.fetchall()
    ]    
    print("DEBUG",data)

    return JsonResponse({
        "transaction_with_method_combo": data
    })


def transaction_with_user_combo(request):
    tran_main_head_id = request.GET.get('tran_main_head_id')
    # method = request.GET.get('method')
    tran_with_id = request.GET.get('tran_with_id')

    print("DEBUG MAIN HEAD ID >>>>>> ",tran_main_head_id)
    # print("DEBUG METHOD >>>>>> ",method)
    print("DEBUG TRAN WITH ID >>>>>> ",tran_with_id)

    cursor = connection.cursor()

    sql = """
        SELECT
        s.id AS id,
        s.user_name AS name
        FROM user__infos s
        WHERE s.tran_user_type = %s AND s.tran_with_id = %s
        ORDER BY s.user_name;

    """
    # AND s.tran_method = %s
    params = [tran_main_head_id, tran_with_id]

    cursor.execute(sql, params)
    # data = dictfetchall(cursor)

    data  = [
        {
            "id": row[0],
            "user_name": row[1]
        }
        for row in cursor.fetchall()
    ]    
    print("DEBUG",data)

    return JsonResponse({
        "transaction_with_user_combo": data
    })

def user_role_combo(request):

    cursor = connection.cursor()

    sql = """
        SELECT
        s.id AS id,
        s.name AS name
        FROM roles s    
        
    """
    params = []

    cursor.execute(sql, params)

    data  = [
        {
            "id": row[0],
            "name": row[1]
        }
        for row in cursor.fetchall()
    ]    
    print("DEBUG",data)

    return JsonResponse({
        "user_role_combo": data
    })



def fetch_combo_data(request):
    # tran_main_head_id = request.GET.get('tran_main_head_id')
    # transaction_method = request.GET.get('transaction_method')

    # print(tran_main_head_id);
    # print(transaction_method);
    
    cursor = connection.cursor()

    sql = """
       SELECT
        s.id AS id,
        s.category_name AS name
        FROM item__categories s
        WHERE s.status = 1
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
        "fetchdata": data
    })


def get_transaction_main_heads_combo(request):
    # tran_main_head_id = request.GET.get('tran_main_head_id')
    # transaction_method = request.GET.get('transaction_method')

    # print(tran_main_head_id);
    # print(transaction_method);
    
    cursor = connection.cursor()

    sql = """
       SELECT
            s.id AS id,
            s.type_name AS name
        FROM transaction__main__heads s
        WHERE s.status = 1
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




