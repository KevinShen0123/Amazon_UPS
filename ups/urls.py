# init urls
from django.contrib import admin
from django.urls import include, path
from . import views

urlpatterns = [
    path('', views.login_page, name='login_page'),
		path('main/', views.main, name='main'),
    path('signup/', views.signup_page, name='signup_page'),
    path('logout', views.logout_page, name='logout_page'),
		path('<int:pack_id>/packageDetail/', views.packageDetail, name='packageDetail'),

]