from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.http import HttpResponse
from django.template import loader
from .models import *
from django.contrib.auth import get_user_model
from .forms import *
from menuserve import views
from django.contrib.auth import views
from .decorators import manager_required, employee_required, manager_or_employee_required
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from django.core import serializers

# Create your views here.
def register(request):
	if request.method == 'POST':
		form = SignUpForm(request.POST)
		if form.is_valid():
			form.save()
			username = form.cleaned_data.get('username')
			raw_password = form.cleaned_data.get('password1')
			user = authenticate(username=username, password=raw_password)
			login(request, user)
			return redirect('customer')
	else:
		form = SignUpForm()

	return render(request, 'menuserve/register.html', {'form': form})

def welcome(request):

	return render(request, 'menuserve/welcome.html')

@login_required(login_url="/login")
@manager_required
def manager(request):

	return render(request, 'menuserve/manager.html')

@login_required(login_url="/login")
def customer(request):

	return render(request, 'menuserve/customer.html')

@login_required(login_url="/login")
@employee_required
def employee(request):

	return render(request, 'menuserve/employee.html')

@login_required(login_url="/login")
@manager_required
def editMenu(request):

	items = Item.objects.all()
	context = {'items' : items}
	template = loader.get_template('menuserve/editMenu.html')
	return HttpResponse(template.render(context,request))

@csrf_exempt
@login_required(login_url="/login")
@manager_or_employee_required
def processOrder(request):
	
	User = get_user_model()
	u = request.user

	if request.method == 'POST':
		
		processor = None
		stores_selected = []
		locations_selected=[]
		stores = Store.objects.all()

		if u.is_employee == True:
			processor = u.employee_profile
			for store in stores:
				if processor in store.employees.all():
					stores_selected.append(store)
					locations_selected.append(store.location)

		elif u.is_manager == True:
			processor = u.manager_profile
			for store in stores:
				if processor in store.managers.all():
					stores_selected.append(store)
					locations_selected.append(store.location)

		location = request.POST.get("location")
		if location is None:
			location = 'All your stores'

		status = request.POST.get("status")
		if status is None:
			status = 'Received'

		if request.POST.get("order") is not None:

			order_to_change = SubmittedOrder.objects.get(pk=request.POST.get("order"))
			order_to_change.status=status
			order_to_change.save()

		orders = SubmittedOrder.objects.all()
		orders_selected =[]
		order_item={}
		for order in orders:
			if order.location in locations_selected or order.location =='All your stores':
				if order.items.all():
					if order.location == location or location =='All your stores':
						orders_selected.append(order)
						item_quantity={}
						for item in order.items.all():
							item_quantity[item.pk]=OrderItem.objects.get(order=order,item=item).quantity
						order_item[order.pk] = item_quantity

		pk_list=[]
		for o in orders_selected:
			pk_list.append(o.pk)

		return render(request, 'menuserve/processOrder.html', {'pk':pk_list,'num' : len(orders_selected),'stores':stores_selected, 'orders' : orders_selected, 'records': order_item, 'location': location})
	
	else:
		location='All your stores'

		processor = None
		stores_selected = []
		locations_selected=[]
		stores = Store.objects.all()

		if u.is_employee == True:
			processor = u.employee_profile
			for store in stores:
				if processor in store.employees.all():
					stores_selected.append(store)
					locations_selected.append(store.location)

		elif u.is_manager == True:
			processor = u.manager_profile
			for store in stores:
				if processor in store.managers.all():
					stores_selected.append(store)
					locations_selected.append(store.location)

		orders = SubmittedOrder.objects.all()
		orders_selected =[]
		order_item={}
		for order in orders:
			if order.location in locations_selected:
				if order.items.all():
					orders_selected.append(order)
					item_quantity={}
					for item in order.items.all():
						item_quantity[item.pk]=OrderItem.objects.get(order=order,item=item).quantity
					order_item[order.pk] = item_quantity

		context = {'stores':stores_selected, 'orders' : orders_selected, 'records': order_item, 'location':location}
		template = loader.get_template('menuserve/processOrder.html')
		return HttpResponse(template.render(context,request))

