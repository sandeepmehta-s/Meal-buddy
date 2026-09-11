from decimal import Decimal, InvalidOperation

import razorpay
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from .models import Cart, Customer, Item, Restaurant


def index(request):
    return render(request, 'delivery/index.html')


def open_signin(request):
    return render(request, 'delivery/signin.html')


def open_signup(request):
    return render(request, 'delivery/signup.html')


def _customer_session(request, customer):
    request.session['customer_id'] = customer.id
    request.session['username'] = customer.username


def _render_customer_home(request, customer):
    return render(request, 'delivery/customer_home.html', {
        'restaurantList': Restaurant.objects.all(),
        'username': customer.username,
    })


@require_GET
def logout_view(request):
    request.session.flush()
    return redirect('home')


@require_POST
def signup(request):
    username = request.POST.get('username', '').strip()
    password = request.POST.get('password', '')
    email = request.POST.get('email', '').strip()
    mobile = request.POST.get('mobile', '').strip()
    address = request.POST.get('address', '').strip()

    if not all([username, password, email, mobile, address]):
        messages.error(request, 'Please complete every field.')
        return render(request, 'delivery/signup.html', status=400)
    if len(password) < 8:
        messages.error(request, 'Password must be at least 8 characters long.')
        return render(request, 'delivery/signup.html', status=400)
    if not mobile.isdigit() or len(mobile) != 10:
        messages.error(request, 'Enter a valid 10-digit mobile number.')
        return render(request, 'delivery/signup.html', status=400)
    if Customer.objects.filter(username=username).exists():
        messages.error(request, 'That username is already taken.')
        return render(request, 'delivery/signup.html', status=409)

    customer = Customer.objects.create(username=username, password=make_password(password), email=email, mobile=mobile, address=address)
    _customer_session(request, customer)
    return redirect('customer_home', username=customer.username)


@require_POST
def signin(request):
    username = request.POST.get('username', '').strip()
    password = request.POST.get('password', '')
    customer = Customer.objects.filter(username=username).first()
    valid_password = customer and (check_password(password, customer.password) or customer.password == password)
    if not customer or not valid_password:
        messages.error(request, 'Username or password is incorrect.')
        return render(request, 'delivery/fail.html', status=401)
    if customer.password == password:
        customer.password = make_password(password)
        customer.save(update_fields=['password'])
    _customer_session(request, customer)
    if username == 'admin':
        return redirect('admin_home')
    return redirect('customer_home', username=customer.username)


@require_GET
def customer_home(request, username):
    return _render_customer_home(request, get_object_or_404(Customer, username=username))


@require_GET
def admin_home(request):
    return render(request, 'delivery/admin_home.html')


@require_GET
def open_add_restaurant(request):
    return render(request, 'delivery/add_restaurant.html')


@require_POST
def add_restaurant(request):
    name = request.POST.get('name', '').strip()
    cuisine = request.POST.get('cuisine', '').strip()
    picture = request.POST.get('picture', '').strip()
    try:
        rating = Decimal(request.POST.get('rating', '0'))
        if not 0 <= rating <= 5:
            raise InvalidOperation
    except (InvalidOperation, TypeError):
        messages.error(request, 'Rating must be a number between 0 and 5.')
        return render(request, 'delivery/add_restaurant.html', status=400)
    if not name or not cuisine:
        messages.error(request, 'Restaurant name and cuisine are required.')
        return render(request, 'delivery/add_restaurant.html', status=400)
    if Restaurant.objects.filter(name__iexact=name).exists():
        messages.error(request, 'A restaurant with that name already exists.')
        return render(request, 'delivery/add_restaurant.html', status=409)
    Restaurant.objects.create(name=name, picture=picture or Restaurant._meta.get_field('picture').default, cuisine=cuisine, rating=rating)
    messages.success(request, 'Restaurant added successfully.')
    return redirect('open_show_restaurant')


@require_GET
def open_show_restaurant(request):
    return render(request, 'delivery/show_restaurants.html', {'restaurantList': Restaurant.objects.prefetch_related('items').all()})


@require_GET
def open_update_restaurant(request, restaurant_id):
    return render(request, 'delivery/update_restaurant.html', {'restaurant': get_object_or_404(Restaurant, id=restaurant_id)})


