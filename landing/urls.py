from django.urls import path,include
from . import views

urlpatterns = [
    path('', views.createAccoutn,name="createAccount"),
    path('login/', views.logIn, name="login"),
    path('createAccountDb/', views.createAccountDb, name="createAccountDb"),
    path('validateLogin/', views.validateLogin, name="validateLogin"),
    path('home/', include('home.urls')),   
    path('getEmail/', views.getEmail, name="getEmail"),
    path('recoveryPassword/', views.recoveryPassword, name="recoveryPassword"),
    path('changePassword/', views.changePassword, name="changePassword"),
]
