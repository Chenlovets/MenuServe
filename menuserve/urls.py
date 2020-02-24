from django.urls import path
from . import views

#app_name = 'menuserve'

urlpatterns = [

    path('', views.welcome, name='welcome'),
    path('manager/', views.manager, name='manager'),
    path('employee/', views.employee, name='employee'),
    path('customer/', views.customer, name='customer'),
    path('hr/', views.hr, name='hr'),
    path('editMenu/', views.editMenu, name='editMenu'),
    path('processOrder/', views.processOrder, name='processOrder'),
    path('viewMenu/', views.viewMenu, name='viewMenu'),
    path('editItem/', views.editItem, name='editItem'),
    path('deleteItem/', views.deleteItem, name='deleteItem'),
    path('addItem/', views.addItem, name='addItem'),
    path('ChangeMenu/', views.ChangeMenu, name='ChangeMenu'),   
    path('addToOrder/', views.addToOrder, name='addToOrder'),
    path('removeFromOrder/', views.removeFromOrder, name='removeFromOrder'),
    path('submitOrder/', views.submitOrder, name='submitOrder'),
    path('viewOrder/', views.viewOrder, name='viewOrder'),
    #path('backToMenu/', views.backToMenu, name='backToMenu'),
    path('home/', views.home, name='home'),
	path('manageHR/', views.manageHR, name='manageHR'),
	path('editOrDelete/', views.editOrDelete, name='editOrDelete'),
    path('register/', views.register, name='register'),
    path('ourMenu/', views.ourMenu, name='ourMenu'),
    path('ourMenuChangeLocation/', views.ourMenuChangeLocation, name='ourMenuChangeLocation'),
    path('ourMenu/', views.ourMenu, name='ourMenu'),
    path('viewHistory/', views.viewHistory, name='viewHistory'),
    path('getSubmittedOrder/', views.getSubmittedOrder, name='getSubmittedOrder'),
]
