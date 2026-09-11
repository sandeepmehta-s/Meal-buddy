from django.db import models

# Create your models here.
class Customer(models.Model):
    username = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=128)
    email = models.EmailField(max_length=254)
    mobile = models.CharField(max_length=10)
    address = models.CharField(max_length=255)

    def __str__(self):
        return self.username

class Restaurant(models.Model):
    name = models.CharField(max_length=80, unique=True)
    picture = models.URLField(max_length = 200, default='https://designshack.net/wp-content/uploads/Free-Simple-Restaurant-Logo-Template.jpg')
    cuisine = models.CharField(max_length = 200)
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=0)

    def __str__(self):
        return self.name
    
class Item(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete = models.CASCADE, related_name = "items")
    name = models.CharField(max_length=80)
    description = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    vegeterian = models.BooleanField(default=False)
    picture = models.URLField(max_length = 400, default='https://www.indiafilings.com/learn/wp-content/uploads/2024/08/How-to-Start-Food-Business.jpg')

    class Meta:
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(fields=['restaurant', 'name'], name='unique_item_per_restaurant'),
        ]

    def __str__(self):
        return self.name

class Cart(models.Model):
    customer = models.ForeignKey(Customer, on_delete = models.CASCADE, related_name = "cart")
    items = models.ManyToManyField("Item", related_name = "carts")

    def total_price(self):
        return sum(item.price for item in self.items.all())
    