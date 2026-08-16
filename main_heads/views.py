from django.shortcuts import render

# Create your views here.
from django.utils import timezone
from django.http import JsonResponse
from .models import TransactionMainHeads

def transaction_head_page(request):
    heads = TransactionMainHeads.objects.filter(status=1).order_by('id')
    return render(request, 'transaction_main_heads/transaction_main_heads.html', {'heads': heads})


def transaction_head_fetch(request):
    h = TransactionMainHeads.objects.get(id=request.GET['id'])
    return JsonResponse({'id': h.id, 'type_name': h.type_name})


def transaction_head_update(request):
    h = TransactionMainHeads.objects.get(id=request.POST['id'])
    h.type_name = request.POST['type_name']
    h.updated_at = timezone.now()
    h.save()
    return JsonResponse({'success': True})


def transaction_head_delete(request):
    TransactionMainHeads.objects.filter(id=request.POST['id']).update(status=0)
    return JsonResponse({'success': True})
