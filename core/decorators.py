# core/decorators.py
from functools import wraps
from django.shortcuts import redirect

def user_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.session.get('user_id'):  # check your custom login session
            return view_func(request, *args, **kwargs)
        return redirect('login')  # no ?next= appended
    return wrapper
