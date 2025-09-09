from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Please login to access this page")
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Please login to access this page")
            return redirect('login')
        if request.user.user_type != 3:  # 3 is Admin
            messages.error(request, "You don't have permission to access this page")
            return redirect('user_dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def staff_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Please login to access this page")
            return redirect('login')
        if request.user.user_type != 2:  # 2 is Staff
            messages.error(request, "You don't have permission to access this page")
            return redirect('user_dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped_view