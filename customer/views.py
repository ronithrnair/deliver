import json
from django.shortcuts import render, redirect
from django.views import View
from django.db.models import Q
from django.core.mail import send_mail
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from .models import MenuItem, Category, OrderModel,Restaurant,Student,Hostel


class Login(View):
    def get(self , request, *args, **kwargs):
        hostels = Hostel.objects.all()
        context = {
            'hostels': hostels
        }
        return render(request, 'customer/login.html', context)
    
    def post(self , request, *args, **kwargs):
        name = request.POST.get('name')
        roll_no = request.POST.get('roll_no')
        password = request.POST.get('password')
        hostel_id = request.POST.get('hostel')
        hostel = Hostel.objects.get(pk=hostel_id)

        student_list = Student.objects.filter(roll_no=roll_no)
        if not student_list:
            NewStudent = Student.objects.create(
                name=name,
                block=hostel,
                roll_no=roll_no,
                password=password
            )
            redirect('customer/index.html')
        

class Index(View):
    def get(self, request, *args, **kwargs):
        restaurants = Restaurant.objects.all()
        context = {
            'restaurants' : restaurants
        }
        return render(request, 'customer/index.html',context)

    def post(self, request, *args, **kwargs):
        
        items = request.POST.get('r_options')
        # rpk = Restaurant.objects.get(pk = items)
        return redirect('order', pk = items)
class About(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'customer/about.html')


class Order(View):
    def get(self, request, pk = None,*args, **kwargs):
        # get every item from each category
        starters = MenuItem.objects.filter(restaurant__pk = pk).filter(category__name__contains='Starter')
        mains = MenuItem.objects.filter(restaurant__pk = pk).filter(category__name__contains='Main')
        desserts = MenuItem.objects.filter(restaurant__pk = pk).filter(category__name__contains='Dessert')
        beverages = MenuItem.objects.filter(restaurant__pk = pk).filter(category__name__contains='Beverages')

        # pass into context
        context = {
            'id' : pk,
            'starters': starters,
            'mains': mains,
            'desserts': desserts,
            'beverages': beverages,
        }

        # render the template
        return render(request, 'customer/order.html',context)

    def post(self, request, *args, **kwargs):
        id = request.POST.get('id')
        restaurant = Restaurant.objects.get(pk = id)
        name = request.POST.get('name')
        roll_no = request.POST.get('roll_no')
        street = request.POST.get('street')
        # data = get_context_data(**kwargs)
        print(args)
        order_items = {
            'items': []
        }

        items = request.POST.getlist('items[]')

        for item in items:
            menu_item = MenuItem.objects.get(pk__contains=int(item))
            item_data = {
                'id': menu_item.pk,
                'name': menu_item.name,
                'price': menu_item.price,
            }

            order_items['items'].append(item_data)

            price = 0
            item_ids = []

        for item in order_items['items']:
            price += item['price']
            item_ids.append(item['id'])

        order = OrderModel.objects.create(
            price=price,
            name=name,
            roll_no = roll_no,
            street=street,
            restaurant= restaurant
        )
        order.items.add(*item_ids)

        # After everything is done, send confirmation email to the user
        body = ('Thank you for your order! Your food is being made and will be delivered soon!\n'
                f'Your total: {price}\n'
                'Thank you again for your order!')

        # send_mail(
        #     'Thank You For Your Order!',
        #     body,
        #     'example@example.com',
        #     [email],
        #     fail_silently=False
        # )

        context = {
            'items': order_items['items'],
            'price': price
        }

        return redirect('order-confirmation', pk=order.pk)


class OrderConfirmation(View):
    def get(self, request, pk, *args, **kwargs):
        order = OrderModel.objects.get(pk=pk)

        context = {
            'pk': order.pk,
            'items': order.items,
            'price': order.price,
        }

        return render(request, 'customer/order_confirmation.html', context)

    def post(self, request, pk, *args, **kwargs):
        data = json.loads(request.body)

        if data['isPaid']:
            order = OrderModel.objects.get(pk=pk)
            order.is_paid = True
            order.save()

        return redirect('payment-confirmation')


class OrderPayConfirmation(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'customer/order_pay_confirmation.html')


class Menu(View):
    def get(self, request, *args, **kwargs):
        menu_items = MenuItem.objects.all()

        context = {
            'menu_items': menu_items
        }

        return render(request, 'customer/menu.html', context)


class MenuSearch(View):
    def get(self, request, *args, **kwargs):
        query = self.request.GET.get("q")

        menu_items = MenuItem.objects.filter(
            Q(name__icontains=query) |
            Q(price__icontains=query) |
            Q(description__icontains=query)
        )

        context = {
            'menu_items': menu_items
        }

        return render(request, 'customer/menu.html', context)
