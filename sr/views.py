import json
import traceback
from django.shortcuts import render
from django.http import JsonResponse
from django.db import connection, transaction
from django.utils import timezone

def dict_fetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def dict_fetchone(cursor):
    columns = [col[0] for col in cursor.description]
    row = cursor.fetchone()
    if row:
        return dict(zip(columns, row))
    return None

# 📋 1. SR MATRIX LISTING VIEW
def sr_list_view(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM item__sr_agents ORDER BY id DESC")
        sr_agents = dict_fetchall(cursor)
    return render(request, 'sr/sr_list.html', {'sr_agents': sr_agents})

# 📝 2. SPLIT ENTRY & EDIT FORM VIEW 
def sr_form_view(request, pk=None):
    sr_data = None
    if pk:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM item__sr_agents WHERE id = %s", [pk])
            sr_data = dict_fetchone(cursor)
            
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM item__sr_agents ORDER BY id DESC")
        all_agents = dict_fetchall(cursor)
            
    return render(request, 'sr/sr_form.html', {
        'sr': sr_data,
        'sr_agents': all_agents,
        'edit_id': pk
    })

# 🔍 3. FETCH SINGLE SR PROFILE DATA
def fetch_sr_profile(request):
    sr_id = request.GET.get('id')
    if not sr_id:
        return JsonResponse({'error': 'Missing target context ID'}, status=400)
        
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM item__sr_agents WHERE id = %s AND is_active = 1", [sr_id])
        agent = dict_fetchone(cursor)
        
    if agent:
        return JsonResponse(agent)
    return JsonResponse({'error': 'Target agent record profile not found'}, status=404)

# 💾 4. STORE NEW PROFILES (AJAX POST)
# sr/views.py application execution handler block data mapping functions check update logic:
def store_sr(request):
    if request.method != "POST":
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)
    try:
        data = request.POST
        current_now = timezone.now()

        with transaction.atomic():
            with connection.cursor() as cursor:
                name_val = data.get('name', '').strip()
                if not name_val:
                    return JsonResponse({'success': False, 'error': 'Representative name required'}, status=400)

                # Step 1: Next primary database schema serial trace counter seed tracking
                cursor.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM item__sr_agents")
                next_sr_id = cursor.fetchone()[0]

                # Step 2: Perfect exact 12 character corporate padding string alignment formula assignment 
                formatted_sr_id_string = f"SR{next_sr_id:010d}"

                insert_sql = """
                    INSERT INTO item__sr_agents (
                        id, custom_sr_id, name, company_name, commission_percentage, is_active, created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(insert_sql, [
                    next_sr_id,
                    formatted_sr_id_string, # Save literal direct code token parameters structure mapping text entries 
                    name_val,
                    data.get('company_name') or None,
                    data.get('commission_percentage') or 0.00,
                    1,
                    current_now
                ])
                return JsonResponse({'success': True, 'id': next_sr_id})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

# 🔄 5. UPDATE EXISTING REGISTERED PROFILES (AJAX POST)
def update_sr(request, pk):
    if request.method != "POST":
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)
    try:
        data = request.POST
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("SELECT id FROM item__sr_agents WHERE id = %s", [pk])
                if not cursor.fetchone():
                    return JsonResponse({'success': False, 'error': 'Target dynamic map missing'}, status=404)

                update_sql = """
                    UPDATE item__sr_agents SET 
                        name = %s, 
                        company_name = %s, 
                        commission_percentage = %s
                    WHERE id = %s
                """
                cursor.execute(update_sql, [
                    data.get('name'),
                    data.get('company_name') or None,
                    data.get('commission_percentage') or 0.00,
                    pk
                ])
                return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

# ❌ 6. UNLINK / TERMINATE PROFILE ENTRIES (AJAX POST)
def delete_sr(request, pk):
    if request.method != "POST":
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)
    try:
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM item__sr_agents WHERE id = %s", [pk])
                return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)