# init urls
from django.contrib import admin
from django.urls import include, path
from . import views

urlpatterns = [
    path('login/', views.login_page, name='login_page'),
		path('', views.main, name='main'),
    path('signup/', views.signup_page, name='signup_page'),
    path('logout', views.logout_page, name='logout_page'),
		path('<int:pack_id>/packageDetail/', views.packageDetail, name='packageDetail'),
    path('<int:order_id>/addrUpdate/', views.addrUpdate, name='addrUpdate'),
    path('search/', views.search, name='search'),
    path('delsearch/', views.delSearch, name='del_search'),
    path('connect_backend/', views.connect_backend, name='connect_backend'),
    path('userinfo/', views.userinfo, name='userinfo'),
    path('useredit/<int:userID>', views.useredit, name='useredit'),
    path('driverportal/', views.driverportal, name='driverportal'),
    path('send_delivery_email', views.send_delivery_email, name='sendDelEmail'),
    path('<int:pack_id>/adddelproof', views.addDelProof, name='addDelProof'),

]