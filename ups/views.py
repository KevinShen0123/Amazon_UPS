from django.shortcuts import render
import socket
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
from django.urls import reverse
from django.shortcuts import redirect


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
    username = request.user.username
    is_authenticated = request.user.is_authenticated
    upsaccount = username
    package_list =Delivery.objects.filter(order__in=Order.objects.filter(upsaccount=upsaccount))
    context = {
        'packageList': package_list,
        'user':user,
        'is_authenticated': is_authenticated
    } 
    return render(request, 'main.html', context)


@login_required
def packageDetail(request, pack_id):
    package = get_object_or_404(Delivery, pk=pack_id) 
    context = {
        'package' : package
    }  
    return render(request, 'packagedetail.html', context)

def search(request):
    query = request.GET.get('pack_search')
    context = {}
    if query:
        try:
            cur_delivery = Delivery.objects.get(package_id=query)
            context['package'] = cur_delivery
            user = request.user
            username = request.user.username
            is_authenticated = request.user.is_authenticated
            upsaccount = username
            package_list =Delivery.objects.filter(order__in=Order.objects.filter(upsaccount=upsaccount))
            context['user'] = user
            context['is_authenticated']= is_authenticated
            context['packageList'] = package_list
        except Delivery.DoesNotExist:
            context['error_message'] = f"No package found with tracking number {query}."
    return render(request, 'main.html', context)

def addrUpdate(request, pack_id):
    if request.method =="POST":
        dest_x = request.POST.get('dest_x')
        dest_y = request.POST.get('dest_y')
        
        delivery = get_object_or_404(Delivery, package_id=pack_id)
        if dest_x is not None:  
            delivery.dest_x = dest_x
        if dest_y is not None:  
            delivery.dest_y = dest_y
        delivery.save()

        msg = str(pack_id)+","+str(dest_x)+","+str(dest_y)
        print("connecting to backend, sending: ", msg)
        try:
            backend_info = ('127.0.0.1', 8080)
            socket_to_backend =  socket.socket()
            socket_to_backend.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

            socket_to_backend.connect(backend_info)
            socket_to_backend.send(msg.encode('utf-8'))
            print(msg)
        except :
            error_message = 'lost connection to server!'
            print(error_message)
        return redirect(reverse('packageDetail', args=[pack_id]))
    else:
        package = get_object_or_404(Delivery, pk= pack_id)
        user = request.user
        context = {
            'package': package
        }
        return render(request,'addrUpdate.html', context)


def connect_backend(request):
    msg = "123,1,2"
    print("connecting to backend")
    try:
        backend_info = ('127.0.0.1', 8080)
        socket_to_backend =  socket.socket()
        socket_to_backend.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

        socket_to_backend.connect(backend_info)
        socket_to_backend.send(msg.encode('utf-8'))
        print(msg)
    except :
        error_message = 'lost connection to server!'
        print(error_message)
    return render(request, 'main.html')