@login_required(login_url="/login")
@manager_required	
def hr(request):

	return render(request, 'menuserve/hr.html')

@login_required(login_url="/login")
def viewMenu(request):
	items = Item.objects.all()
	stores = Store.objects.all()
	if request.method == "POST":

		User = get_user_model()
		
		customer = request.POST.get("input")
		location = request.POST.get("location")
		u = User.objects.get(username=customer)
		
		if location is None:
			location = "Select Store"

		order = Order(user=u)
		order.save()

		return render(request, 'menuserve/menu.html', {'order' : order, 'items': items, 'stores':stores, 'location': location})

@login_required(login_url="/login")
def viewHistory(request):

	if request.method == "POST":

		User = get_user_model()

		customer = request.POST.get("input")
		u = User.objects.get(username=customer)

		stores = Store.objects.all()
		location = request.POST.get("location")
		if location is None:
			location = 'All Stores'

		orders = SubmittedOrder.objects.filter(user=u)
		orders_selected =[]
		order_item={}
		for order in orders:
			if order.items.all():
				if order.location == location or location =='All Stores':
					orders_selected.append(order)
					item_quantity={}
					for item in order.items.all():
						item_quantity[item.pk]=OrderItem.objects.get(order=order,item=item).quantity
						order_item[order.pk] = item_quantity

		return render(request, 'menuserve/orderHistory.html', {'stores':stores, 'orders' : orders_selected, 'records': order_item, 'location': location, 'customer':customer})
	
@login_required(login_url="/login")
@manager_required
def editItem(request):

	if request.method == 'POST':

		item_num = request.POST.get("pk")

		form = MenuForm(request.POST, request.FILES)
			
		if form.is_valid():
			i = Item.objects.get(pk=item_num)
			i.item_category = form.cleaned_data['item_category']
			i.item_name = form.cleaned_data['item_name']
			i.item_image= form.cleaned_data['item_image']
			i.item_price = form.cleaned_data['item_price']
			i.save()
			#form.save(force_update=True)
			items = Item.objects.all()
			return render(request, 'menuserve/editMenu.html', {'items':items})
		
		else:
			i = Item.objects.get(pk=item_num)
			form = MenuForm(initial={'item_category': i.item_category, 'item_name': i.item_name, 'item_price': i.item_price, 'item_image':i.item_image})
	else:
		form = MenuForm()
	
	return render(request, 'menuserve/editItem.html', {'form' : form, 'item' : item_num })

@login_required(login_url="/login")
@manager_required
def deleteItem(request):

	if request.method == 'POST':

		item_num = request.POST.get("pk")

		i = Item.objects.get(pk=item_num).delete()
		items = Item.objects.all()
		return render(request, 'menuserve/editMenu.html', {'items':items})
	
	else:
		items = Item.objects.all()
		return render(request, 'menuserve/editMenu.html', {'items':items})

@login_required(login_url="/login")
@manager_required
def addItem(request):

	items = Item.objects.all()

	if request.method == 'POST':

			request.FILES['item_category'] = request.POST.get("category")
			form = MenuForm(request.POST, request.FILES)
				
			if form.is_valid(): 
				form.save()
				items = Item.objects.all()
				return render(request, 'menuserve/editMenu.html', {'items':items} )
				
			else:
				form = MenuForm(initial={'item_category': request.POST.get("category")})

	else:
		form = MenuForm()

	return render(request, 'menuserve/editItem.html', {'form' : form })

@csrf_exempt
@login_required(login_url="/login")
def addToOrder(request):
	
	if request.method == 'POST':

		if request.is_ajax():

			order_num = request.POST["orderID"]
			order = Order.objects.get(pk=order_num)

			item_num = request.POST["itemID"]
			i = Item.objects.get(pk=item_num)

			action=''

			if i in order.items.all():
				action='existing'
				preorderitem = PreorderItem.objects.get(order=order,item=i)
				preorderitem.quantity += 1
				preorderitem.save()
			else:
				action='new'
				order.items.add(i)
				order.save()
				preorderitem = PreorderItem(item=i, order=order)
				preorderitem.save()		

		#stay in the menu page, render all items again
		#items = Item.objects.all()
		item_name = i.item_name
		item_pk = i.pk
		p = PreorderItem.objects.get(order=order,item=i)
		item_quantity = p.quantity

		#location=request.POST["orderLocation"]
		#if location is None:
			#location = "Select Store"

		return JsonResponse({'action':action,'item': item_name, 'pk':item_pk, 'order':order_num, 'quantity':item_quantity})

