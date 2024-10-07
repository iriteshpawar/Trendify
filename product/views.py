from django.db.models import Q
from django.shortcuts import render
from oauth2_provider.contrib.rest_framework import (
    OAuth2Authentication, TokenMatchesOASRequirements)
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from common.models import PublicId
from product.models import Category, Product, Review
from product.services import CreateCateoryService
from user_management.models import User

from .models import Wishlist
from .serializers import (CategoryDetailSerializer, ProductDetailSerializer,
                          ProductSerializer, ReviewSerializer,
                          WishlistSerializer)

# Create your views here.


class CategoryView(APIView):
    authentication_classes = [OAuth2Authentication]
    permission_classes = [TokenMatchesOASRequirements]
    required_alternate_scopes = {"POST": [["create"]]}

    def post(self, request, *args, **kwargs):
        serializer = CategoryDetailSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            return CreateCateoryService.execute(
                {"payload": serializer.validated_data, "user": request.user}
            )


class CategoryUpdateView(APIView):
    authentication_classes = [OAuth2Authentication]
    permission_classes = [TokenMatchesOASRequirements]
    required_alternate_scopes = {"PATCH": [["update"]]}

    def patch(self, request, public_id, *args, **kwargs):
        if request.user.is_superuser:
            try:
                category = Category.objects.get(public_id=public_id)
                serializer = CategoryDetailSerializer(
                    category, data=request.data, partial=True
                )
                if serializer.is_valid(raise_exception=True):
                    serializer.save()
                    return Response(
                        {
                            "message": "Category Update sucessfully",
                            "data": serializer.data,
                        },
                        status=status.HTTP_201_CREATED,
                    )
            except Category.DoesNotExist:
                return Response(
                    {"error": "category doesn't exists"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                {"error": "Permission denied. Only superusers can update categories."},
                status=status.HTTP_403_FORBIDDEN,
            )


class CategoryAccessView(APIView):
    def get(self, request, public_id=None, *args, **kwargs):
        if public_id:
            try:
                category = Category.objects.get(public_id=public_id)
                serializer = CategoryDetailSerializer(category)
                return Response(
                    {"message": "category fetch successfully", "data": serializer.data},
                    status=status.HTTP_200_OK,
                )
            except Category.DoesNotExist:
                return Response(
                    {"error": "category doesn't exists"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        else:
            try:
                category = Category.objects.all()
                serializer = CategoryDetailSerializer(category, many=True)
                return Response(
                    {"message": "fetch category list", "data": serializer.data},
                    status=status.HTTP_200_OK,
                )
            except Category.DoesNotExist:
                return Response(
                    {"error": "category doesn't exist"},
                    status=status.HTTP_400_BAD_REQUEST,
                )


class ProductView(APIView):
    authentication_classes = [OAuth2Authentication]
    permission_classes = [TokenMatchesOASRequirements]
    required_alternate_scopes = {"POST": [["create"]]}

    def post(self, request, *args, **kwargs):
        if request.user.is_superuser or request.user.is_seller:
            try:
                serializer = ProductSerializer(data=request.data)
                if serializer.is_valid(raise_exception=True):
                    user = request.user
                    category_id = request.data["category"]
                    category_instance = None

                    if category_id:
                        try:
                            category_instance = Category.objects.get(
                                public_id=category_id
                            )
                        except Category.DoesNotExist:
                            return Response(
                                {"error": "Parent category does not exist"},
                                status=status.HTTP_400_BAD_REQUEST,
                            )
                    product = Product.objects.create(
                        public_id=PublicId.create_public_id(),
                        name=request.data["name"],
                        description=request.data.get("description"),
                        price=request.data["price"],
                        quantity=request.data["quantity"],
                        category=category_instance,
                        image=request.data.get("image"),
                        Highlights=request.data.get("Highlights"),
                        Warranty=request.data.get("Warranty"),
                        release_date=request.data["release_date"],
                        weight=request.data["weight"],
                        refund_period = request.data.get("refund_period"),
                        is_available=request.data.get("is_available"),
                        discount=request.data.get("discount"),
                        user=user,
                    )
                    return Response(
                        {"message": "Product add successfully"},
                        status=status.HTTP_201_CREATED,
                    )
            except Exception as e:
                return Response(
                    {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        else:
            return Response(
                {
                    "error": "Permission denied. Only superusers and seller can create products."
                },
                status=status.HTTP_403_FORBIDDEN,
            )


class ProductUpdateView(APIView):
    authentication_classes = [OAuth2Authentication]
    permission_classes = [TokenMatchesOASRequirements]
    required_alternate_scopes = {"PATCH": [["update"]]}

    def patch(self, request, public_id, *args, **kwargs):
        try:
            product = Product.objects.get(public_id=public_id)
            if request.user.is_superuser or product.user == request.user:
                serializer = ProductDetailSerializer(
                    product, data=request.data, partial=True
                )
                if serializer.is_valid(raise_exception=True):
                    serializer.save()
                return Response(
                    {"message": "Update Product", "data": serializer.data},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"error": "You do not have permission to update this product."},
                    status=status.HTTP_403_FORBIDDEN,
                )
        except Product.DoesNotExist:
            return Response(
                {"error": "Product doesn't exist"}, status=status.HTTP_400_BAD_REQUEST
            )


class ProductAccessView(APIView):
    authentication_classes = [OAuth2Authentication]
    permission_classes = [TokenMatchesOASRequirements]
    required_alternate_scopes = {"GET": [["read"]]}

    def get(self, request, public_id=None, *args, **kwargs):
        if public_id:
            try:
                product = Product.objects.get(public_id=public_id)
                if request.user.is_superuser or product.user == request.user:
                    serializer = ProductDetailSerializer(product)
                    return Response(
                        {"message": "Fetch product list", "data": serializer.data},
                        status=status.HTTP_200_OK,
                    )
                else:
                    return Response(
                        {"error": "You do not have permission to get this product."},
                        status=status.HTTP_403_FORBIDDEN,
                    )
            except Product.DoesNotExist:
                return Response(
                    {"error": "Product doesn't exist"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            try:
                if request.user.is_superuser:
                    products = Product.objects.all()
                    serializer = ProductDetailSerializer(products, many=True)
                    return Response(
                        {"message": "Fetch all products", "data": serializer.data},
                        status=status.HTTP_200_OK,
                    )
                else:
                    products = Product.objects.filter(user=request.user)
                    serializer = ProductDetailSerializer(products, many=True)
                    return Response(
                        {"message": "Fetch your products", "data": serializer.data},
                        status=status.HTTP_200_OK,
                    )
            except Product.DoesNotExist:
                return Response(
                    {"error": "Product doesn't exist"},
                    status=status.HTTP_400_BAD_REQUEST,
                )


class PublicProductView(APIView):
    def get(self, request, public_id=None, *args, **kwargs):
        if public_id:
            try:
                product = Product.objects.get(public_id=public_id)
                serializer = ProductDetailSerializer(product)
                return Response(
                    {"message": "Fetch product list", "data": serializer.data},
                    status=status.HTTP_200_OK,
                )
            except Product.DoesNotExist:
                return Response(
                    {"error": "Product doesn't exist"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            try:
                products = Product.objects.all()
                paginator = PageNumberPagination()
                product_paginated = paginator.paginate_queryset(products, request)
                serializer = ProductDetailSerializer(product_paginated, many=True)
                return paginator.get_paginated_response(
                    {"message": "Fetch all products", "data": serializer.data}
                )
            except Product.DoesNotExist:
                return Response(
                    {"error": "Product doesn't exist"},
                    status=status.HTTP_400_BAD_REQUEST,
                )


class ReviewView(APIView):

    authentication_classes = [OAuth2Authentication]
    permission_classes = [TokenMatchesOASRequirements]
    required_alternate_scopes = {
        "POST": [["create"]],
        "PATCH": [["update"]],
    }

    def post(self, request, *args, **kwargs):
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):

            user_id = request.data.get("user")
            user = None
            if user_id:
                user = User.objects.get(public_id=user_id)

            product_id = request.data.get("product")
            product = None
            if product_id:
                product = Product.objects.get(public_id=product_id)

            Review.objects.create(
                user=user,
                product=product,
                rating=request.data["rating"],
                title=request.data.get("title"),
                comment=request.data.get("comment"),
            )
            return Response(
                {"success": "Review added successfully"}, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, id, *args, **kwargs):
        try:
            review = Review.objects.get(id=id)
            if request.user != review.user:
                return Response(
                    {"error": "You do not have permission to update this review."}
                )
            serializer = ReviewSerializer(review, data=request.data, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(
                    {"success": "Review updated successfully", "data": serializer.data},
                    status=status.HTTP_200_OK,
                )
        except Review.DoesNotExist:
            return Response(
                {"error": "Review not found"}, status=status.HTTP_404_NOT_FOUND
            )


class ReviewAccessView(APIView):
    def get(self, request, *args, **kwargs):
        reviews = Review.objects.all()
        serializer = ReviewSerializer(reviews, many=True)
        return Response({"reviews": serializer.data}, status=status.HTTP_200_OK)


class WhishlistView(APIView):

    authentication_classes = [OAuth2Authentication]
    permission_classes = [TokenMatchesOASRequirements]
    required_alternate_scopes = {
        "GET": [["read"]],
        "POST": [["create"]],
        "DELETE": [["delete"]],
    }

    def post(self, request, *args, **kwargs):

        user_id = request.data.get("user")
        product_ids = request.data.get("products")

        try:
            user = User.objects.get(public_id=user_id)
            products = Product.objects.filter(public_id=product_ids)

            person = request.user
            wishlist, created = Wishlist.objects.get_or_create(user=person)
            wishlist.products.add(*products)

            serializer = WishlistSerializer(wishlist)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
            )
        except User.DoesNotExist:
            return Response(
                {"error": "user does not exist"}, status=status.HTTP_404_NOT_FOUND
            )
        except Product.DoesNotExist:
            return Response(
                {"error": "Product does not exist"}, status=status.HTTP_404_NOT_FOUND
            )

    def get(self, request, *args, **kwargs):
        try:
            wishlist = Wishlist.objects.get(user=request.user)

            serializer = WishlistSerializer(wishlist)
            return Response(
                {"message": "Fetched wishlist", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        except Wishlist.DoesNotExist:
            return Response(
                {"error": "Wishlist does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )

    def delete(self, request, *args, **kwargs):

        product_id = request.data.get("products")

        try:
            product = Product.objects.get(public_id=product_id)
            whishlist = Wishlist.objects.get(user=request.user)

            if product in whishlist.products.all():
                whishlist.products.remove(product)
                whishlist.save()

            serializer = WishlistSerializer(whishlist)
            return Response(
                {"message": "remove product successfully", "data": serializer.data}
            )
        except Product.DoesNotExist:
            return Response(
                {"error": "Product does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )

        except Wishlist.DoesNotExist:
            return Response(
                {"error": "Whishlist does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )
