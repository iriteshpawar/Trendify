from django.urls import path

from .views import (ChangePasswordView, LoginView, LogoutView, ResetOTPView,
                    ResetPasswordView, SellerRegistrationView, SellerView,
                    SuperuserRegistrationView, SuperuserView,
                    UserRegistrationView, UserView, VerifyOTPView)

urlpatterns = [
    path("registration/", UserRegistrationView.as_view(), name="add-user"),
    path("seller_registration/", SellerRegistrationView.as_view(), name="add-seller"),
    path(
        "superuser_registration/",
        SuperuserRegistrationView.as_view(),
        name="add-superuser",
    ),
    path("user/", UserView.as_view(), name="view-user"),
    path("seller/", SellerView.as_view(), name="view-seller"),
    path("superuser/", SuperuserView.as_view(), name="view-superuser"),
    path("login/", LoginView.as_view(), name="login-user"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("change_password/", ChangePasswordView.as_view(), name="change-password"),
    path("reset_otp/", ResetOTPView.as_view(), name="reset_otp"),
    path("verify_otp/", VerifyOTPView.as_view(), name="verify_otp"),
    path("reset_password/", ResetPasswordView.as_view(), name="reset_password"),
]
