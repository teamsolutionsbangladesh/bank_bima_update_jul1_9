from django.db import connection
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import render, redirect
import random
from django.shortcuts import render, redirect
from core.models import CompanyDetails, LocationInfos, UserInfos
# from .models import TransactionMainHeads, TransactionWiths, TransactionGroupes


# SUBJECT

def add_page_init(request):
    company_id = request.session.get("company_id")
    if not company_id and request.session.get("company_name"):
        company = CompanyDetails.objects.filter(company_name=request.session.get("company_name")).order_by("-id").first()
        company_id = company.id if company else ""
    return render(request, 'page_init/page_init.html', {
        "fixed_location_id": request.session.get("loc_id") or "",
        "fixed_company_id": company_id or "",
    })


def _resolve_company_id(request):
    company_id = request.session.get("company_id")
    if company_id:
        return company_id
    company_name = request.session.get("company_name")
    if company_name:
        company = CompanyDetails.objects.filter(company_name=company_name).order_by("-id").first()
        if company:
            request.session["company_id"] = company.id
            return company.id
    company = CompanyDetails.objects.order_by("id").first()
    if company:
        request.session["company_id"] = company.id
        return company.id
    return None

def save_page_init(request):
    if request.method == "POST":
        def clean_value(value):
            return value if value not in ("", None, "null", "undefined") else None

        location_id = clean_value(request.POST.get("location_id")) or request.session.get("loc_id") or 1
        company_id = clean_value(request.POST.get("company_id")) or _resolve_company_id(request)
        status = clean_value(request.POST.get("status")) or 1
        page_id = clean_value(request.POST.get('page_id'))
        transactionmainheads = clean_value(request.POST.get('transactionmainheads'))
        load_head_all = clean_value(request.POST.get('load_head_all')) or 0
        transaction_with_method = clean_value(request.POST.get('transaction_with_method'))
        transaction_with = clean_value(request.POST.get('transaction_with'))
        transaction_method = clean_value(request.POST.get('transaction_method'))
        tran_group = clean_value(request.POST.get('tran_group'))

        print("DEBUG >>>>>>>>>>>>>>>>>>>>>>>>>>> ", page_id);        
        print("DEBUG >>>>>>>>>>>>>>>>>>>>>>>>>>> ", transactionmainheads);
        print("DEBUG >>>>>>>>>>>>>>>>>>>>>>>>>>> ", load_head_all);
        print("DEBUG >>>>>>>>>>>>>>>>>>>>>>>>>>> ", transaction_with_method);
        print("DEBUG >>>>>>>>>>>>>>>>>>>>>>>>>>> ", transaction_with);
        print("DEBUG >>>>>>>>>>>>>>>>>>>>>>>>>>> ", transaction_method);
        print("DEBUG >>>>>>>>>>>>>>>>>>>>>>>>>>> ", tran_group);

        if not page_id:
            return JsonResponse({"status":"failed","message":"Page ID required"}, status=400)

        try:
            cursor = connection.cursor()
            cursor.execute("SELECT id FROM page_init WHERE page_id = %s LIMIT 1", [page_id])
            existing = cursor.fetchone()

            if existing:
                sql = """
                    UPDATE page_init
                    SET tran_main_head_id = %s,
                        location_id = %s,
                        company_id = %s,
                        load_head_all = %s,
                        user_tran_method = %s,
                        user_tran_with_id = %s,
                        tran_method = %s,
                        tran_group_id = %s,
                        status = %s
                    WHERE page_id = %s
                """
                params = [
                    transactionmainheads,
                    location_id,
                    company_id,
                    load_head_all,
                    transaction_with_method,
                    transaction_with,
                    transaction_method,
                    tran_group,
                    status,
                    page_id,
                ]
                cursor.execute(sql, params)
                return JsonResponse({"status":"success","message":"Updated Successfull!"})

            sql = """
                INSERT INTO page_init
                (page_id,
                location_id,
                company_id,
                tran_main_head_id,
                load_head_all,
                user_tran_method,
                user_tran_with_id,
                tran_method,
                tran_group_id,
                status
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            params = [
                page_id,
                location_id,
                company_id,
                transactionmainheads,
                load_head_all,
                transaction_with_method,
                transaction_with,
                transaction_method,
                tran_group,
                status,
            ]

            cursor.execute(sql, params)

            return JsonResponse({"status":"success","message":"Save Successfull!"})
        except IntegrityError as exc:
            return JsonResponse({"status":"failed","message":str(exc)}, status=400)
        except Exception as exc:
            return JsonResponse({"status":"failed","message":str(exc)}, status=500)
    
    return JsonResponse({"status":"faield","message":"Invalid entry!"})

def update_page_init(request):
    if request.method == "POST":
        def clean_value(value):
            return value if value not in ("", None, "null", "undefined") else None

        page_id = request.POST.get('page_id')
        transactionmainheads = clean_value(request.POST.get('transactionmainheads'))
        location_id = clean_value(request.POST.get("location_id")) or request.session.get("loc_id") or 1
        company_id = clean_value(request.POST.get("company_id")) or _resolve_company_id(request)
        status = clean_value(request.POST.get("status")) or 1
        transaction_with_method = request.POST.get('transaction_with_method')
        transaction_with = request.POST.get('transaction_with')
        transaction_method = request.POST.get('transaction_method')
        tran_group = request.POST.get('tran_group')

        cursor = connection.cursor()
        sql = """
            UPDATE page_init 
            SET 
            tran_main_head_id = %s,
            location_id = %s,
            company_id = %s,
            user_tran_method = %s,
            user_tran_with_id = %s,
            tran_method = %s,
            tran_group_id = %s,
            status = %s
            WHERE page_id = %s

        """
        params = [             
            transactionmainheads,
            location_id,
            company_id,
            transaction_with_method,
            transaction_with,
            transaction_method,
            tran_group,
            status,
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


