from django.shortcuts import render
from .models import *
from .models import Order  # Ensure this import exists
import datetime


from  django.http import JsonResponse
import json

from .utils import cookieCart, cartData
# Create your views here.
def store(request):
	data = cookieCart(request)
	cartItems = data['cartItems']
	
	products = Product.objects.all()
	context = {'products':products, 'cartItems':cartItems}
	return render(request, 'store/store.html', context)


def cart(request):
	data = cookieCart(request)
	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {'items':items, 'order':order, 'cartItems':cartItems}
	return render(request, 'store/cart.html', context)


def checkout(request):
	
		#Create empty cart for now for non-logged in user
	data = cookieCart(request)
	cartItems = data['cartItems']
	order = data['order']
	items = data['items']


	context = {'items':items, 'order':order, 'cartItems':cartItems}
	return render(request, 'store/checkout.html', context)


def updateItem(request):
	data = json.loads(request.body)
	productId = data['productId']
	action = data['action']
	print('Action:', action)
	print('Product:', productId)

	customer = request.user.customer
	product = Product.objects.get(id=productId)
	order, created = Order.objects.get_or_create(customer=customer, complete=False)

	orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

	if action == 'add':
		orderItem.quantity = (orderItem.quantity + 1)
	elif action == 'remove':
		orderItem.quantity = (orderItem.quantity - 1)

	orderItem.save()

	if orderItem.quantity <= 0:
		orderItem.delete()

	return JsonResponse('Item was added', safe=False)



#from django.views.decorators.csrf import csrf_exempt

#@csrf_exempt
def processOrder(request):
	print("inside process")
	print("data", request.body)

	transation_id = datetime.datetime.now().timestamp()
	data = json.loads(request.body)
	if request.user.is_authenticated:
		customer = request.user.customer

		order, created = Order.objects.get_or_create(customer=customer, complete=False)
		total = float(data['from']['total'])
		order.transaction_id = transation_id

		if total == order.get_cart_total:
			order.complete = True
		order.save()

		if order.shipping == True:
			ShippingAddress.objects.create(
				customer= customer,
				order= order,
				address = data['shipping']['address'],
				city = data['shipping']['city'],
				state = data['shipping']['state'],
				zipcode = data['shipping']['zipcode'],
			)
	else:
		print("user is not logged in ..")
	return JsonResponse('Payment complete', safe=False)

