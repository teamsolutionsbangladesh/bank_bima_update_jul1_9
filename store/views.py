from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone
from .models import Stores, LocationInfos

# Store Page
def store_page(request):
    stores = Stores.objects.filter(status=1).order_by('id')
    locations = LocationInfos.objects.filter(status=1).order_by('id')

    # create a dict: {id: upazila}
    loc_dict = {loc.id: loc.upazila for loc in locations}

    return render(request, 'store/store.html', {
        'stores': stores,
        'locations': locations,
        'loc_dict': loc_dict
    })

# Add Store
def store_store(request):
    store_name = request.POST.get('store_name')
    division = request.POST.get('division')
    location_id = request.POST.get('location_id')
    address = request.POST.get('address')

    Stores.objects.create(
        store_name=store_name,
        division=division,
        location_id=location_id,
        address=address,
        status=1,
        added_at=timezone.now()
    )

    return JsonResponse({'success': True})

# Fetch single store (for edit)
def store_fetch(request):
    store = Stores.objects.get(id=request.GET['id'])
    return JsonResponse({
        'id': store.id,
        'store_name': store.store_name,
        'division': store.division,
        'location_id': store.location_id,
        'address': store.address
    })

# Update store
def store_update(request):
    store = Stores.objects.get(id=request.POST['id'])
    store.store_name = request.POST['store_name']
    store.division = request.POST['division']
    store.location_id = request.POST['location_id']
    store.address = request.POST['address']
    store.updated_at = timezone.now()
    store.save()
    return JsonResponse({'success': True})

# Delete store
def store_delete(request):
    Stores.objects.filter(id=request.POST['id']).update(status=0)
    return JsonResponse({'success': True})
