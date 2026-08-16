from datetime import timezone
import json
from django.http import JsonResponse
from django.forms import model_to_dict
from django.shortcuts import get_object_or_404, redirect, render
from .models import TransactionHeads, Stores, ItemManufacturers, LocationInfos, TransactionMainsTemps, TransactionDetailsTemps, TransactionMainHeads
from django.core.paginator import Paginator
from django.db import connection
from django.db import transaction
from django.db.models import F, Q
from django.db.models import Count, Case, When, IntegerField, Q
from datetime import datetime
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


def dictfetchall(cursor):
    """Return all rows from a cursor as a list of dicts."""
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]
# def medicine_list(request):
#     products = TransactionHeads.objects.all().defer('added_at', 'updated_at', 'expiry_date').order_by('id')
#     paginator = Paginator(products, 10)  # 10 per page
#     page_number = request.GET.get('page', 1)
#     page_obj = paginator.get_page(page_number)
    
#     return render(request, 'pharmacy/medicine_list.html', {
#         'products': page_obj
# })

def medicine_list(request):
    # 🔹 Get filters from GET parameters
    status_filter = request.GET.get('status', '')
    search = request.GET.get('search', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')

    # 🔹 Base queryset: only PURCHASE transactions
    data = TransactionMainsTemps.objects.all().order_by('tran_id')
    status_filter = request.GET.get('status')

    if status_filter in ['1', '0']:
        data = data.filter(status=int(status_filter))

    if search:
        data = data.filter(user_name__icontains=search)

    if start_date:
        data = data.filter(tran_date__date__gte=start_date)
    if end_date:
        data = data.filter(tran_date__date__lte=end_date)

    # 🔹 Pagination
    per_page = int(request.GET.get("per_page", 15))
    paginator = Paginator(data, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # 🔹 Per-page options for dropdown
    per_page_options = [15, 30, 50, 100, 500]
    stores = Stores.objects.all()
    context = {
        'data': page_obj,              # paginated data
        'status_filter': status_filter,
        'search': search,
        'start_date': start_date,
        'end_date': end_date,
        'per_page': per_page,
        'per_page_options': per_page_options,
        'paginator': paginator,
        'page_number': page_number,
        'stores': stores,
    }

    return render(request, 'pharmacy/medicine_list.html', context)



def medicine_add(request):
    # Add Medicine modal/page
    return render(request, 'pharmacy/add.html')


def product_search(request):
    q = request.GET.get('q', '').strip()
    offset = int(request.GET.get('offset', 0))
    # tran_group_id = request.GET.get('tran_group_id').strip()
    
    limit = 10

    cursor = connection.cursor()

    # If no search text → show all
    if q:
        # Search by name startswith
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
            LEFT JOIN item__manufacturers m ON t.manufacturer_id = m.id
            LEFT JOIN item__forms f ON t.form_id = f.id
            LEFT JOIN item__categories c ON t.category_id = c.id
            LEFT JOIN transaction__groupes tg ON t.groupe_id = tg.id
            LEFT JOIN transaction__main__heads tmh ON tmh.id = tg.tran_groupe_type
            WHERE t.tran_head_name LIKE %s
            AND (tmh.id = %s OR tmh.id IS NULL)
            ORDER BY t.id ASC
            LIMIT %s OFFSET %s
        """
        params = [f"{q}%", 6, limit, offset, tran_group_id]

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
            LEFT JOIN item__manufacturers m ON t.manufacturer_id = m.id
            LEFT JOIN item__forms f ON t.form_id = f.id
            LEFT JOIN item__categories c ON t.category_id = c.id
            LEFT JOIN transaction__groupes tg ON t.groupe_id = tg.id
            LEFT JOIN transaction__main__heads tmh ON tmh.id = tg.tran_groupe_type
            WHERE tmh.id = 6
            ORDER BY t.id
            LIMIT %s OFFSET %s
        """
        params = [limit, offset, tran_group_id]

    cursor.execute(sql, params)
    data = dictfetchall(cursor)

    print("SQL",sql)
    return JsonResponse({'results': data})

def purchase_list(request):
    # return render(request, 'pharmacy/medicine_list.html')
    return render(request, 'pharmacy/purchase_list.html')

def issue_list(request):
    return render(request, 'pharmacy/issue_list.html')

def purchase_list_load(request):
    q = request.GET.get('q', '').strip()
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    offset = int(request.GET.get('offset', 0))
    limit = 50

    cursor = connection.cursor()

    # If no search text → show all
    if q:
        # Search by name startswith
        # sql = """
        #     SELECT 
        #         m.id,
        #         m.tran_id AS tran_id,
        #         m.tran_date AS tran_date,
        #         m.tran_user AS tran_supplier,
        #         m.bill_amount AS bill_total,
        #         m.discount AS discount,
        #         m.net_amount AS net_total,
        #         m.receive AS advance,
        #         m.due_col AS due_collection,
        #         m.due_disc AS due_discount,
        #         m.due AS due
        #     FROM transaction__mains m
        #     ORDER BY m.id ASC
        #     LIMIT %s OFFSET %s
        # """
        # params = [limit, offset]        
        # # params = [f"{q}%", 6, limit, offset]  
              
        # sql = """
        #     SELECT 
        #         m.id,
        #         m.tran_id AS tran_id,
        #         m.tran_date AS tran_date,
        #         m.tran_user AS tran_supplier,
        #         m.bill_amount AS bill_total,
        #         m.discount AS discount,
        #         m.net_amount AS net_total,
        #         m.receive AS advance,
        #         m.due_col AS due_collection,
        #         m.due_disc AS due_discount,
        #         m.due AS due
        #     FROM transaction__mains m
        #     WHERE (%s IS NULL OR m.tran_date >= %s)
        #     AND (%s IS NULL OR m.tran_date <= %s)
        #     ORDER BY m.id
        #     LIMIT %s OFFSET %s
        # """
        # params = [start_date, start_date, end_date, end_date, limit, offset]

        sql = """
            SELECT 
                m.id,
                m.tran_id AS tran_id,
                m.tran_date AS tran_date,
                m.tran_user AS tran_supplier,
                m.bill_amount AS bill_total,
                m.discount AS discount,
                m.net_amount AS net_total,
                m.receive AS advance,
                m.due_col AS due_collection,
                m.due_disc AS due_discount,
                m.due AS due
            FROM transaction__mains m
            WHERE 1=1
        """

        params = []

        # date filter
        if start_date:
            sql += " AND DATE(m.tran_date) >= %s"
            params.append(start_date)

        if end_date:
            sql += " AND DATE(m.tran_date) <= %s"
            params.append(end_date)

        sql += " ORDER BY m.id DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])        


    else:
        # sql = """
        #     SELECT 
        #         m.id,
        #         m.tran_id AS tran_id,
        #         m.tran_date AS tran_date,
        #         m.tran_user AS tran_supplier,
        #         m.bill_amount AS bill_total,
        #         m.discount AS discount,
        #         m.net_amount AS net_total,
        #         m.receive AS advance,
        #         m.due_col AS due_collection,
        #         m.due_disc AS due_discount,
        #         m.due AS due
        #     FROM transaction__mains m
        #     ORDER BY m.id
        #     LIMIT %s OFFSET %s
        # """
        # params = [limit, offset]

        sql = """
            SELECT 
                m.id,
                m.tran_id AS tran_id,
                m.tran_date AS tran_date,
                m.tran_user AS tran_supplier,
                m.bill_amount AS bill_total,
                m.discount AS discount,
                m.net_amount AS net_total,
                m.receive AS advance,
                m.due_col AS due_collection,
                m.due_disc AS due_discount,
                m.due AS due
            FROM transaction__mains m
            WHERE 1=1
        """

        params = []

        # date filter
        if start_date:
            sql += " AND DATE(m.tran_date) >= %s"
            params.append(start_date)

        if end_date:
            sql += " AND DATE(m.tran_date) <= %s"
            params.append(end_date)

        sql += " ORDER BY m.id ASC LIMIT %s OFFSET %s"
        params.extend([limit, offset])

    cursor.execute(sql, params)
    data = dictfetchall(cursor)

    print("SQL",sql)
    return JsonResponse({'results': data})


def add_medicine(request):
    # Fetch only active stores (status=1)
    stores = Stores.objects.filter(status=1).order_by('store_name')
    return render(request, 'pharmacy/add.html', {'stores': stores})

def get_stores(request):
    stores = Stores.objects.filter(status=1).order_by('store_name')
    data = [
        {"id": s.id, "name": s.store_name}
        for s in stores
    ]
    return JsonResponse({"stores": data})

def get_suppliers(request):
    # Status 1 er manufacturer fetch
    manufacturers = ItemManufacturers.objects.filter(status=1).order_by('manufacturer_name')
    data = [{"id": m.id, "name": m.manufacturer_name} for m in manufacturers]
    return JsonResponse({"suppliers": data})

def get_divisions(request):
    # Only active locations (status=1)    
    divisions = LocationInfos.objects.filter(status=1).order_by('division')
    data = [{"id": d.id, "name": d.division} for d in divisions]
    return JsonResponse({"divisions": data})


def get_divisions_combo(request):

    cursor = connection.cursor()

    sql = """
        SELECT
        MIN(loc.id) AS id,
        loc.division
        FROM location__infos loc
        GROUP BY loc.division
        ORDER BY loc.division;
    """
    params = []

    cursor.execute(sql, params)
    data = dictfetchall(cursor)
    print("DEBUG",data)

    return JsonResponse({
        "divisions_combo": data
    }, safe=False)

def get_supplier_combo(request):

    cursor = connection.cursor()

    sql = """
        SELECT
        m.id AS id,
        m.manufacturer_name
        FROM item__manufacturers m
        ORDER BY m.manufacturer_name;
    """
    params = []

    cursor.execute(sql, params)
    data = dictfetchall(cursor)
    print("DEBUG",data)

    return JsonResponse({
        "supplier_combo": data
    })

def get_store_combo(request):

    cursor = connection.cursor()

    sql = """
        SELECT
        s.id AS id,
        s.store_name
        FROM stores s
        ORDER BY s.store_name;
    """
    params = []

    cursor.execute(sql, params)
    # data = dictfetchall(cursor)

    # data = [
    #     {"id": s.id, "store_name": s.store_name}
    #     for s in cursor.fetchall()
    # ]    

    data  = [
        {
            "id": row[0],
            "store_name": row[1]
        }
        for row in cursor.fetchall()
    ]    
    print("DEBUG",data)

    return JsonResponse({
        "store_combo": data
    })


def add_purchase_page(request):
    return render(request, 'pharmacy/add_4.html')

def add_issue_page(request):
    return render(request, 'pharmacy/issue.html')

@csrf_exempt   # AJAX hole thakbe, na hole CSRF use koro
def create_transaction_temp(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request"}, status=405)

    try:
        with transaction.atomic():  # 🔑 ensures atomic DB operation

            # Generate new transaction ID
            last_tran = TransactionMainsTemps.objects.order_by('-id').first()
            last_number = int(last_tran.tran_id[3:]) if last_tran else 0
            new_number = last_number + 1
            tran_id = f"TRA{new_number:09d}"  # total 12 digits

            # Get POST data
            bill_amount = float(request.POST.get("bill_amount") or 0)
            discount = float(request.POST.get("discount") or 0)
            net_amount = float(request.POST.get("net_amount") or 0)
            payment = float(request.POST.get("payment") or 0)
            due = float(request.POST.get("due") or 0)
            store_id = request.POST.get("store_id")
            supplier = request.POST.get("supplier")
            tran_method = request.POST.get("tran_method")
            location_name = request.POST.get("location")

            # Validate store
            if not store_id:
                return JsonResponse({"success": False, "message": "Store required"}, status=400)
            store = Stores.objects.get(id=store_id)

            # Location
            location = LocationInfos.objects.filter(division__iexact=location_name).first()
            loc_id = location.id if location else None

            # Transaction type
            tran_type_obj = TransactionMainHeads.objects.filter(type_name__iexact="Pharmacy").first()
            if not tran_type_obj:
                return JsonResponse({"success": False, "message": "Invalid transaction type"}, status=400)
            tran_type = tran_type_obj.id

            # 🔹 TABLE 1: transaction_mains_temps
            main_tran = TransactionMainsTemps.objects.create(
                tran_id=tran_id,
                tran_type=tran_type,
                tran_method=tran_method,
                tran_user=supplier,
                store=store,
                loc_id=loc_id,
                tran_date=timezone.now(),
                status=1,
                invoice=bill_amount,
                bill_amount=bill_amount,
                discount=discount,
                net_amount=net_amount,
                payment=payment,
                due=due
            )

            # 🔹 TABLE 2: transaction_details_temp (empty product row)
            TransactionDetailsTemps.objects.create(
                tran_id=tran_id,
                tran_type=tran_type,
                tran_method=tran_method,
                invoice=bill_amount,
                tran_user=supplier,
                amount=bill_amount,
                discount=discount,
                receive=payment,
                payment=payment,
                due=due,
                store=store,
                status=1,
                tran_date=timezone.now(),
                # product fields set to null/defaults
                tran_head_id=None,
                quantity_actual=0,
                quantity=0,
                quantity_issue=0,
                quantity_return=0,
                tot_amount=net_amount,
                cp=None,
                mrp=None
            )

            # Prepare response safely
            response_data = {
                "id": main_tran.id,
                "tran_id": main_tran.tran_id,
                "user_name": getattr(main_tran, 'user_name', supplier),
                "bill_amount": main_tran.bill_amount,
                "discount": main_tran.discount,
                "net_amount": main_tran.net_amount,
                "payment": main_tran.payment,
                "due": main_tran.due,
                "due_col": getattr(main_tran, 'due_col', 0),
                "due_disc": getattr(main_tran, 'due_disc', 0),
                "status": main_tran.status
            }

            return JsonResponse({"success": True, "tran_id": tran_id, "data": response_data})

    # except Stores.DoesNotExist:
    #     return JsonResponse({"success": False, "message": "Invalid store"}, status=400)
    except Exception as e:
        print("🔥 TRANSACTION ERROR:", e)
        return JsonResponse({"success": False, "error": str(e)}, status=500)
    
# def test_tran_id_generation(request):
#         store = Stores.objects.first()  # any store for testing

#         tran_id = generate_tran_id("TRA")

#         TransactionMainsTemps.objects.create(
#             tran_id=tran_id,
#             tran_type = 1,
#             store=store,
#             loc_id=store.location_id,
#             tran_date=timezone.now(),
#             status=1,
#             discount=0
#         )

#         return JsonResponse({
#             "message": "Tran ID generated & saved successfully",
#             "tran_id": tran_id
#         })


def get_transaction(request, tran_id):
    try:
        # 🔹 Fetch main transaction
        main = get_object_or_404(TransactionMainsTemps, tran_id=tran_id)

        # 🔹 Supplier name from tran_user
        supplier_name = ""
        if main.tran_user:
            supplier = ItemManufacturers.objects.filter(id=main.tran_user).first()
            if supplier:
                supplier_name = supplier.manufacturer_name

        # 🔹 Store info
        store_name = main.store.store_name if main.store else ""
        store_id = main.store.id if main.store else None

        # 🔹 Location
        location_name = ""
        if main.loc_id:
            loc = LocationInfos.objects.filter(id=main.loc_id).first()
            if loc:
                location_name = loc.division

        # 🔹 Transaction details
        details_qs = TransactionDetailsTemps.objects.filter(tran_id=tran_id)
        details = []
        for d in details_qs:
            # Get product name
            product_name = ""
            if d.tran_head_id:
                product = TransactionHeads.objects.filter(id=d.tran_head_id).first()
                if product:
                    product_name = product.tran_head_name
            details.append({
                "id": d.id,
                "name": product_name or "Unknown Product",
                "qty": d.quantity or 0,
                "cp": d.cp or 0,
                "total": d.tot_amount or 0,
                "unit": "PCS"  # optional, or fetch from d.unit_id if needed
            })

        # 🔹 Response
        response = {
            "success": True,
            "data": {
                "tran_id": main.tran_id,
                "supplier": supplier_name,
                "store_id": store_id,
                "store_name": store_name,
                "location": location_name,
                "tran_method": main.tran_method,
                "tran_date": main.tran_date.date().strftime("%Y-%m-%d"),
                "bill_amount": main.bill_amount or 0,
                "discount": main.discount or 0,
                "net_amount": main.net_amount or 0,
                "payment": main.payment or 0,
                "due": main.due or 0,
                "details": details
            }
        }

        return JsonResponse(response)

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})

    

# def get_temp_transaction(request, tran_id):
#     tran = TransactionMainsTemps.objects.get(id=tran_id)
#     medicines = tran.medicines.all().values("name","quantity","unit_price","total")

#     # fetch products from transaction__heads table
#     cursor = connection.cursor()
#     cursor.execute("SELECT tran_head_name AS name, '' AS generic_name, '' AS manufacture, '' AS form, quantity AS qty, cp, mrp FROM transaction__heads")
#     products = dictfetchall(cursor)

#     return JsonResponse({
#         "success": True,
#         "data": {
#             "location": tran.location,
#             "store_id": tran.store_id,
#             "date": tran.date,
#             "supplier_name": tran.supplier_name,
#             "payment_method": tran.tran_method,
#             "bill_amount": tran.bill_amount,
#             "discount": tran.discount,
#             "net_amount": tran.net_amount,
#             "payment": tran.payment,
#             "due": tran.due,
#             "medicines": list(medicines),
#             "products": products
#         }
#     })
    

    



# def get_temp_details(request, tran_id):
#     main = TransactionMainsTemps.objects.get(tran_id=tran_id)

#     items = TransactionDetailsTemps.objects.filter(tran_id=tran_id)

#     med_list = []
#     for i in items:
#         med_list.append({
#             "name": i.product_name,
#             "qty": i.qty,
#             "price": i.unit_price,
#             "total": i.total
#         })

#     return JsonResponse({
#         "tran_id": main.tran_id,
#         "store_id": main.store_id,
#         "location": main.loc_id,
#         "method": main.tran_method,
#         "bill_amount": main.bill_amount,
#         "discount": main.discount,
#         "net_amount": main.net_amount,
#         "payment": main.payment,
#         "due": main.due,
#         "medicines": med_list
#     })


@csrf_exempt  # AJAX POST

@transaction.atomic
def save_purchase(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request"}, status=405)

    try:
        data = json.loads(request.body)

        # ---- Form-level info ----
        store_id = data.get("store")
        location_id = data.get("location")
        tran_type_with = data.get("supplier")
        invoice = data.get("purchaseinvoice")
        payment_method = data.get("payment_method")
        bill_amount = data.get("bill_amount") or 0
        discount = data.get("discount") or 0
        net_amount = data.get("net_amount") or 0
        receive = data.get("receive") or 0
        due = data.get("due") or 0
        # tran_date = data.get("tran_date") or timezone.now().strftime("%Y-%m-%d %H:%M:%S")
        tran_date = data.get("tran_date")
        # Date & Time Both
        if tran_date:
            tran_date = datetime.combine(
                datetime.strptime(tran_date, "%Y-%m-%d").date(),
                timezone.localtime().time()
            )
        else:
            tran_date = timezone.localtime()
        
        # Only Date
        # if tran_date:
        #     tran_date = datetime.strptime(tran_date, "%Y-%m-%d")
        #     tran_date = timezone.make_aware(tran_date)
        # else:
        #     tran_date = timezone.now()

        print("tran_date from form:", tran_date)

        products = data.get("products", [])
        if not products:
            return JsonResponse({"success": False, "message": "No products selected"}, status=400)

        # ---- Generate transaction ID ----
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT tran_id 
                FROM transaction__mains
                WHERE tran_id LIKE 'PHR%'
                ORDER BY tran_id DESC
                LIMIT 1
            """)
            
            row = cursor.fetchone()

            if row:
                last_number = int(row[0][3:])  # remove PHR
            else:
                last_number = 0

            phr_code = "PHR" + str(last_number + 1).zfill(9)
        # ---- END of Generate transaction ID ----

        tran_type = 6
        status = 1

        # ---- Insert into transaction__mains ----
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO transaction__mains
                (tran_id, tran_type, tran_method, tran_type_with, store_id, 
                 loc_id, tran_date, status, invoice, bill_amount, discount, net_amount,
                 payment, due)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, [
                phr_code, tran_type, payment_method, tran_type_with, store_id,
                location_id, tran_date, status, invoice, bill_amount, 
                discount, net_amount, receive, due
            ])

        # ---- Prepare details data using index-style access ----
        details_data = []

        update_query = """
        UPDATE transaction__heads
        SET cp = %s, mrp = %s
        WHERE id = %s
        """
        update_data = []
        
        for row in products:
            details_data.append([
                # phr_code,         # tran_id
                # tran_type,        # tran_type_with
                # location_id,      # loc_id
                # store_id,         # store_id
                # tran_type_with,   # tran_user
                # row[0],           # tran_head_id
                # row[1],           # quantity_actual
                # row[1],           # quantity
                # 0,                # quantity_issue
                # 0,                # quantity_return   
                # row[4],           # cp
                # row[5],           # mrp
                # row[6],           # expiry_date
                # row[7],           # tot_amount                
                # tran_date,        # tran_date
                # status,           # status
                # discount,         # discount
                # receive,          # receive
                # receive,          # payment
                # due               # due

                phr_code,          # tran_id
                tran_type,        # tran_type_with
                payment_method,   # tran_method
                invoice,          # invoice
                location_id,      # loc_id
                tran_type_with,      # tran_user
                row[0],           # tran_head_id
                row[1],           # quantity_actual
                row[1],           # quantity
                0,                # quantity_issue
                0,                # quantity_return
                0,                # unit_id
                row[2],           # amount (cp)
                row[5],           # tot_amount
                row[2],           # cp
                row[3],           # mrp
                row[4],           # expiry_date
                store_id,         # store_id
                tran_date,        # tran_date
                status,           # status
                discount,           # discount
                receive,          # receive
                receive,          # payment
                due               # due

            ])

            # update product price
            # cursor.execute(update_query, [row[2], row[3], row[0]])

            update_data.append((row[2], row[3], row[0]))

        # ✅ new cursor
        with connection.cursor() as cursor:
            cursor.executemany(update_query, update_data)

        # ---- Insert into transaction__details ----
        # query = """
        #     INSERT INTO transaction__details
        #     (tran_id, tran_type, loc_id, store_id, tran_type_with, 
        #     tran_head_id, quantity_actual, quantity, quantity_issue, quantity_return,
        #     cp, mrp, expiry_date, tot_amount,
        #     tran_date, status, discount, receive, payment, due)
        #     VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        # """        
        query = """
            INSERT INTO transaction__details
            (tran_id, tran_type, tran_method, invoice, loc_id, tran_type_with,
             tran_head_id, quantity_actual, quantity, quantity_issue, quantity_return,
             unit_id, amount, tot_amount, cp, mrp, expiry_date, store_id,
             tran_date, status, discount, receive, payment, due)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """

        with connection.cursor() as cursor:
            cursor.executemany(query, details_data)

        return JsonResponse({"success": True, "tran_id": phr_code})

    except Exception as e:
        print("🔥 SAVE PURCHASE ERROR:", e)
        return JsonResponse({"success": False, "error": str(e)}, status=500)
    
@transaction.atomic
def save_issue(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request"}, status=405)

    try:
        data = json.loads(request.body)

        # ---- Form-level info ----
        store_id = data.get("store")
        location_id = data.get("location")
        tran_type_with = data.get("supplier")
        invoice = data.get("purchaseinvoice")
        payment_method = data.get("payment_method")
        bill_amount = data.get("bill_amount") or 0
        discount = data.get("discount") or 0
        net_amount = data.get("net_amount") or 0
        receive = data.get("receive") or 0
        due = data.get("due") or 0
        tran_date = data.get("tran_date") or timezone.now().strftime("%Y-%m-%d %H:%M:%S")

        products = data.get("products", [])
        if not products:
            return JsonResponse({"success": False, "message": "No products selected"}, status=400)

        # ---- Generate transaction ID ----
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT tran_id 
                FROM transaction__mains
                WHERE tran_id LIKE 'PHI%'
                ORDER BY tran_id DESC
                LIMIT 1
            """)
            
            row = cursor.fetchone()

            if row:
                last_number = int(row[0][3:])  # remove PHR
            else:
                last_number = 0

            phr_code = "PHI" + str(last_number + 1).zfill(9)
        # ---- END of Generate transaction ID ----

        tran_type = 6
        status = 1

        # ---- Insert into transaction__mains ----
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO transaction__mains
                (tran_id, tran_type, tran_method, tran_type_with, store_id, loc_id,
                 tran_date, status, invoice, bill_amount, discount, net_amount,
                 payment, due)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, [
                phr_code, tran_type, payment_method, tran_type_with, store_id,
                location_id, tran_date, status, bill_amount, bill_amount,
                discount, net_amount, receive, due
            ])

        # ---- Prepare details data using index-style access ----
        details_data = []
        for row in products:
            details_data.append([
                phr_code,         # tran_id
                tran_type,        # tran_type_with
                payment_method,   # tran_method
                invoice,          # invoice
                location_id,      # loc_id
                tran_type_with,   # tran_user
                row[0],           # tran_head_id
                row[1],           # quantity_actual
                0,                # quantity
                row[1],           # quantity_issue
                0,                # quantity_return
                row[5],           # unit_id
                row[2],           # amount (cp)
                row[3],           # tot_amount
                row[2],           # cp
                0,                # mrp (ignored)
                row[6],           # expiry_date
                store_id,         # store_id
                tran_date,        # tran_date
                status,           # status
                discount,         # discount
                receive,          # receive
                receive,          # payment
                due               # due
            ])

        # ---- Insert into transaction__details ----
        query = """
            INSERT INTO transaction__details
            (tran_id, tran_type, tran_method, invoice, loc_id, tran_type_with,
             tran_head_id, quantity_actual, quantity, quantity_issue, quantity_return,
             unit_id, amount, tot_amount, cp, mrp, expiry_date, store_id,
             tran_date, status, discount, receive, payment, due)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """

        with connection.cursor() as cursor:
            cursor.executemany(query, details_data)

        return JsonResponse({"success": True, "tran_id": phr_code})

    except Exception as e:
        print("🔥 SAVE PURCHASE ERROR:", e)
        return JsonResponse({"success": False, "error": str(e)}, status=500)    