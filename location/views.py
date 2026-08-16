from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from .models import LocationInfos
from django.views.decorators.csrf import csrf_exempt

def location_page(request):
    locations = LocationInfos.objects.filter(status=1).order_by('-id')
    return render(request, 'location/location.html', {'locations': locations})
@csrf_exempt
def location_store(request):
    LocationInfos.objects.create(
        division=request.POST['division'],
        district=request.POST['district'],
        upazila=request.POST['upazila'],
        status=1,
        added_at=timezone.now()
    )
    return JsonResponse({'success': True})

def location_fetch(request):
    loc_id = request.GET.get('id')  # <-- safe way
    if not loc_id:
        return JsonResponse({'error':'No ID provided'}, status=400)

    loc = LocationInfos.objects.get(id=loc_id)
    return JsonResponse({
        'id': loc.id,
        'division': loc.division,
        'district': loc.district,
        'upazila': loc.upazila
    })


def location_update(request):
    loc = LocationInfos.objects.get(id=request.POST['id'])
    loc.division = request.POST['division']
    loc.district = request.POST['district']
    loc.upazila = request.POST['upazila']
    loc.updated_at = timezone.now()
    loc.save()
    return JsonResponse({'success': True})

def location_delete(request):
    LocationInfos.objects.filter(id=request.POST['id']).update(status=0)
    return JsonResponse({'success': True})
