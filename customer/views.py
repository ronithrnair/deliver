import json
from django.shortcuts import render, redirect
from django.views import View
from django.db.models import Q
from django.core.mail import send_mail
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from .models import MenuItem, Category, OrderModel,Restaurant,Student,Hostel
from django.contrib import sessions


class Login(View):
    def get(self , request, *args, **kwargs):
        student = request.session.get('student')
        if student:
            del request.session['student']    
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
        if not Student.objects.filter(roll_no=roll_no):
            NewStudent = Student.objects.create(
                name=name,
                block=hostel,
                roll_no=roll_no,
                password=password
            )
            request.session['student'] = NewStudent.pk
            NewStudent.save()
            return redirect('index')
        else:
            student_list = Student.objects.get(roll_no=roll_no)  
            print(student_list)
            if student_list.password == password:
                request.session['student'] = student_list.pk
                return redirect('index')
            else:   
                print("Incorrect password")

        # try:
        #     student_list = Student.objects.get(roll_no=roll_no)
                
        #     if not student_list:
        #         NewStudent = Student.objects.create(
        #             name=name,
        #             block=hostel,
        #             roll_no=roll_no,
        #             password=password
        #         )
        #         # NewStudent.save()
        #         request.session['student'] = NewStudent.pk
        #         return redirect('index')
        #     else:
        #         if student_list.password == password:
        #             request.session['student'] = student_list.pk
        #             return redirect('index')
        #         else:   
        #             error_message = "Incorrect password"

        # except Student.DoesNotExist:
        #     error_message = "Student not found"
        return render(request, 'customer/login.html')

class Index(View):
    def get(self, request, *args, **kwargs):
        if not request.session or not request.session.get('student'):
            return redirect('login')
        restaurants = Restaurant.objects.all()
        student = request.session.get('student')
        student_name = Student.objects.get(pk=student).name
        context = {
            'student' : student_name,
            'restaurants' : restaurants
        }
        return render(request, 'customer/index.html',context)

    def post(self, request, *args, **kwargs):
        
        items = request.POST.get('r_options')
        # rpk = Restaurant.objects.get(pk = items)
        return redirect('order', pk = items)
class About(View):
    def get(self, request, *args, **kwargs):
        student = request.session['student']
        context = {
            'student' : Student.objects.get(pk = student).name
        }
        return render(request, 'customer/about.html',context)


class Order(View):
    def get(self, request, pk = None,*args, **kwargs):
        # get every item from each category
        starters = MenuItem.objects.filter(restaurant__pk = pk).filter(category__name__contains='Starter')
        mains = MenuItem.objects.filter(restaurant__pk = pk).filter(category__name__contains='Main')
        desserts = MenuItem.objects.filter(restaurant__pk = pk).filter(category__name__contains='Dessert')
        beverages = MenuItem.objects.filter(restaurant__pk = pk).filter(category__name__contains='Beverages')
        student = request.session['student']
        # pass into context
        context = {
            'id' : pk,
            'starters': starters,
            'mains': mains,
            'desserts': desserts,
            'beverages': beverages,
            'student' : Student.objects.get(pk = student).name
        }

        # render the template
        return render(request, 'customer/order.html',context)

    def post(self, request, *args, **kwargs):
        id = request.POST.get('id')
        restaurant = Restaurant.objects.get(pk = id)
        name = request.POST.get('name')
        roll_no = request.POST.get('roll_no')
        street = request.POST.get('street')
        student = request.session.get('student')
        student = Student.objects.get(pk = student)
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
            name=student.name,
            roll_no = student.roll_no,
            street=student.block,
            restaurant= restaurant,
            student = student
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
        student = request.session.get('student')

        context = {
            'pk': order.pk,
            'items': order.items,
            'price': order.price,
            'student' : Student.objects.get(pk = student).name
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
        student = request.session.get('student')
        return render(request, 'customer/order_pay_confirmation.html',{'student' : Student.objects.get(pk = student).name})


class Menu(View):
    def get(self, request, *args, **kwargs):
        menu_items = MenuItem.objects.all()
        student = request.session.get('student')
        context = {
            'menu_items': menu_items,
            'student' : Student.objects.get(pk = student).name
        }

        return render(request, 'customer/menu.html', context)


class MenuSearch(View):

    def get(self, request, *args, **kwargs):
        query = self.request.GET.get("q")
        student = request.session['student']
        menu_items = MenuItem.objects.filter(
            Q(name__icontains=query) |
            Q(price__icontains=query) |
            Q(description__icontains=query)
        )

        context = {
            'menu_items': menu_items,
            'student' : Student.objects.get(pk = student).name
        }

        return render(request, 'customer/menu.html', context)

class UserDashboard(View):
    def get(self, request, *args, **kwargs):
        student = request.session['student']
        orders = OrderModel.objects.filter(student__pk=student)

        # loop through the orders and add the price value, check if order is not shipped
        unshipped_orders = []
        total_revenue = 0
        for order in orders:
            total_revenue += order.price
            unshipped_orders.append(order)

        # pass total number of orders and total revenue into template
        context = {
            'orders': unshipped_orders,
            'total_revenue': total_revenue,
            'total_orders': len(orders),
            'student' : Student.objects.get(pk = student).name
        }

        return render(request, 'customer/userdashboard.html', context)

    def test_func(self):
        return self.request.user.groups.filter(name='Staff').exists()


class CustomerOrderDetails(View):

    def get(self, request, pk, *args, **kwargs):
        student = request.session['student']
        order = OrderModel.objects.get(pk=pk)
        context = {
            'order': order,
            'items'  : order.items,
            'student' : Student.objects.get(pk = student).name
        }

        return render(request, 'customer/customer-order-details.html', context)

    def post(self, request, pk, *args, **kwargs):
        order = OrderModel.objects.get(pk=pk)
        order.is_delivered = True
        order.save()

        context = {
            'order': order
        }

        return redirect('userdashboard')

    '''def test_func(self):
        return self.request.user.groups.filter(name='Staff').exists()
    '''