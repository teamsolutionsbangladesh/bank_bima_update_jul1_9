from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone
from core.models import Corporates

def corporates_page(request):
    corporates = Corporates.objects.filter(status=1).order_by('id')  # ascending
    return render(request, 'corporates/corporates.html', {'corporates': corporates})

def corporate_store(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        discount = request.POST.get('discount')
        Corporates.objects.create(
            name=name,
            discount=discount,
            status=1,
            added_at=timezone.now()
        )
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

def corporate_fetch(request):
    corp = Corporates.objects.get(id=request.GET['id'])
    return JsonResponse({
        'id': corp.id,
        'name': corp.name,
        'discount': corp.discount
    })

def corporate_update(request):
    if request.method == 'POST':
        corp = Corporates.objects.get(id=request.POST['id'])
        corp.name = request.POST.get('name')
        corp.discount = request.POST.get('discount')
        corp.updated_at = timezone.now()
        corp.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

def corporate_delete(request):
    if request.method == 'POST':
        Corporates.objects.filter(id=request.POST['id']).update(status=0)
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})
