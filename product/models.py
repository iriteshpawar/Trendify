from django.db import models

from common.models import BaseModel, UniqueIds
from user_management.models import User


# Create your models here.
class Category(UniqueIds, BaseModel, models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True , blank = True)
    is_active = models.BooleanField(default=True)
    parent_category = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subcategories",
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="category",
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.name


class Product(UniqueIds, BaseModel, models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True , blank = True)
    Highlights = models.TextField(null=True , blank = True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    Warranty = models.CharField(null=True , blank = True)
    quantity = models.IntegerField()
    image = models.ImageField(upload_to="category/product/", null=True, blank=True)
    release_date = models.DateField()
    weight = models.FloatField()
    is_available = models.BooleanField(default=True)
    refund_period = models.PositiveIntegerField(null=True , blank = True) 
    discount = models.PositiveIntegerField(default=0, help_text="Discount Percentage")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="products")
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="products"
    )

    def __str__(self):
        return self.name


class Review(BaseModel, models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="reviews"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField(
        default=1, choices=[(i, str(i)) for i in range(1, 6)]
    )
    title = models.CharField(max_length=200, blank=True)
    comment = models.TextField(blank=True)

    def __str__(self):
        return f"Review by {self.user} for {self.product}"


class Wishlist(BaseModel, models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wishlists")
    products = models.ManyToManyField(Product, related_name="wishlists")

    def __str__(self):
        return f"Wishlist for {self.customer}"
