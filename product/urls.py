from django.urls import path

from .views import (CategoryAccessView, CategoryUpdateView, CategoryView,
                    ProductAccessView, ProductUpdateView, ProductView,
                    PublicProductView, ReviewAccessView, ReviewView,
                    WhishlistView)

urlpatterns = [
    path("category/", CategoryView.as_view(), name="add-category"),
    path(
        "category/<int:public_id>/",
        CategoryUpdateView.as_view(),
        name="update-category",
    ),
    path(
        "categoryaccess/",
        CategoryAccessView.as_view(),
        name="update-category",
    ),
    path(
        "categoryaccess/<int:public_id>/",
        CategoryAccessView.as_view(),
        name="update-category",
    ),
    path("item/", ProductView.as_view(), name="add-product"),
    path("item/<int:public_id>/", ProductUpdateView.as_view(), name="update-product"),
    path("itemaccess/", ProductAccessView.as_view(), name="update-product"),
    path(
        "itemaccess/<int:public_id>/",
        ProductAccessView.as_view(),
        name="update-product",
    ),
    path("public_product/", PublicProductView.as_view(), name="see-products"),
    path("review/", ReviewView.as_view(), name="add-review"),
    path("review/<int:id>/", ReviewView.as_view(), name="update-review"),
    path("reviewaccess/", ReviewAccessView.as_view(), name="see-review"),
    path("whishlist/", WhishlistView.as_view(), name="Whish-list"),
]
