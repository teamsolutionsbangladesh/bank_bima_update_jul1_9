import json
import traceback
from django.shortcuts import render
from django.http import JsonResponse
from django.db import connection, transaction
from django.utils import timezone

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


# =========================================================================
# 📋 1. DOCTOR RESOURCE DIRECTORIES MATRIX LISTING (HTML VIEW 1)
# =========================================================================
def doctor_list_view(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM doctors_info ORDER BY id DESC")
        doctors = dict_fetchall(cursor)
    return render(request, 'doctors/doctor_list.html', {'doctors': doctors})


# =========================================================================
# 📝 2. SPLIT ENTRY & EDIT FORM COMPONENT GENERAL VIEW (HTML VIEW 2)
# =========================================================================
def doctor_form_view(request, pk=None):
    doctor_data = None
    if pk:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM doctors_info WHERE id = %s", [pk])
            doctor_data = dict_fetchone(cursor)
            
    # Submitting list dataset context on the right side pane dynamically
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM doctors_info ORDER BY id DESC")
        all_doctors = dict_fetchall(cursor)
            
    return render(request, 'doctors/doctor_form.html', {
        'doctor': doctor_data,
        'doctors': all_doctors,
        'edit_id': pk
    })


# =========================================================================
# 🔍 3. FETCH SINGLE DOCTOR PROFILE DATA ENGINE (AJAX GET FOR COMBOS)
# =========================================================================
def fetch_doctor_profile(request):
    doc_id = request.GET.get('id')
    if not doc_id:
        return JsonResponse({'error': 'Missing target context ID'}, status=400)
        
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM doctors_info WHERE id = %s AND is_active = 1", [doc_id])
        doctor = dict_fetchone(cursor)
        
    if doctor:
        return JsonResponse(doctor)
    return JsonResponse({'error': 'Target provider record profile not found'}, status=404)


# =========================================================================
# 💾 4. STORE NEW PROFILES LAYOUT DATA STRUCTURE (AJAX POST)
# =========================================================================
# doctors/views.py er vethor raw insert operational query model replace sequence update logic:
def store_doctor(request):
    if request.method != "POST":
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)
    
    try:
        data = request.POST
        current_now = timezone.now()

        name_val = data.get('name', '').strip()
        specialization_val = data.get('specialization', '').strip() or None
        doctor_type_val = data.get('doctor_type', '').strip() or 'diagnosis'
        chamber_val = data.get('chamber', '').strip() or None
        phone_val = data.get('phone', '').strip() or None 

        if not name_val:
            return JsonResponse({'success': False, 'error': 'Doctor name required'}, status=400)

        with transaction.atomic():
            with connection.cursor() as cursor:
                
                # =========================================================
                # STEP 1: CALCULATE NEXT BASELINE AUTOINCREMENT SEED COUNTER
                # =========================================================
                cursor.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM doctors_info")
                next_auto_id = cursor.fetchone()[0]
                formatted_doc_id = f"DOC{next_auto_id:09d}"

                # =========================================================
                # STEP 2: INSERT PRIMARY DOCTOR RECORD
                # =========================================================
                insert_doctor_sql = """
                    INSERT INTO doctors_info (
                        id, custom_doc_id, name, specialization, doctor_type, chamber, is_active, created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(insert_doctor_sql, [
                    next_auto_id, formatted_doc_id, name_val, specialization_val, doctor_type_val, chamber_val, 1, current_now
                ])

                # =========================================================
                # STEP 3: REFLECT DATA MIRROR SYNC PIPELINE INTO user__infos
                # =========================================================
                DOCTOR_ROLE_ID = 4  
                TRAN_USER_TYPE_ID = None  

                TRAN_METHOD = doctor_type_val or 'diagnosis'
                TRAN_WITH_ID = next_auto_id 

                # 🔥 FIX: Explicitly passing NULL (None) value mapping into 'tran_method' field definition constraints
                insert_user_info_sql = """
                    INSERT INTO user__infos (
                        user_id, login_user_id, title, user_name, user_phone, 
                        user_role, tran_user_type, tran_method, tran_with_id, status, added_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(insert_user_info_sql, [
                    formatted_doc_id,
                    formatted_doc_id,
                    "Dr.",
                    name_val,
                    phone_val,
                    DOCTOR_ROLE_ID,
                    TRAN_USER_TYPE_ID,
                    TRAN_METHOD,
                    TRAN_WITH_ID,
                    1,
                    current_now
                ])
                return JsonResponse({'success': True, 'id': next_auto_id, 'custom_doc_id': formatted_doc_id})

    except Exception as e:
        print("========!!! COREDATA CRASH TRACEBACK (DOCTOR STORE MIRROR) !!!========")
        traceback.print_exc()
        print("==========================================================================")
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

# =========================================================================
# 🔄 5. UPDATE EXISTING REGISTERED PROFILES CONTEXT (AJAX POST)
# =========================================================================
def update_doctor(request, pk):
    if request.method != "POST":
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)
        
    try:
        data = request.POST

        with transaction.atomic():
            with connection.cursor() as cursor:
                
                # Check record profile presence safely
                cursor.execute("SELECT id FROM doctors_info WHERE id = %s", [pk])
                if not cursor.fetchone():
                    return JsonResponse({'success': False, 'error': 'Target dynamic map missing'}, status=404)

                # Execute explicit target cell updates
                update_sql = """
                    UPDATE doctors_info SET 
                        name = %s, 
                        specialization = %s, 
                        chamber = %s, 
                        doctor_type = %s
                    WHERE id = %s
                """
                cursor.execute(update_sql, [
                    data.get('name'),
                    data.get('specialization') or None,
                    data.get('chamber') or None,
                    data.get('doctor_type') or 'diagnosis',
                    pk
                ])

                return JsonResponse({'success': True})
                
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


# =========================================================================
# ❌ 6. UNLINK / TERMINATE PROFESSIONAL LOG GRID ENTRIES (AJAX POST)
# =========================================================================
def delete_doctor(request, pk):
    if request.method != "POST":
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)
    try:
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM doctors_info WHERE id = %s", [pk])
                return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
    

# =========================================================================
# 🔍 7. REALTIME SYSTEM LOOKUP COMBO MODULES (SELECT2 LOOKUPS)
# =========================================================================
def get_doctors_lookup_combo(request):
    """🧠 System Search Loop: Query parameters filter doctors via key constraints"""
    q = request.GET.get('term', '').strip()
    with connection.cursor() as cursor:
        sql = """
            SELECT id, name AS name, specialization, chamber 
            FROM doctors_info 
            WHERE name LIKE %s OR CAST(id AS CHAR) LIKE %s
            LIMIT 20;
        """
        cursor.execute(sql, [f"%{q}%", f"%{q}%"])
        columns = [col[0] for col in cursor.description]
        data = [dict(zip(columns, row)) for row in cursor.fetchall()]
    return JsonResponse({"results": data}, safe=False)


def get_sr_lookup_combo(request):
    """🧠 System Search Loop: Query parameters filter SR representatives via key constraints"""
    q = request.GET.get('term', '').strip()
    with connection.cursor() as cursor:
        sql = """
            SELECT id, sr_name AS name 
            FROM item__sr_agents 
            WHERE sr_name LIKE %s OR CAST(id AS CHAR) LIKE %s
            LIMIT 20;
        """
        cursor.execute(sql, [f"%{q}%", f"%{q}%"])
        columns = [col[0] for col in cursor.description]
        data = [dict(zip(columns, row)) for row in cursor.fetchall()]
    return JsonResponse({"results": data}, safe=False)