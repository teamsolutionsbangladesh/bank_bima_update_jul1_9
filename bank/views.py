from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone
from .models import Banks, LocationInfos
from django.views.decorators.csrf import csrf_exempt

def bank_page(request):
    banks = Banks.objects.filter(status=1).order_by('id')
    locations = LocationInfos.objects.filter(status=1).order_by('division')
    return render(request, 'bank/bank.html', {'banks': banks, 'locations': locations})
@csrf_exempt
def bank_store(request):
    # 1️⃣ Generate Bank ID
    last_bank = Banks.objects.order_by('-id').first()
    last_number = int(last_bank.user_id[1:]) if last_bank else 0  # skip 'B'
    new_number = last_number + 1
    bank_id = f"B{new_number:09d}"

    # 2️⃣ Create Bank without using request.POST['user_id']
    Banks.objects.create(
        user_id=bank_id,               # <-- use generated ID
        name=request.POST['name'],
        email=request.POST['email'],
        phone=request.POST['phone'],
        loc_id=request.POST.get('loc'),
        address=request.POST.get('address'),
        status=1,
        added_at=timezone.now()
    )

    # 3️⃣ Return JSON response
    return JsonResponse({'success': True, 'bank_id': bank_id})

def bank_fetch(request):
    bank_id = request.GET.get('id')
    if not bank_id:
        return JsonResponse({'error':'No ID provided'}, status=400)
    bank = Banks.objects.get(id=bank_id)
    return JsonResponse({
        'id': bank.id,
        'user_id': bank.user_id,
        'name': bank.name,
        'email': bank.email,
        'phone': bank.phone,
        'loc': bank.loc.id if bank.loc else '',
        'address': bank.address
    })

def bank_update(request):
    bank = Banks.objects.get(id=request.POST['id'])
    bank.user_id = request.POST['user_id']
    bank.name = request.POST['name']
    bank.email = request.POST['email']
    bank.phone = request.POST['phone']
    bank.loc_id = request.POST.get('loc')
    bank.address = request.POST.get('address')
    bank.updated_at = timezone.now()
    bank.save()
    return JsonResponse({'success': True})

def bank_delete(request):
    Banks.objects.filter(id=request.POST['id']).update(status=0)
    return JsonResponse({'success': True})
