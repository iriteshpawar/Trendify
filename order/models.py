from django.db import models
from django.utils import timezone

from common.models import BaseModel, UniqueIds
from product.models import Product
from user_management.models import User


class BuyNowOrder(UniqueIds, BaseModel, models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="buy_now_orders"
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="buy_now_orders"
    )
    quantity = models.PositiveIntegerField(default=1)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    order_date = models.DateTimeField(default=timezone.now)
    refund_day = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ("processing", "processing"),
            ("shipped", "shipped"),
            ("delivered", "delivered"),
            ("cancelled", "cancelled"),
        ],
        default="processing",
    )

    def __str__(self):
        return f"BuyNowOrder {self.id} by {self.user}"
    
    
class Cart(UniqueIds, BaseModel, models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="cart")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="cart")
    quantity = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Cart {self.user.id}"


class Order(UniqueIds, BaseModel, models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    cart = models.OneToOneField(
        Cart, on_delete=models.CASCADE, related_name="order", null=True, blank=True
    )
    order_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(
        max_length=20,
        choices=[
            ("processing", "processing"),
            ("shipped", "shipped"),
            ("delivered", "delivered"),
            ("cancelled", "cancelled"),
        ],
    )
    note = models.TextField(max_length=300, null=True, blank=True)

    def __str__(self):
        return f"Order {self.id} by {self.user}"


class OrderItem(BaseModel, models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="order_items"
    )
    product_name = models.CharField(max_length=255)
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order {self.order.id}"


class Discount(models.Model):
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(null=True, blank=True)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Discount Code: {self.code}"


class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="payments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payments")
    payment_method = models.CharField(
        max_length=20,
        choices=[
            ("credit_card", "Credit Card"),
            ("paypal", "PayPal"),
            ("stripe", "Stripe"),
            ("bank_transfer", "Bank Transfer"),
        ],
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ("success", "Success"),
            ("failed", "Failed"),
            ("pending", "Pending"),
        ],
    )
    payment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.id} for Order {self.order.id}"


class ShippingAddress(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="shipping_address"
    )
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name="shipping_address",
        null=True,
        blank=True,
    )
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"Shipping Address for {self.user}"


class RefundRequest(BaseModel, models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="refund_requests"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="refund_requests"
    )
    reason = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=[
            ("requested", "Requested"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
            ("processed", "Processed"),
        ],
        default="requested",
    )
    request_date = models.DateTimeField(auto_now_add=True)
    resolution_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Refund Request {self.id} for Order {self.order.id}"
