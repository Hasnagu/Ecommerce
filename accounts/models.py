from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from shop.models import Product


class CustomUser(AbstractUser):
    is_client = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    def __str__(self):
        return self.username


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=50, default="cash")
    status = models.CharField(max_length=20, default="en_attente")
    created_at = models.DateTimeField(auto_now_add=True)

    # SUPPRESSION des champs :
    # shipping_address
    # postal_code

    def __str__(self):
        return f"Order #{self.id}"

    @property
    def total_price(self):
        return sum(item.subtotal for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def subtotal(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.product.name} x{self.quantity}"