@csrf_exempt
@login_required(login_url="/login")
def removeFromOrder(request):
	
	if request.method == 'POST':

		if request.is_ajax():

			order_num = request.POST["orderID"]
			order = Order.objects.get(pk=order_num)

			item_num = request.POST["itemID"]
			i = Item.objects.get(pk=item_num)

			action=''
				
			preorderitem = PreorderItem.objects.get(order=order, item=i)

			if preorderitem.quantity > 1:
				action = 'minus'
				preorderitem.quantity -= 1
				preorderitem.save()
			else:
				action = 'remove'
				preorderitem.delete()
				order.items.remove(i)
				order.save()

		return JsonResponse({'action':action,'pk':item_num, 'order':order_num, 'quantity': preorderitem.quantity, 'name': i.item_name})

@csrf_exempt
@login_required(login_url="/login")
def viewOrder(request):

	if request.method == 'POST':

		if request.POST.get("action") =='back':
			return render(request,'menuserve/customer.html')
		else:
			order_num = request.POST.get("hidden")
			order = Order.objects.get(pk=order_num)
			items = order.items.all()
			quantities = {}
			stores = Store.objects.all()

			for i in items:
				quantities[i] = PreorderItem.objects.get(order=order, item=i).quantity

			location = request.POST.get("location")
			if location is None:
				location = 'Select Store'

			return render(request, 'menuserve/order.html', {'stores':stores,'items' : items, 'order': order, 'location': location, 'quantities':quantities})

@csrf_exempt
@login_required(login_url="/login")
def submitOrder(request):

	if request.method == 'POST':

		order_num = request.POST.get("hidden_order")
		order = Order.objects.get(pk=order_num)

		s = SubmittedOrder(pk=order_num, user=order.user)
		s.save()
		os_num=s.pk

		l = request.POST.get("hidden_location")
		os = SubmittedOrder.objects.get(pk=os_num)
		if l =='Select Store':
			os.location = "All your stores"
		else:
			os.location = l
		os.save()

		items = order.items.all()
		quantity = {}
		total = 0

		for item in items:
			
			orderitem = OrderItem(item=item, order=s)
			orderitem.save()		
			orderitem.quantity = int(request.POST.get(str(item.pk)))
			orderitem.save(force_update=True)
			gs = SubmittedOrder.objects.get(pk=os_num)
			if orderitem.quantity != 0:
				gs.items.add(item)
				gs.save()

			total += item.item_price * orderitem.quantity
		
		ks = SubmittedOrder.objects.get(pk=os_num)
		ks.total=total
		ks.save()

		return render(request, 'menuserve/customer.html')

@login_required(login_url="/login")
def ChangeMenu(request):

	items = Item.objects.all()
	stores = Store.objects.all()
		
	if request.method == "POST":

		location = request.POST.get("location")

		if location is None:
			location = "Select Store"

		order_num = request.POST.get("hidden")
		order = Order.objects.get(pk=order_num)

		return render(request, 'menuserve/menu.html', {'stores':stores,'items' : items, 'order': order, 'location':location})

