from django.shortcuts import render
from django.contrib.auth.decorators import login_required


def home(request):
    if request.user.is_authenticated:
        return render(request, 'core/home.html')
    return render(request, 'core/landing.html')
