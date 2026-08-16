from django.shortcuts import render

# Create your views here.
from django.utils import timezone
from django.http import JsonResponse
from .models import PaymentMethods

def payment_method_page(request):
    methods = PaymentMethods.objects.filter(status=1).order_by('id')
    return render(request, 'payment/payment_method.html', {'methods': methods})


def payment_method_store(request):
    PaymentMethods.objects.create(
        name=request.POST['name'],
        status=1,
        added_at=timezone.now()
    )
    return JsonResponse({'success': True})


def payment_method_fetch(request):
    m = PaymentMethods.objects.get(id=request.GET['id'])
    return JsonResponse({'id': m.id, 'name': m.name})


def payment_method_update(request):
    m = PaymentMethods.objects.get(id=request.POST['id'])
    m.name = request.POST['name']
    m.updated_at = timezone.now()
    m.save()
    return JsonResponse({'success': True})


def payment_method_delete(request):
    PaymentMethods.objects.filter(id=request.POST['id']).update(status=0)
    return JsonResponse({'success': True})