@login_required(login_url="/login")
@manager_required
def manageHR(request):

	if request.method == 'POST':

		current_stores = Store.objects.all()
		User = get_user_model()
		all_users = User.objects.all()
		
		val = request.POST.get("input")
		userToAssign = request.POST.get("user")
		storeToAssign = request.POST.get("workat")

		if val == 'create_employee':

			if userToAssign is not None and storeToAssign is not None:

				s = Store.objects.get(pk=storeToAssign)
				u = User.objects.get(pk=userToAssign)
				#chaneg the user access to employee
				u.is_employee = True
				u.save()
				#create a new employee profile and associate with that user
				Employee.objects.get_or_create(user = u)
				u.employee_profile.location = storeToAssign
				u.save()

				#whether the employee is already in the store
				if u.employee_profile not in s.employees.all():
					u.employee_profile.num_store +=1
					u.employee_profile.save()
					#add the employee to the new store
					s.employees.add(u.employee_profile)
					s.save()
				return render(request, 'menuserve/hr.html')
			
			else:
				#user_not_employee = []
				#for user in all_users:
					#if not user.is_employee and not user.is_manager:
						#user_not_employee.append(user)
				return render(request, 'menuserve/addEmployee.html', {'users':all_users,'stores':current_stores})

		elif val == 'create_manager':

			if userToAssign is not None and storeToAssign is not None: 

				s = Store.objects.get(pk=storeToAssign)
				u = User.objects.get(pk=userToAssign)
				#chaneg the user access to manager
				u.is_manager = True
				u.save()
				#create a new manager profile and associate with that user
				Manager.objects.get_or_create(user = u)
				u.manager_profile.location = storeToAssign
				u.save()

				#whether the employee is already in the store
				if u.manager_profile not in s.managers.all():
					u.manager_profile.num_store +=1
					u.manager_profile.save()
					#add the manager to that store
					s.managers.add(u.manager_profile)
					s.save()
				return render(request, 'menuserve/hr.html')

			else:
				#user_not_manager = []
				#for user in all_users:
					#if not user.is_manager and not user.is_employee:
						#user_not_manager.append(user)
				return render(request, 'menuserve/addManager.html', {'users':all_users, 'stores':current_stores})

		elif val == 'create_store':
			form = StoreForm(request.POST)
			if form.is_valid(): 
				form.save()
				return render(request, 'menuserve/hr.html')
			else:
				form = StoreForm() 
				return render(request, 'menuserve/addStore.html', {'store':form, 'stores':current_stores})

		elif val =='edit':

			u = User.objects.get(username=request.POST.get("currentUser"))
			m = u.manager_profile

			managers_dict ={}
			employees_dict={}
			yourStore=[]

			for store in current_stores:
				if m in store.managers.all():
					managers_dict[store.pk] = store.managers.all()
					employees_dict[store.pk] = store.employees.all()
					yourStore.append(store)

			return render(request, 'menuserve/displayHR.html', {'yourStore':yourStore, 'employees_dict':employees_dict, 'managers_dict':managers_dict})

		elif val =='backToHR':
			return render(request, 'menuserve/hr.html')


	else:
		return render(request, 'menuserve/hr.html')

