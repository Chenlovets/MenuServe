from django.test import TestCase, LiveServerTestCase
from .models import *
from django.contrib.auth import get_user_model
from selenium import webdriver
from selenium.webdriver.support.ui import Select 
import time
import os
from django.conf import settings

# Create your tests here.
class UserTestCase(TestCase):
	def setUp(self):
		User.objects.get_or_create(pk=17637, first_name='web', last_name='apps')

	def test_user_name(self):
		user = User.objects.get(pk=17637)
		self.assertEqual(user.first_name, 'web')
		self.assertEqual(user.last_name, 'apps')

class ManagerTestCase(TestCase):
	def setUp(self):
		User.objects.get_or_create(pk=17637, first_name='web', last_name='apps')
		u = User.objects.get(pk=17637)
		Manager.objects.create(user = u, location="PITT - CMU")

	def test_manager_location(self):
		u = User.objects.get(pk=17637)
		m = u.manager_profile
		self.assertEqual(m.location, 'PITT - CMU')

class EmployeeTestCase(TestCase):
	def setUp(self):
		User.objects.get_or_create(pk=17637, first_name='web', last_name='apps')
		u = User.objects.get(pk=17637)
		Employee.objects.create(user = u, location="PITT - CMU")

	def test_employee_location(self):
		u = User.objects.get(pk=17637)
		e = u.employee_profile
		self.assertEqual(e.location, 'PITT - CMU')

class ItemTestCase(TestCase):
	def setUp(self):
		Item.objects.create(pk=17637, item_category = 'Burger')

	def test_item_category(self):
		item = Item.objects.get(pk=17637)
		self.assertEqual(item.item_category, 'Burger')

class OrderTestCase(TestCase):
	def setUp(self):
		User.objects.get_or_create(pk=17637, first_name='web', last_name='apps')
		u = User.objects.get(pk=17637)
		Order.objects.create(pk=17637, user=u, total = 17437)

	def test_order_total(self):
		order = Order.objects.get(pk=17637)
		self.assertEqual(order.total, 17437)

class PreorderItemTestCase(TestCase):
	def setUp(self):
		User.objects.get_or_create(pk=17637, first_name='web', last_name='apps')
		u = User.objects.get(pk=17637)
		Order.objects.get_or_create(pk=17637, user=u)
		order = Order.objects.get(pk=17637)
		Item.objects.get_or_create(pk=17437)
		i = Item.objects.get(pk=17437)
		PreorderItem.objects.create(item=i, order=order, quantity=11785)

	def test_PreorderItem_quantity(self):
		order = Order.objects.get(pk=17637)
		i = Item.objects.get(pk=17437)
		p = PreorderItem.objects.get(order=order,item=i)
		self.assertEqual(p.quantity, 11785)

class SubmittedOrderTestCase(TestCase):
	def setUp(self):
		User.objects.get_or_create(pk=17637, first_name='web', last_name='apps')
		u = User.objects.get(pk=17637)
		SubmittedOrder.objects.create(pk=17637, user=u, total = 17437)

	def test_submitted_total(self):
		s = SubmittedOrder.objects.get(pk=17637)
		self.assertEqual(s.total, 17437)

class OrderItemTestCase(TestCase):
	def setUp(self):
		User.objects.get_or_create(pk=17637, first_name='web', last_name='apps')
		u = User.objects.get(pk=17637)
		SubmittedOrder.objects.get_or_create(pk=17637, user=u)
		order = SubmittedOrder.objects.get(pk=17637)
		Item.objects.get_or_create(pk=17437)
		i = Item.objects.get(pk=17437)
		OrderItem.objects.create(item=i, order=order, quantity=17683)

	def test_OrderItem_quantity(self):
		order = SubmittedOrder.objects.get(pk=17637)
		i = Item.objects.get(pk=17437)
		o = OrderItem.objects.get(order=order, item=i)
		self.assertEqual(o.quantity, 17683)

class StoreTestCase(TestCase):
	def setUp(self):
		Store.objects.create(pk=17637, location = 'PITT - CMU')

	def location(self):
		store = Store.objects.get(pk=17637)
		self.assertEqual(store.location, 'PITT - CMU')


