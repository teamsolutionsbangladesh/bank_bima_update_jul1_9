from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from core.models import Roles
from django.views.decorators.csrf import csrf_exempt  # only if you want to exempt CSRF

# ==============================
# ROLES CRUD
# ==============================

def roles_list(request):
    """
    Display all roles in the system.
    """
    roles = Roles.objects.all().order_by('id')
    return render(request, 'users/roles_list.html', {
        'roles': roles
    })


def create_role(request):
    """
    Create a new role via AJAX POST.
    CSRF must be sent in header or data.
    """
    if request.method == "POST":
        name = request.POST.get("name")
        status = int(request.POST.get("status", 1))

        if not name:
            return JsonResponse({"success": False, "message": "Name is required"})

        role = Roles.objects.create(name=name, status=status)
        return JsonResponse({"success": True, "id": role.id, "name": role.name, "status": role.status})

    return JsonResponse({"success": False, "message": "Invalid request"})


def update_role(request, pk):
    """
    Update an existing role via AJAX POST.
    """
    if request.method == "POST":
        role = get_object_or_404(Roles, pk=pk)
        name = request.POST.get("name")
        status = int(request.POST.get("status", 1))

        if not name:
            return JsonResponse({"success": False, "message": "Name is required"})

        role.name = name
        role.status = status
        role.save()
        return JsonResponse({"success": True, "id": role.id, "name": role.name, "status": role.status})

    return JsonResponse({"success": False, "message": "Invalid request"})


def delete_role(request, pk):
    """
    Delete a role via AJAX POST.
    """
    if request.method == "POST":
        role = get_object_or_404(Roles, pk=pk)
        role.delete()
        return JsonResponse({"success": True})

    return JsonResponse({"success": False, "message": "Invalid request"})
