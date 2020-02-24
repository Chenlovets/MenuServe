from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
class User(AbstractUser):
    
    is_employee = models.BooleanField(default=False)
    is_manager = models.BooleanField(default=False)

class Manager(models.Model):

    user=models.OneToOneField(User, on_delete=models.CASCADE, related_name='manager_profile')
    location = models.CharField(max_length=30)
    num_store=models.IntegerField(default=0)

    def __str__(self):
        return str(self.pk)


class Employee(models.Model):

    user=models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_profile')
    location = models.CharField(max_length=30)
    num_store=models.IntegerField(default=0)

    def __str__(self):
        return str(self.pk)

class Item(models.Model):

    item_category = models.CharField(max_length=100)
    item_name = models.CharField(max_length=100)
    item_price = models.DecimalField(max_digits=10, default=0, decimal_places=2)
    item_image = models.ImageField(upload_to='images/')

    def __str__(self):
        return self.item_name

class Order(models.Model):

    items = models.ManyToManyField(Item)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='order')
    location = models.CharField(max_length=100)
    total = models.DecimalField(max_digits=10, default=0, decimal_places=2)

    def __str__(self):
        return str(self.pk)

class PreorderItem(models.Model):

    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return str(self.pk)

class SubmittedOrder(models.Model):

    items = models.ManyToManyField(Item)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submittedorder')
    location = models.CharField(max_length=100)
    total = models.DecimalField(max_digits=10, default=0, decimal_places=2)
    status = models.CharField(max_length=100, default="Received")

    def __str__(self):
        return str(self.pk)

class OrderItem(models.Model):

    order = models.ForeignKey(SubmittedOrder, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return str(self.pk)

class Store(models.Model):
    location = models.CharField(max_length=100)
    storeID = models.CharField(max_length=100)
    managers = models.ManyToManyField(Manager)
    employees = models.ManyToManyField(Employee)

    def __str__(self):
        return str(self.pk)








