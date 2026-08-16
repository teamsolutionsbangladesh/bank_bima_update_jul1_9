from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from core.models import CompanyTypes, CompanyDetails
from django.conf import settings
from django.core.files.storage import FileSystemStorage


# ==============================
# COMPANY TYPES (UNCHANGED)
# ==============================

def company_types_list(request):
    company_types = CompanyTypes.objects.all().order_by('id')
    return render(request, 'company/company_types_list.html', {
        'company_types': company_types
    })


@csrf_exempt
def create_company_type(request):
    if request.method == "POST":
        name = request.POST.get("name")
        status = int(request.POST.get("status", 1))
        if not name:
            return JsonResponse({"success": False, "message": "Name required"})
        ct = CompanyTypes.objects.create(name=name, status=status)
        return JsonResponse({"success": True, "id": ct.id, "name": ct.name})


@csrf_exempt
def update_company_type(request, pk):
    if request.method == "POST":
        ct = get_object_or_404(CompanyTypes, pk=pk)
        ct.name = request.POST.get("name")
        ct.status = request.POST.get("status")
        ct.save()
        return JsonResponse({"success": True})

    
@csrf_exempt
def delete_company_type(request, pk):
    if request.method == "POST":
        company = get_object_or_404(CompanyTypes, pk=pk)
        company.delete()
        return JsonResponse({'success': True})


# ==============================
# COMPANY DETAILS (FIXED LIKE TYPES)
# ==============================

def company_details_list(request):
    types = CompanyTypes.objects.filter(status=1)
    details = CompanyDetails.objects.all()
    return render(request, 'company/company_details_list.html', {
        'types': types,
        'details': details
    })


@csrf_exempt
def create_company_detail(request):
    if request.method == "POST":
        name = request.POST.get("company_name")
        type_id = request.POST.get("company_type")
        email = request.POST.get("company_email")
        phone = request.POST.get("company_phone")
        address = request.POST.get("address")
        domain = request.POST.get("domain")
        status = int(request.POST.get("status", 1))

        if not name or not type_id:
            return JsonResponse({'success': False, 'message': 'Name and Type are required'})

        ctype = get_object_or_404(CompanyTypes, id=type_id)

        # Auto-generate company_id as CO + 9-digit zero-padded number
        last = CompanyDetails.objects.all().order_by('id').last()
        if last and last.company_id.startswith("CO"):
            last_num = int(last.company_id[2:])
            next_id = f"CO{last_num + 1:09d}"
        else:
            next_id = "CO000000001"

        # Handle logo upload
        logo_file = request.FILES.get("logo")
        logo_name = None
        if logo_file:
            fs = FileSystemStorage()
            logo_name = fs.save(logo_file.name, logo_file)
            logo_url = fs.url(logo_name)
        else:
            logo_url = None

        company = CompanyDetails.objects.create(
            company_id=next_id,
            company_name=name,
            company_type=ctype,
            company_email=email,
            company_phone=phone,
            address=address,
            domain=domain,
            logo=logo_name,  # store filename
            status=status
        )

        return JsonResponse({
            'success': True,
            'id': company.id,
            'sl': CompanyDetails.objects.count(),
            'company_id': company.company_id,
            'company_name': company.company_name,
            'company_type_id': ctype.id,
            'company_type_name': ctype.name,
            'company_email': company.company_email,
            'company_phone': company.company_phone,
            'address': company.address,
            'domain': company.domain,
            'logo_url': logo_url,  # send full URL to JS
            'status': company.status
        })


@csrf_exempt
def update_company_detail(request, id):
    if request.method == "POST":
        company = get_object_or_404(CompanyDetails, id=id)
        name = request.POST.get("company_name")
        type_id = request.POST.get("company_type")
        email = request.POST.get("company_email")
        phone = request.POST.get("company_phone")
        address = request.POST.get("address")
        domain = request.POST.get("domain")
        status = int(request.POST.get("status", 1))

        if not name or not type_id:
            return JsonResponse({'success': False, 'message': 'Name and Type are required'})

        ctype = get_object_or_404(CompanyTypes, id=type_id)

        # Handle logo upload
        logo_file = request.FILES.get("logo")
        logo_name = company.logo  # keep old if not updated
        if logo_file:
            fs = FileSystemStorage()
            logo_name = fs.save(logo_file.name, logo_file)
            logo_url = fs.url(logo_name)
        else:
            logo_url = company.logo.url if company.logo else None

        company.company_name = name
        company.company_type = ctype
        company.company_email = email
        company.company_phone = phone
        company.address = address
        company.domain = domain
        company.logo = logo_name
        company.status = status
        company.save()

        return JsonResponse({'success': True, 'logo_url': logo_url})


@csrf_exempt
def delete_company_detail(request, id):
    if request.method == "POST":
        company = get_object_or_404(CompanyDetails, id=id)
        company.delete()
        return JsonResponse({'success': True})