class LiveServerTestCase(LiveServerTestCase):

	def setUp(self):
		User.objects.create_superuser(username='webapps', password='lizichenlovets',first_name='web', last_name='apps', email='zichenli@andrew.cmu.edu')
		u = User.objects.get(username='webapps')
		u.is_manager = True
		u.save()
		u.is_employee =True
		u.save()

		#create an item for testing
		item = Item(pk=17637, item_category = 'Burgers', item_price = '5', item_name='chen', item_image = os.getcwd()+"/media/images/burger.png")
		item.save()

		options = webdriver.ChromeOptions()
		options.add_argument('headless')
		# set the window size
		options.add_argument('window-size=1200x600')
		self.driver = webdriver.Chrome(executable_path=os.path.join(settings.BASE_DIR,'chromedriver'), chrome_options=options)

	def test_register(self):
		#self.driver = webdriver.Chrome()
		self.driver.get(self.live_server_url)
		self.driver.find_element_by_id("register").click()
		self.driver.find_element_by_id("id_username").send_keys("TaylorSwift")
		self.driver.find_element_by_id("id_first_name").send_keys("taylor")
		self.driver.find_element_by_id("id_last_name").send_keys("swift")
		self.driver.find_element_by_id("id_email").send_keys("lover@ts.com")
		self.driver.find_element_by_id("id_password1").send_keys("lizichenlovets")
		self.driver.find_element_by_id("id_password2").send_keys("lizichenlovets")
		self.driver.find_element_by_id("signupafterfill").click()
		result = self.driver.find_element_by_id("greeting").text
		self.assertEquals(result, "Hi there, TaylorSwift!")

	def test_login(self):
		#self.driver = webdriver.Chrome()
		self.driver.get(self.live_server_url)
		self.driver.find_element_by_id("login").click()
		self.driver.find_element_by_id("id_username").send_keys("webapps")
		self.driver.find_element_by_id("id_password").send_keys("lizichenlovets")
		self.driver.find_element_by_id("loginAfterFill").click()
		result = self.driver.find_element_by_id("greeting").text
		self.assertEquals(result, "Welcome to MacDonald's, webapps!")

	def test_makeOrder(self):
		#self.driver = webdriver.Chrome()
		self.driver.get(self.live_server_url)

		#log in as customer
		self.driver.find_element_by_id("login").click()
		self.driver.find_element_by_id("id_username").send_keys("webapps")
		self.driver.find_element_by_id("id_password").send_keys("lizichenlovets")
		self.driver.find_element_by_id("loginAfterFill").click()
		self.driver.find_element_by_id("customer").click()

		before = SubmittedOrder.objects.count()

		#enter order page
		self.driver.find_element_by_id("OrderNow").click()
		self.driver.find_element_by_id('Iam17637').click()
		self.driver.find_element_by_id("CheckOut").click()
		self.driver.find_element_by_id("SubmitOrder").click()
		time.sleep(3)

		#test result
		#if it returns to the customer page, which means the order is submitted.
		after = SubmittedOrder.objects.count()
		self.assertEquals(after - before, 1)

	def test_addItem(self):
		#self.driver = webdriver.Chrome()
		self.driver.get(self.live_server_url)

		#log in as manager
		self.driver.find_element_by_id("login").click()
		self.driver.find_element_by_id("id_username").send_keys("webapps")
		self.driver.find_element_by_id("id_password").send_keys("lizichenlovets")
		self.driver.find_element_by_id("loginAfterFill").click()
		self.driver.find_element_by_id("manager").click()

		#enter menu management page
		self.driver.find_element_by_id("EditMenu").click()
		self.driver.find_element_by_id("AddItem").click()
		self.driver.find_element_by_id("id_item_name").send_keys("Chen")
		self.driver.find_element_by_id("id_item_price").send_keys("1")
		self.driver.find_element_by_id("id_item_image").send_keys(os.getcwd()+"/media/images/burger.png")
		time.sleep(5)
		self.driver.find_element_by_id("EditItemConfirm").click()

		#test result
		result = self.driver.find_element_by_id("greeting").text
		self.assertEquals(result, "Menu Management")