@require_POST
def update_restaurant(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    name = request.POST.get('name', '').strip()
    cuisine = request.POST.get('cuisine', '').strip()
    try:
        rating = Decimal(request.POST.get('rating', '0'))
        if not 0 <= rating <= 5:
            raise InvalidOperation
    except (InvalidOperation, TypeError):
        messages.error(request, 'Rating must be a number between 0 and 5.')
        return render(request, 'delivery/update_restaurant.html', {'restaurant': restaurant}, status=400)
    if Restaurant.objects.filter(name__iexact=name).exclude(id=restaurant.id).exists():
        messages.error(request, 'A restaurant with that name already exists.')
        return render(request, 'delivery/update_restaurant.html', {'restaurant': restaurant}, status=409)
    restaurant.name = name
    restaurant.picture = request.POST.get('picture', '').strip() or restaurant.picture
    restaurant.cuisine = cuisine
    restaurant.rating = rating
    restaurant.save()
    messages.success(request, 'Restaurant updated successfully.')
    return redirect('open_show_restaurant')


@require_POST
def delete_restaurant(request, restaurant_id):
    get_object_or_404(Restaurant, id=restaurant_id).delete()
    messages.success(request, 'Restaurant deleted.')
    return redirect('open_show_restaurant')


@require_GET
def open_update_menu(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    return render(request, 'delivery/update_menu.html', {'itemList': restaurant.items.all(), 'restaurant': restaurant})


@require_POST
def update_menu(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    name = request.POST.get('name', '').strip()
    description = request.POST.get('description', '').strip()
    picture = request.POST.get('picture', '').strip()
    try:
        price = Decimal(request.POST.get('price', '0'))
        if price < 0:
            raise InvalidOperation
    except (InvalidOperation, TypeError):
        messages.error(request, 'Price must be a non-negative number.')
        return redirect('open_update_menu', restaurant_id=restaurant.id)
    if not name or not description:
        messages.error(request, 'Item name and description are required.')
        return redirect('open_update_menu', restaurant_id=restaurant.id)
    if Item.objects.filter(restaurant=restaurant, name__iexact=name).exists():
        messages.error(request, 'That item already exists in this menu.')
        return redirect('open_update_menu', restaurant_id=restaurant.id)
    Item.objects.create(restaurant=restaurant, name=name, description=description, price=price, vegeterian=request.POST.get('vegeterian') == 'on', picture=picture or Item._meta.get_field('picture').default)
    messages.success(request, 'Menu item added.')
    return redirect('open_update_menu', restaurant_id=restaurant.id)


@require_GET
def view_menu(request, restaurant_id, username):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    return render(request, 'delivery/customer_menu.html', {'itemList': restaurant.items.all(), 'restaurant': restaurant, 'username': username})


@require_POST
def add_to_cart(request, item_id, username):
    item = get_object_or_404(Item, id=item_id)
    customer = get_object_or_404(Customer, username=username)
    cart, _ = Cart.objects.get_or_create(customer=customer)
    cart.items.add(item)
    messages.success(request, f'{item.name} added to your cart.')
    return redirect('view_menu', restaurant_id=item.restaurant_id, username=username)


@require_GET
def show_cart(request, username):
    customer = get_object_or_404(Customer, username=username)
    cart = Cart.objects.filter(customer=customer).prefetch_related('items').first()
    return render(request, 'delivery/cart.html', {'itemList': cart.items.all() if cart else [], 'total_price': cart.total_price() if cart else Decimal('0.00'), 'username': username})


@require_GET
def checkout(request, username):
    customer = get_object_or_404(Customer, username=username)
    cart = Cart.objects.filter(customer=customer).prefetch_related('items').first()
    cart_items = cart.items.all() if cart else []
    total_price = cart.total_price() if cart else Decimal('0.00')
    if total_price == 0:
        return render(request, 'delivery/checkout.html', {'username': username, 'error': 'Your cart is empty.'})
    if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
        return render(request, 'delivery/checkout.html', {'username': username, 'error': 'Payments are not configured yet. Add Razorpay credentials to the environment.'}, status=503)
    order = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)).order.create(data={'amount': int(total_price * 100), 'currency': 'INR', 'payment_capture': '1'})
    return render(request, 'delivery/checkout.html', {'username': username, 'cart_items': cart_items, 'total_price': total_price, 'razorpay_key_id': settings.RAZORPAY_KEY_ID, 'order_id': order['id'], 'amount': int(total_price * 100)})


@require_GET
def orders(request, username):
    customer = get_object_or_404(Customer, username=username)
    cart = Cart.objects.filter(customer=customer).prefetch_related('items').first()
    cart_items = list(cart.items.all()) if cart else []
    total_price = cart.total_price() if cart else Decimal('0.00')
    if cart:
        cart.items.clear()
    return render(request, 'delivery/orders.html', {'username': username, 'customer': customer, 'cart_items': cart_items, 'total_price': total_price})
