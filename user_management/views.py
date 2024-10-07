import random
from datetime import datetime, timedelta, timezone

from django.contrib.auth import authenticate
from django.core.mail import EmailMultiAlternatives
from django.db import IntegrityError
from django.shortcuts import render
from django.template.loader import render_to_string
from oauth2_provider.contrib.rest_framework import (
    OAuth2Authentication, TokenMatchesOASRequirements)
from oauth2_provider.models import Application, RefreshToken
from oauth2_provider.oauth2_validators import AccessToken
from oauth2_provider.settings import oauth2_settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from common.models import PublicId
from common.token_generator import generate_token
from Trendify.settings import EMAIL_HOST_USER

from .models import Role, User
from .serializers import (
    ChangePasswordSerializer, ResetOTPSerializer, SellerRegistrationSerializer,
    SellerSerializer, SuperuserRegistrationSerializer, SuperuserSerializer,
    UserRegistrationSerializer, UserSerializer, loginSerializer)


class UserRegistrationView(APIView):

    def post(self, request, *args, **kwargs):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            email = serializer.validated_data["email"]
            if User.objects.filter(email=email).exists():
                return Response(
                    {"error": "User with this email already exists."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                user = User.objects.create(
                    public_id=PublicId.create_public_id(),
                    first_name=request.data["first_name"],
                    last_name=request.data["last_name"],
                    username=request.data["email"],
                    email=request.data["email"],
                    address=request.data.get("address"),
                    date_of_birth=request.data.get("date_of_birth"),
                    phone_no=request.data["phone_no"],
                )
                user.set_password(request.data["password"])
                user.save()
                role = Role.objects.get(name="User")
                user.roles.add(role)
                return Response(
                    {"message": "User added successfully", "data": serializer.data},
                    status=status.HTTP_201_CREATED,
                )

            except ValueError as e:
                return Response(
                    {"error": "Invalid data provided."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            except IntegrityError as e:
                return Response(
                    {"error": "User with this email already exists."},
                    status=status.HTTP_400_BAD_REQUEST,
                )


class UserView(APIView):

    # authentication_classes = [OAuth2Authentication]
    # permission_classes = [TokenMatchesOASRequirements]
    # required_alternate_scopes = {
    #     "GET": [["read"]],
    # }

    def get(self, request, *args, **kwargs):
        # if request.user.is_superuser:
        role = Role.objects.get(name="User")
        users = User.objects.filter(roles=role)
        if not users.exists():
            return Response(
                {"message": "No users found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = UserSerializer(users, many=True)
        return Response(
            {"message": "User list fetched successfully", "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    # else:
    #     return Response(
    #         {"error": "Permission denied."},
    #         status=status.HTTP_403_FORBIDDEN,
    #     )


class SellerRegistrationView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = SellerRegistrationSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            email = serializer.validated_data["email"]
            if User.objects.filter(email=email).exists():
                return Response(
                    {"error": "Seller with this email already exists."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                user = User.objects.create(
                    public_id=PublicId.create_public_id(),
                    first_name=request.data["first_name"],
                    last_name=request.data["last_name"],
                    username=email,
                    email=email,
                    address=request.data.get("address"),
                    date_of_birth=request.data.get("date_of_birth"),
                    store_name=request.data.get("store_name"),
                    phone_no=request.data["phone_no"],
                    is_seller=request.data["is_seller"],
                )
                user.set_password(request.data["password"])
                user.save()

                role = Role.objects.get(name="Seller")
                user.roles.add(role)
                return Response(
                    {"message": "Seller added successfully", "data": serializer.data},
                    status=status.HTTP_201_CREATED,
                )

            except ValueError as e:
                return Response(
                    {"error": "Invalid data provided."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            except IntegrityError as e:
                return Response(
                    {"error": "Seller with this email already exists."},
                    status=status.HTTP_400_BAD_REQUEST,
                )


class SellerView(APIView):

    authentication_classes = [OAuth2Authentication]
    permission_classes = [TokenMatchesOASRequirements]
    required_alternate_scopes = {
        "GET": [["read"]],
    }

    def get(self, request, *args, **kwargs):
        if request.user.is_superuser:
            query = User.objects.filter(is_seller=True)
            if not query.exists():
                return Response(
                    {"message": "No seller found."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            serializer = SellerSerializer(query, many=True)
            return Response(
                {
                    "message": "seller list fetched successfully",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"error": "Permission denied."},
                status=status.HTTP_403_FORBIDDEN,
            )


class SuperuserRegistrationView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = SuperuserRegistrationSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            email = serializer.validated_data["email"]
            if User.objects.filter(email=email).exists():
                return Response(
                    {"error": "Superuser with this email already exists."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                user = User.objects.create(
                    public_id=PublicId.create_public_id(),
                    first_name=serializer.validated_data["first_name"],
                    last_name=serializer.validated_data["last_name"],
                    username=email,
                    email=email,
                    address=serializer.validated_data.get("address"),
                    date_of_birth=serializer.validated_data.get("date_of_birth"),
                    phone_no=serializer.validated_data["phone_no"],
                )
                user.set_password(serializer.validated_data["password"])
                user.is_superuser = True
                user.is_staff = True
                user.save()

                # Add superuser role
                role = Role.objects.get(name="Superadmin")
                user.roles.add(role)

                return Response(
                    {
                        "message": "Superuser added successfully",
                        "data": serializer.data,
                    },
                    status=status.HTTP_201_CREATED,
                )
            except Role.DoesNotExist:
                return Response(
                    {"error": "Role 'superadmin' does not exist."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            except Exception as e:
                return Response(
                    {"error": str(e)},
                    status=status.HTTP_400_BAD_REQUEST,
                )


class SuperuserView(APIView):

    authentication_classes = [OAuth2Authentication]
    permission_classes = [TokenMatchesOASRequirements]
    required_alternate_scopes = {
        "GET": [["read"]],
    }

    def get(self, request, *args, **kwargs):
        if request.user.is_superuser:
            query = User.objects.filter(is_superuser=True)
            if not query.exists():
                return Response(
                    {"message": "No users found."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            serializer = SuperuserSerializer(query, many=True)
            return Response(
                {
                    "message": "Superuser list fetched successfully",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"error": "Permission denied."},
                status=status.HTTP_403_FORBIDDEN,
            )


class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = loginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            email = serializer.validated_data["email"]
            password = serializer.validated_data["password"]

            try:
                user = User.objects.get(email=email)
                if not user.is_active:
                    return Response(
                        {
                            "error": "Your account is not active. Please contact support for assistance."
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                auth_user = authenticate(username=email, password=password)

                if auth_user is None:
                    return Response(
                        {"error": "Invalid Credentials."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                app = Application()
                app.authorization_grant_type = "password"
                app.client_type = "client-credentials"
                app.redirect_uris = request.build_absolute_uri("/")
                app.save()

                access_token = AccessToken.objects.create(
                    user=auth_user,
                    application=app,
                    token=generate_token(request),
                    expires=datetime.now(timezone.utc)
                    + timedelta(seconds=oauth2_settings.ACCESS_TOKEN_EXPIRE_SECONDS),
                    scope="read create update delete",
                )

                refresh_token = RefreshToken.objects.create(
                    user=auth_user,
                    application=app,
                    token=generate_token(request),
                    access_token=access_token,
                )

                token = {
                    "access_token": access_token.token,
                    "expires_in": oauth2_settings.ACCESS_TOKEN_EXPIRE_SECONDS,
                    "refresh_token": refresh_token.token,
                    "token_type": "Bearer",
                }

                token["access_token"] = (
                    token.pop("token_type") + " " + token["access_token"]
                )
                if auth_user.is_superuser:
                    token["role"] = "Superuser"
                elif auth_user.is_seller:
                    token["role"] = "Seller"
                    token["store_name"] = auth_user.store_name
                else:
                    token["role"] = "User"

                token["name"] = auth_user.first_name + auth_user.last_name
                token["email"] = auth_user.email
                token["phone_no"] = auth_user.phone_no
                return Response(
                    {"message": "Logged in successfully", "token": token},
                    status=status.HTTP_200_OK,
                )

            except User.DoesNotExist:
                return Response(
                    {"error": "Invalid Credentials."},
                    status=status.HTTP_400_BAD_REQUEST,
                )


class LogoutView(APIView):
    authentication_classes = [OAuth2Authentication]
    permission_classes = [TokenMatchesOASRequirements]

    required_alternate_scopes = {
        "DELETE": [["delete"]],
    }

    @staticmethod
    def delete(request):
        token = request._auth.token
        access_token = AccessToken.objects.get(token=token)
        access_token.application.delete()
        access_token.delete()
        return Response({"Logout": "Logout successfully"}, status.HTTP_200_OK)


class ChangePasswordView(APIView):
    authentication_classes = [OAuth2Authentication]
    permission_classes = [TokenMatchesOASRequirements]
    required_alternate_scopes = {"PATCH": [["update"]]}

    def patch(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer_data = serializer.validated_data
            users = request.user
            if not users.check_password(serializer_data["password"]):
                return Response(
                    {
                        "error": "The current password you have entered is wrong. Please try again !"
                    }
                )
            new_password = serializer_data["new_password"]
            users.password = new_password
            users.set_password(new_password)
            users.save()
            AccessToken.objects.filter(user=request.user).delete()
            return Response({"message": "Password Changed successfully"})


class ResetOTPView(APIView):

    def post(self, request, *args, **kwargs):
        serializer = ResetOTPSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer_data = serializer.validated_data
            email = serializer_data["email"]
            if not email:
                return Response({"error": "email is not found"})

            user = User.objects.filter(email=email).first()
            if not user:
                return Response({"error": "User is not found"})

            otp = random.randint(100000, 999999)
            user.otp = otp
            user.save()

            context = {
                "otp": user.otp,
                "user": user.first_name,
            }

            email_html_content = render_to_string("forget_password_otp.html", context)

            msg = EmailMultiAlternatives(
                "Your OTP Code", email_html_content, EMAIL_HOST_USER, [email]
            )
            msg.attach_alternative(email_html_content, "text/html")
            msg.send()
            return Response(
                {"success": "OTP sent to email"},
                status=status.HTTP_200_OK,
            )


class VerifyOTPView(APIView):

    def post(self, request):
        try:

            public_id = request.data.get("public_id")
            otp = request.data.get("otp")

            # Check if public_id and otp are provided in the request
            if not public_id or not otp:
                return Response(
                    {"error": "OTP is required"}, status=status.HTTP_400_BAD_REQUEST
                )

            # Attempt to find the user with the provided public_id and otp
            user = User.objects.filter(public_id=public_id, otp=otp).first()
            if not user:
                return Response(
                    {"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST
                )

            # Clear the OTP after successful verification
            user.otp = None  # Clear the OTP after verification
            user.save()

            return Response(
                {"success": "OTP verified", "public_id": user.public_id},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ResetPasswordView(APIView):
    def post(self, request):
        try:
            public_id = request.data.get("public_id")
            password = request.data.get("password")
            confirm_password = request.data.get("confirm_password")

            if not public_id or not password or not confirm_password:
                return Response(
                    {"error": "password is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if password != confirm_password:

                return Response(
                    {"error": "Passwords do not match"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user = User.objects.filter(public_id=public_id).first()
            if not user:
                return Response(
                    {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
                )

            user.set_password(password)
            user.save()

            return Response(
                {"success": "Password reset successfull"}, status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
