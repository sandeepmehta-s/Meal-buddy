from django.contrib.auth.hashers import check_password
from django.test import TestCase
from django.urls import reverse

from .models import Customer, Item, Restaurant


class MealMateFlowTests(TestCase):
    def setUp(self):
        self.restaurant = Restaurant.objects.create(
            name='Green Table', cuisine='Indian', rating='4.5'
        )
        self.item = Item.objects.create(
            restaurant=self.restaurant,
            name='Paneer Bowl',
            description='A warm, fresh bowl.',
            price='180.00',
            vegeterian=True,
        )

    def test_home_and_customer_pages_render(self):
        self.assertEqual(self.client.get(reverse('home')).status_code, 200)
        customer = Customer.objects.create(
            username='sandeep', password='unused', email='s@example.com',
            mobile='9876543210', address='Gurugram'
        )
        self.assertEqual(self.client.get(reverse('customer_home', args=[customer.username])).status_code, 200)
        self.assertEqual(self.client.get(reverse('view_menu', args=[self.restaurant.id, customer.username])).status_code, 200)

    def test_signup_hashes_password_and_redirects(self):
        response = self.client.post(reverse('signup'), {
            'username': 'new-user',
            'password': 'a-secure-password',
            'email': 'new@example.com',
            'mobile': '9876543210',
            'address': 'Gurugram',
        })
        self.assertRedirects(response, reverse('customer_home', args=['new-user']))
        customer = Customer.objects.get(username='new-user')
        self.assertNotEqual(customer.password, 'a-secure-password')
        self.assertTrue(check_password('a-secure-password', customer.password))

    def test_cart_requires_post_and_checkout_handles_empty_cart(self):
        customer = Customer.objects.create(
            username='buyer', password='unused', email='b@example.com',
            mobile='9876543210', address='Gurugram'
        )
        add_url = reverse('add_to_cart', args=[self.item.id, customer.username])
        self.assertEqual(self.client.get(add_url).status_code, 405)
        response = self.client.post(add_url)
        self.assertRedirects(response, reverse('view_menu', args=[self.restaurant.id, customer.username]))
        self.assertEqual(self.client.get(reverse('show_cart', args=[customer.username])).status_code, 200)
        customer.cart.first().items.clear()
        response = self.client.get(reverse('checkout', args=[customer.username]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Your cart is empty')

    def test_delete_restaurant_is_post_only(self):
        delete_url = reverse('delete_restaurant', args=[self.restaurant.id])
        self.assertEqual(self.client.get(delete_url).status_code, 405)
        response = self.client.post(delete_url)
        self.assertRedirects(response, reverse('open_show_restaurant'))
        self.assertFalse(Restaurant.objects.filter(id=self.restaurant.id).exists())

    def test_management_and_order_pages_render(self):
        customer = Customer.objects.create(
            username='admin', password='unused', email='a@example.com',
            mobile='9876543210', address='Gurugram'
        )
        for url in (
            reverse('admin_home'),
            reverse('open_add_restaurant'),
            reverse('open_show_restaurant'),
            reverse('open_update_restaurant', args=[self.restaurant.id]),
            reverse('open_update_menu', args=[self.restaurant.id]),
            reverse('checkout', args=[customer.username]),
            reverse('orders', args=[customer.username]),
        ):
            self.assertIn(self.client.get(url).status_code, (200, 503), url)
