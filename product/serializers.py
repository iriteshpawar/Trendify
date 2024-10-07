from rest_framework import serializers

from .models import Category, Product, Review, Wishlist

# class CategorySerializer(serializers.Serializer):
#     name = serializers.CharField(max_length=100)
#     description = serializers.CharField()
#     is_active = serializers.BooleanField(default=True, required=False)
#     parent_category = serializers.CharField(required=False, allow_null=True)

# parent_category = serializers.SlugRelatedField(
#     queryset=Category.objects.all(),
#     slug_field='public_id',
#     allow_null=True,
#     required=False
# )

# parent_category = serializers.PrimaryKeyRelatedField(
#     queryset=Category.objects.all(),
#     required=False,
#     allow_null=True,
#     write_only=True,
# )


class CategoryDetailSerializer(serializers.ModelSerializer):

    parent_category = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            "id",
            "public_id",
            "name",
            "description",
            "is_active",
            "parent_category",
            "user",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "public_id",
            "created_at",
            "updated_at",
        ]

    def get_parent_category(self, obj):
        if obj.parent_category:
            print(
                f"Parent Category: {obj.parent_category.public_id}, {obj.parent_category.name}"
            )
            return {
                "public_id": obj.parent_category.public_id,
                "name": obj.parent_category.name,
            }
        return None


class ProductSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    description = serializers.CharField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    quantity = serializers.IntegerField()
    category = serializers.CharField()
    Highlights = serializers.CharField()
    Warranty = serializers.CharField()
    image = serializers.ImageField(required=False, allow_null=True)
    release_date = serializers.DateField()
    weight = serializers.FloatField()
    is_available = serializers.BooleanField(default=True)
    refund_period = serializers.IntegerField()
    discount = serializers.IntegerField(default=0)


class ProductDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "id",
            "public_id",
            "name",
            "description",
            "price",
            "Highlights",
            "Warranty",
            "quantity",
            "category",
            "image",
            "release_date",
            "weight",
            "is_available",
            "discount",
            "refund_period",
            "user",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "public_id",
            "refund_period",
            "category",
            "user",
            "release_date",
            "created_at",
            "updated_at",
        ]


class ReviewSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = [
            "id",
            "product",
            "user",
            "rating",
            "title",
            "comment",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "product", "user", "created_at", "updated_at"]

    def get_user(self, obj):
        if obj.user:
            customer = obj.user
            full_name = f"{customer.first_name} {customer.last_name}"
            return {
                "public_id": customer.public_id,
                "name": full_name,
            }
        return None

    def get_product(self, obj):
        if obj.product:
            return {
                "public_id": obj.product.public_id,
                "name": obj.product.name,
            }
        return None


class WishlistSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    products = serializers.SerializerMethodField()

    class Meta:
        model = Wishlist
        fields = ["user", "products"]

    def get_user(self, obj):
        if obj.user:
            customer = obj.user
            full_name = f"{customer.first_name} {customer.last_name}"
            return {
                "public_id": customer.public_id,
                "name": full_name,
            }
        return None

    def get_products(self, obj):
        return [
            {
                "product_id": product.public_id,
                "name": product.name,
                "price": product.price,
            }
            for product in obj.products.all()
        ]

    read_only_fields = [
        "user",
    ]