@login_required(login_url="/login")
@manager_required
def editOrDelete(request):

	if request.method == 'POST':

		User = get_user_model()
		u = User.objects.get(username = request.POST.get("currentUser"))
		m = u.manager_profile


		val = request.POST.get("action")

		if val =='backToHR':
			return render(request, 'menuserve/hr.html')

		if val =='editStore':

			form = StoreForm(request.POST)
			if form.is_valid():
				store_to_edit = Store.objects.get(pk = request.POST.get("hidden"))
				store_to_edit.location = form.cleaned_data['location']
				store_to_edit.storeID = form.cleaned_data['storeID']
				store_to_edit.save()
				managers_dict ={}
				employees_dict={}
				yourStore=[]
				current_stores = Store.objects.all()
				for store in current_stores:
					if m in store.managers.all():
						managers_dict[store.pk] = store.managers.all()
						employees_dict[store.pk] = store.employees.all()
						yourStore.append(store)
				return render(request, 'menuserve/displayHR.html', {'yourStore':yourStore, 'employees_dict':employees_dict, 'managers_dict':managers_dict})

			else:
				store_to_edit = Store.objects.get(pk = request.POST.get("hidden"))
				form = StoreForm(initial={'location': store_to_edit.location, 'storeID': store_to_edit.storeID})
				return render(request, 'menuserve/editOrDelete.html', {'store':form, 'hidden':request.POST.get("hidden"),'action':val })

		elif val == 'deleteStore':
			store_to_delete = Store.objects.get(pk = request.POST.get("hidden"))
			if store_to_delete.managers.all().exists():
	
				for m in store_to_delete.managers.all():
					u = User.objects.get(manager_profile = m)
					u.manager_profile.num_store -= 1
					u.manager_profile.save()
					if u.manager_profile.num_store == 0:
						u.is_manager = False
						u.save()
						m.delete()
			if store_to_delete.employees.all().exists():
				for e in store_to_delete.employees.all():
					u = User.objects.get(employee_profile = e)
					u.employee_profile.num_store -= 1
					u.employee_profile.save()
					if u.employee_profile.num_store == 0:
						u.is_employee = False
						u.save()
						e.delete()
			
			store_to_delete.delete()
			managers_dict ={}
			employees_dict={}
			yourStore=[]
			current_stores = Store.objects.all()
			for store in current_stores:
				if m in store.managers.all():
					managers_dict[store.pk] = store.managers.all()
					employees_dict[store.pk] = store.employees.all()
					yourStore.append(store)
			return render(request, 'menuserve/displayHR.html', {'yourStore':yourStore, 'employees_dict':employees_dict, 'managers_dict':managers_dict})

		elif val == 'editManager':

			manager_to_edit = Manager.objects.get(pk = request.POST.get("hidden2"))
			user_to_edit = User.objects.get(manager_profile = manager_to_edit)

			form = EditProfileForm(request.POST, instance=user_to_edit)

			if form.is_valid():			
				user_to_edit.username = form.cleaned_data['username']
				user_to_edit.first_name = form.cleaned_data['first_name']
				user_to_edit.last_name = form.cleaned_data['last_name']
				user_to_edit.email = form.cleaned_data['email']
				user_to_edit.save()

				managers_dict ={}
				employees_dict={}
				yourStore=[]
				current_stores = Store.objects.all()
				for store in current_stores:
					if m in store.managers.all():
						managers_dict[store.pk] = store.managers.all()
						employees_dict[store.pk] = store.employees.all()
						yourStore.append(store)
				return render(request, 'menuserve/displayHR.html', {'yourStore':yourStore, 'employees_dict':employees_dict, 'managers_dict':managers_dict})
			else:
				manager_to_edit = Manager.objects.get(pk = request.POST.get("hidden2"))
				user_to_edit = User.objects.get(manager_profile = manager_to_edit)
				form = EditProfileForm(initial={'username': user_to_edit.username, 'first_name': user_to_edit.first_name, 'last_name':user_to_edit.last_name, 'email':user_to_edit.email})
				return render(request, 'menuserve/editOrDelete.html', {'store':form, 'hidden2':request.POST.get("hidden2"),'action':val })

		elif val == 'deleteManager':

			manager_to_delete = Manager.objects.get(pk = request.POST.get("hidden2"))
			user = User.objects.get(manager_profile = manager_to_delete)
			user.manager_profile.num_store -= 1
			user.manager_profile.save()
			if user.manager_profile.num_store == 0:
				user.is_manager = False
				user.save()
				#delete this manager forever
				manager_to_delete.delete()
			#delete this manager from the selected store
			store_delete_from = Store.objects.get(pk = request.POST.get("hidden"))
			store_delete_from.managers.remove(user.manager_profile)

			managers_dict ={}
			employees_dict={}
			yourStore=[]
			current_stores = Store.objects.all()
			for store in current_stores:
				if m in store.managers.all():
					managers_dict[store.pk] = store.managers.all()
					employees_dict[store.pk] = store.employees.all()
					yourStore.append(store)
			return render(request, 'menuserve/displayHR.html', {'yourStore':yourStore, 'employees_dict':employees_dict, 'managers_dict':managers_dict})

		elif val == 'editEmployee':

			employee_to_edit = Employee.objects.get(pk = request.POST.get("hidden3"))
			user_to_edit = User.objects.get(employee_profile = employee_to_edit)

			form = EditProfileForm(request.POST, instance=user_to_edit)

			if form.is_valid():
				user_to_edit.username = form.cleaned_data['username']
				user_to_edit.first_name = form.cleaned_data['first_name']
				user_to_edit.last_name = form.cleaned_data['last_name']
				user_to_edit.email = form.cleaned_data['email']
				user_to_edit.save()

				managers_dict ={}
				employees_dict={}
				yourStore=[]
				current_stores = Store.objects.all()
				for store in current_stores:
					if m in store.managers.all():
						managers_dict[store.pk] = store.managers.all()
						employees_dict[store.pk] = store.employees.all()
						yourStore.append(store)
				return render(request, 'menuserve/displayHR.html', {'yourStore':yourStore, 'employees_dict':employees_dict, 'managers_dict':managers_dict})
			else:
				employee_to_edit = Employee.objects.get(pk = request.POST.get("hidden3"))
				user_to_edit = User.objects.get(employee_profile = employee_to_edit)
				form = EditProfileForm(initial={'username': user_to_edit.username, 'first_name': user_to_edit.first_name, 'last_name':user_to_edit.last_name, 'email':user_to_edit.email})
				return render(request, 'menuserve/editOrDelete.html', {'store':form, 'hidden3':request.POST.get("hidden3"),'action':val })

		elif val == 'deleteEmployee':
			
			employee_to_delete = Employee.objects.get(pk = request.POST.get("hidden3"))
			user = User.objects.get(employee_profile = employee_to_delete)
			user.employee_profile.num_store -= 1
			user.employee_profile.save()
			if user.employee_profile.num_store == 0:
				user.is_employee = False
				user.save()
				#delete this employee forever
				employee_to_delete.delete()
			
			#delete this employee from the selected store
			store_delete_from = Store.objects.get(pk = request.POST.get("hidden"))
			store_delete_from.employees.remove(user.employee_profile)
			managers_dict ={}
			employees_dict={}
			yourStore=[]
			current_stores = Store.objects.all()
			for store in current_stores:
				if m in store.managers.all():
					managers_dict[store.pk] = store.managers.all()
					employees_dict[store.pk] = store.employees.all()
					yourStore.append(store)
			return render(request, 'menuserve/displayHR.html', {'yourStore':yourStore, 'employees_dict':employees_dict, 'managers_dict':managers_dict})

	else:
		return render(request, 'menuserve/hr.html')

