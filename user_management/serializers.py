from rest_framework import serializers

from .models import User


class UserBaseSerializer(serializers.Serializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    address = serializers.CharField(max_length=100, required=False, allow_blank=True)
    phone_no = serializers.CharField()
    date_of_birth = serializers.DateField(required=False)

    def validate_phone_no(self, value):
        if len(value) != 10:
            raise serializers.ValidationError("Enter the correct number")
        return value


class UserRegistrationSerializer(UserBaseSerializer):
    pass


class SellerRegistrationSerializer(UserBaseSerializer):
    is_seller = serializers.BooleanField()
    store_name = serializers.CharField(required=False)


class SuperuserRegistrationSerializer(UserBaseSerializer):
    pass


class BaseSerializer(serializers.ModelSerializer):
    # role_name = serializers.CharField(source ="roles.name")

    roles = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "public_id",
            "first_name",
            "last_name",
            "email",
            "address",
            "roles",
            "phone_no",
            "date_of_birth",
            "created_at",
            "updated_at",
        ]

    def get_roles(self, obj):
        if obj.roles.exists():
            return [role.name for role in obj.roles.all()]
        return None

    read_only_fields = [
        "public_id",
        "email",
        "created_at",
        "updated_at",
    ]


class UserSerializer(BaseSerializer):
    pass


class SellerSerializer(BaseSerializer):
    is_seller = serializers.BooleanField()
    store_name = serializers.CharField(required=False)

    class Meta(BaseSerializer.Meta):
        fields = BaseSerializer.Meta.fields + ["is_seller", "store_name"]

    read_only_fields = [
        "is_seller",
    ]


class SuperuserSerializer(BaseSerializer):
    pass


class loginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField()


class ChangePasswordSerializer(serializers.Serializer):
    password = serializers.CharField()
    new_password = serializers.CharField()
    confirm_new_password = serializers.CharField()

    def validate(self, data):
        if not data.get("new_password") or not data.get("confirm_new_password"):
            raise serializers.ValidationError("Please enter a password and confirm it.")
        if data.get("new_password") != data.get("confirm_new_password"):
            raise serializers.ValidationError(
                "new_password and confirm_new_password is not match !"
            )
        return data


class ResetOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
