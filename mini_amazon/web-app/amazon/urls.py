from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # use built-in login and logout
    path('', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='logout.html'), name='logout'),
    path('register/', views.register, name='register'),

    # home page
    path('home/', views.home, name='home'),
    #

    #
    # edit my profile
    path('editmy/', views.edit_my, name='editmy'),


     # search products()
     path('search/', views.search, name='search'),

    # product detail
    path('search/detail/<int:productID>',
         views.product_detail, name='detail'),

    # shopping cart
    path('shoppingCart/', views.shoppingcart, name='shoppingCart'),


    # remove order from shopping cart
    path('removeProduct/<int:id>', views.remove_product, name='removeProduct'),


# place Order
    path('placeorder/', views.place_order, name='placeorder'),

    # orderStatus
    path('orderStatus/', views.order_status, name='orderStatus'),

    # orderStatus
    path('packageStatus/<int:order_id>', views.package_status, name='packageStatus'),


    # # seccessfully send order to server
    # path('success', views.success, name='success'),
    #
    # # fail to place order
    # path('fail', views.fail, name='fail')

]