from django.db import models

class Restaurant(models.Model):
    restaurant_name = models.CharField(max_length=100)
    uname = models.CharField(max_length=100)
    image = models.ImageField(upload_to='restaurant_images/')
    
    def __str__(self):
        return self.restaurant_name


class MenuItem(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='menu_images/')
    price = models.DecimalField(max_digits=5, decimal_places=2)
    category = models.ManyToManyField('Category', related_name='item')
    restaurant = models.ForeignKey('Restaurant',on_delete=models.CASCADE)
    def __str__(self):
        return self.name

class Hostel(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class Student(models.Model):
    name = models.CharField(max_length=100)
    block = models.ForeignKey('Hostel', on_delete = models.CASCADE)
    roll_no = models.CharField(max_length=100)
    def __str__(self):
        return self.name



class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class OrderModel(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    items = models.ManyToManyField(
        'MenuItem', related_name='order', blank=True)
    student = models.ForeignKey('Student',on_delete=models.CASCADE)
    name = models.CharField(max_length=50, blank=True)
    roll_no = models.CharField(max_length=50, blank=True)
    street = models.CharField(max_length=50, blank=True)
    restaurant = models.ForeignKey('Restaurant', on_delete=models.CASCADE)
    is_paid = models.BooleanField(default=False)
    is_shipped = models.BooleanField(default=False)
    is_delivered = models.BooleanField(default=False)

    def __str__(self):
        return f'Order: {self.created_on.strftime("%b %d %I: %M %p")}'


