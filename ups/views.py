from django.shortcuts import render

from datetime import datetime
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from .models import Order, Delivery, Truck
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, logout
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.models import User
from django.db.models import Sum, Q
from django.template.defaulttags import register
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.conf import settings


# Create your views here.
def login_page(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if User.objects.filter(username=username).exists():
            user = authenticate(username=username, password=password)
            #user = authenticate(username=username, password=password)   # Django authenticate
            if user:
                auth_login(request, user)    #
                return HttpResponseRedirect('/')
            else:
                return render(request, 'login.html', {
                    'err_code': 'Invalid username/password'
                })
        else:
            # messages.error(request, 'Please enter a valid username.')
            return render(request, 'login.html', {'err_code': 'Invalid username/password'})
       
    return render(request, 'login.html')


def logout_page(request):
    auth_logout(request)
    return HttpResponseRedirect('/')

def signup_page(request):
    if request.method =="POST":
        username = request.POST.get('username')
        if User.objects.filter(username=username).exists():
            return render(request, 'signup.html', {'err_code': 'Someone has already use this username.'})
        else:
            password = request.POST.get('password')
            email = request.POST.get('email')
            firstname = request.POST.get('firstname')
            lastname =request.POST.get('lastname')
            
            user = User.objects.create_user(username, email, password)
            user.first_name = firstname
            user.last_name = lastname
            user.save()
            return HttpResponseRedirect('/')
    return render(request, 'signup.html')


def main(request):
    user = request.user
    is_authenticated = request.user.is_authenticated
    context = {
        'packageList':{},
        'user':user,
        'is_authenticated': is_authenticated
    } 
    return render(request, 'main.html', context)


@login_required
def packageDetail(request, pack_id):
    return render(request, 'packagedetail.html')

def search(request):
    query = request.GET.get('q')
    context = {}
    if query:
        try:
            package = Delivery.objects.get(tracking_number=query)
            context['package'] = package
        except Package.DoesNotExist:
            context['error_message'] = f"No package found with tracking number {query}."
    return render(request, 'main.html', context)
