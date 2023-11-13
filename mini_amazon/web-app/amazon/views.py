from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import ORDER,Package,Product,UserProfile
from .forms import UserRegisterForm,EditMyForm,addShoppingCartForm,PlaceOrderForm
from django.utils import timezone
from django.http import HttpResponse
from amazon.clients import *
import socket
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, f'You have created successfully. Please log in!')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form})


@login_required
def home(request):
    # create profile in database for every new user

    list = UserProfile.objects.filter(userName=request.user)
    if list.exists() is not True:
        profile = UserProfile.objects.create(userName=request.user)
        profile.userName = request.user
        profile.save()

    return render(request, 'home.html')

@login_required
def edit_my(request):
    Logged_User = UserProfile.objects.filter(userName=request.user).first()
    if request.method == "POST":
        profile_form = EditMyForm(request.POST, instance=Logged_User)
        if profile_form.is_valid():
            getAddrX = profile_form.cleaned_data['addrX']
            getAddrY = profile_form.cleaned_data['addrY']
            getUpsID = profile_form.cleaned_data['upsid']

            Logged_User.addrX = getAddrX
            Logged_User.addrY = getAddrY
            Logged_User.upsID = getUpsID
            Logged_User.save()
            return redirect('home')
    else:  # GET
        edit_my = EditMyForm(instance=Logged_User)
        return render(request, 'editmy.html', {'edit_my': edit_my })


@login_required
def search(request):
    if request.method == 'GET':
        query = request.GET.get('q')
        if query:

            results = Product.objects.filter(catalog=query)
        else:

            results = Product.objects.all()

        return render(request, 'search.html', {'results': results, 'query': query})



@login_required
def product_detail(request, productID):
    profile = UserProfile.objects.filter(userName=request.user).first()
    product = Product.objects.filter(product_id = productID)


    if request.method == 'GET':
        form = addShoppingCartForm(instance=profile)
        context = {
            'productPrice': product[0].price,
            'productName': product[0].product_name,
            'productDescription': product[0].product_desc,
            'productID': product[0].product_id,
            'productCatalog': product[0].catalog,
            'placeOrderform': form,
        }
        return render(request, 'productdetail.html', context)
    else:  # POST

        # add record to shopping cart
        form = addShoppingCartForm(request.POST, instance=profile)
        if form.is_valid():
            package = Package.objects.create(
                package_desc= form.cleaned_data['package_desc'],
                amount=form.cleaned_data['amount'],
                product_id=productID,
                package_owner= profile)
        return redirect('search')


@login_required
def shoppingcart(request):
    profile = UserProfile.objects.filter(userName=request.user).first()
    if request.method == 'POST':

        place_form = PlaceOrderForm(request.POST, instance=profile)

        if place_form.is_valid():  # 获取数据
            order = ORDER.objects.create(
                order_addr_x=place_form.cleaned_data['addrX'],
                order_addr_y=place_form.cleaned_data['addrY'],
                time = timezone.now(),
                order_owner = profile,
                upsid =  place_form.cleaned_data['upsid'],
                price = request.POST.get('total_price'))

            package_id_str = request.POST.get('packages')[1:-1].split(',')
            package_ids = [int(num.strip()) for num in package_id_str]

            for package_item_id in package_ids:
                package_item = Package.objects.filter(package_id=package_item_id).first()
                package_item.order = ORDER.objects.filter(order_id = order.order_id).first()
                package_item.status = "packing"
                package_item.save()
            #send socket request to the C++ server to indicate the success of order
            confirm_order(order)





        return redirect('shoppingCart')

    else:
        # get all item in shopping cart for current user

        shopping_items = Package.objects.filter(package_owner=profile,status="open")
        context = {
         'shopping_items': shopping_items,
        }

        return render(request, 'shoppingcart.html', context=context)


@login_required
def remove_product(request, id):
    Package.objects.filter(package_id=id,status = "open").first().delete()
    return redirect('shoppingCart')

@login_required
def place_order(request):
    profile = UserProfile.objects.filter(userName=request.user).first()

    if request.method == 'POST':
        checked_values_str = request.POST.getlist('my_checkboxes')
        checked_values = list(map(int, checked_values_str))
        total_price = 0

        for value in checked_values:
            package_item = Package.objects.filter(package_id=value).first()
            amount = package_item.amount
            product_price = package_item.product.price
            package_price = product_price * amount
            total_price += package_price


        place_form = PlaceOrderForm(instance=profile)
        context = {
            'place_form': place_form,
            'total_price' : total_price,
            'checked_value' : checked_values
        }
        return render(request, 'placeorder.html', context)

@login_required
def order_status(request):
    profile = UserProfile.objects.filter(userName=request.user).first()
    order_list = ORDER.objects.filter(order_owner=profile)
    context = {
        'order_list': order_list,
    }
    return render(request, 'orderstatus.html', context)

@login_required
def package_status(request, order_id):
    order_list = ORDER.objects.filter(order_id=order_id)

    packages_list = Package.objects.filter(order_id=order_list.first())
    context = {
        'packages_list': packages_list,
    }
    return render(request, 'packagestatus.html', context)


