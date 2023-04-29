from django.shortcuts import render
import socket
from datetime import datetime
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from .models import Order, Delivery, Truck, OrderStatus, Driver
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
    order_list = Order.objects.filter(upsaccount=upsaccount)
    package_list = []
    ready_list = []
    for order in order_list:
        # get the deliveries for the order
        deliveries = order.deliveries.all()

        if deliveries.exists():
            # add the existing deliveries to the package list
            package_list.extend(deliveries)
        else:
            # create a new delivery object for the order
            delivery_data = {
                'order': order,
                'truck': None,
                'dest_x': order.dest_x,
                'dest_y': order.dest_y,
                'descr': 'Unavailable at this moment',
                'd_status': 'ready',
            }
            ready_list.append(delivery_data)
    context = {
        'packageList': package_list,
        'readyList': ready_list,
        'user':user,
        'is_authenticated': is_authenticated
    } 
    return render(request, 'main.html', context)


@login_required
def packageDetail(request, pack_id):
    package = get_object_or_404(Delivery, pk=pack_id) 
    order_status = {
        'ready':'',
        'delivering':'',
        'delivered':''
    }
    status_list = OrderStatus.objects.filter(order_id=package.order.order_id).values('order_id', 'od_status', 'm_time')
    for st in status_list:
        if st['od_status'] == 'ready':
            order_status['ready'] = st['m_time'].strftime('%Y-%m-%d %H:%M')
        if st['od_status'] == 'delivering':
            order_status['delivering'] = st['m_time'].strftime('%Y-%m-%d %H:%M')
        if st['od_status'] == 'delivered':
            order_status['delivered'] = st['m_time'].strftime('%Y-%m-%d %H:%M')
    
    context = {
        'package' : package,
        'order_status': order_status
    }  
    return render(request, 'packageDetail.html', context)

def search(request):
    query = request.GET.get('pack_search')
    context = {}
    if query:
        try:
            cur_delivery = Delivery.objects.get(package_id=query)
            context['package'] = cur_delivery
        except Delivery.DoesNotExist:
            context['error_message'] = f"No package found with tracking number {query}."
        user = request.user
        username = request.user.username
        is_authenticated = request.user.is_authenticated
        upsaccount = username
        order_list = Order.objects.filter(upsaccount=upsaccount)
        package_list = []
        ready_list = []
        for order in order_list:
                # get the deliveries for the order
            deliveries = order.deliveries.all()
            if deliveries.exists():
                # add the existing deliveries to the package list
                package_list.extend(deliveries)
            else:
                # create a new delivery object for the order
                delivery_data = {
                    'order': order,
                    'truck': None,
                    'dest_x': order.dest_x,
                    'dest_y': order.dest_y,
                    'descr': 'Unavailable at this moment',
                    'd_status': 'ready',
                }
                ready_list.append(delivery_data)
                
        context['packageList']= package_list
        context['readyList'] = ready_list
        context['user'] = user
        context['is_authenticated'] = is_authenticated
    return render(request, 'main.html', context)

@login_required
def userinfo(request):
    context = {
        'user': request.user
    }
    return render(request,'userinfo.html', context)

@login_required
def useredit(request, userID):
    if request.method =="POST":
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        email = request.POST.get('email')
        
        user = get_object_or_404(User, id=userID)
        user.first_name = firstname
        user.last_name = lastname
        user.email = email
        user.save()
        return HttpResponseRedirect('/userinfo/')
    else:
        user = get_object_or_404(User, id=request.user.id)
        user = request.user
        context = {
            'user': user
        }
        return render(request,'useredit.html', context)

    return render(request, 'useredit.html')

def addrUpdate(request, order_id):
    if request.method =="POST":
        dest_x = request.POST.get('dest_x')
        dest_y = request.POST.get('dest_y')
        
        order = get_object_or_404(Order, order_id=order_id)
        if dest_x is not None:  
            order.dest_x = dest_x
        if dest_y is not None:  
            order.dest_y = dest_y
        order.save()
        
        print("sending email", request.user.email)
        send_mail('Delivery Address Update', 'You delivery address has updated.', settings.EMAIL_HOST_USER, [request.user.email], fail_silently=False)
        msg = str(order_id)+","+str(dest_x)+","+str(dest_y)
        print("connecting to backend, sending: ", msg)
        try:
            backend_info = ('127.0.0.1', 8080)
            socket_to_backend =  socket.socket()
            socket_to_backend.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

            socket_to_backend.connect(backend_info)
            socket_to_backend.send(msg.encode('utf-8'))
            socket_to_backend.close()
        except :
            error_message = 'lost connection to server!'
            print(error_message)
        context =get_main_info(request)
        return render(request, 'main.html', context)
    else:
        order = get_object_or_404(Order, pk= order_id)
        user = request.user
        context = {
            'order': order
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

def get_main_info(request):
    user = request.user
    username = request.user.username
    is_authenticated = request.user.is_authenticated
    upsaccount = username
    order_list = Order.objects.filter(upsaccount=upsaccount)
    package_list = []
    ready_list = []
    for order in order_list:
        # get the deliveries for the order
        deliveries = order.deliveries.all()

        if deliveries.exists():
            # add the existing deliveries to the package list
            package_list.extend(deliveries)
        else:
            # create a new delivery object for the order
            delivery_data = {
                'order': order,
                'truck': None,
                'dest_x': order.dest_x,
                'dest_y': order.dest_y,
                'descr': 'Unavailable at this moment',
                'd_status': 'ready',
            }
            ready_list.append(delivery_data)
    context = {
        'packageList': package_list,
        'readyList': ready_list,
        'user':user,
        'is_authenticated': is_authenticated
    } 
    return context

def driverportal(request):
   
    return render(request, 'driverportal.html')

def send_delivery_email(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        # Retrieve the email address for the user associated with this order_id
        # user_email = Delivery.objects.filter(order_id=order_id).first().user.email
        # Send the email
        order = Order.objects.get(order_id=order_id)
        email_subject = f'Delivery for order {order_id}'
        email_body = f'Your order {order_id} has been delivered. Thank you for choosing us!'
        recipient_user = get_object_or_404(User, username=order.upsaccount)
        recipient_email = recipient_user.email
        print("====== sending mail to", recipient_email)
        #send_mail('Delivery Address Update', 'You delivery address has updated.', settings.EMAIL_HOST_USER, [request.user.email], fail_silently=False)
        send_mail('Delivery Made', email_body, settings.EMAIL_HOST_USER, [recipient_email], fail_silently=False)
        messages.success(request, 'Email sent!')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
  



def addDelProof(request, pack_id):
    
    return render(request, 'uploadproof.html')


def delSearch(request):
    query = request.GET.get('del_search')
    context = {}
    if query:
        try:
            driver = Driver.objects.get(driver_id=query)
            deliveries = driver.deliveries.all()
            context['deliveries'] = deliveries
        except Delivery.DoesNotExist:
            context['error_message'] = f"No package found with tracking number {query}."
       
    return render(request, 'driverportal.html', context)