def ourMenu(request):
	items = Item.objects.all()
	stores = Store.objects.all()
		
	if request.method == "POST":
		
		val = request.POST.get("input")
		location = request.POST.get("location")
		
		if location is None:
			location = "Select Store"

		return render(request, 'menuserve/menuBeforeLogin.html', {'items': items, 'location': location, 'stores':stores})
	
	else:

		location = "Select Store"
		return render(request, 'menuserve/menuBeforeLogin.html', {'items': items, 'location': location, 'stores':stores})	

def ourMenuChangeLocation(request):

	items = Item.objects.all()
	stores = Store.objects.all()
		
	if request.method == "POST":

		location = request.POST.get("location")

		if location is None:
			location = "Select Store"

		return render(request, 'menuserve/menuBeforeLogin.html', {'items' : items, 'location':location, 'stores':stores})

def home(request):

	if request.method == 'POST':

		action = request.POST.get("action")

		if action == "back":
			return render(request, 'menuserve/manager.html')
		else:
			return render(request, 'menuserve/welcome.html')	
	else:
			return render(request, 'menuserve/welcome.html')

@csrf_exempt
def getSubmittedOrder(request):

	User = get_user_model()
	u = request.user

	if request.is_ajax():

		processor = None
		stores_selected = []
		locations_selected=[]
		stores = Store.objects.all()

		if u.is_employee == True:
			processor = u.employee_profile
			for store in stores:
				if processor in store.employees.all():
					stores_selected.append(store)
					locations_selected.append(store.location)

		elif u.is_manager == True:
			processor = u.manager_profile
			for store in stores:
				if processor in store.managers.all():
					stores_selected.append(store)
					locations_selected.append(store.location)

		location = request.POST["location"]

		orders = SubmittedOrder.objects.all()
		orders_selected =[]
		order_item = {}

		for order in orders:
			if order.location in locations_selected or order.location =='All your stores':
				if order.items.all():
			#		if order.location == location or location =='All your stores':
						orders_selected.append(order)
						item_quantity={}
						for item in order.items.all():
							item_quantity[item.item_name]=OrderItem.objects.get(order=order,item=item).quantity
						order_item[order.pk] = item_quantity

		return JsonResponse({
			'location': location,
			'num' : len(orders_selected), 
			'orders' : serializers.serialize('json', orders_selected), 
			'records': json.dumps(order_item)})

