from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import serializers

from apps.catalog.serializers import ProductDetailSerializer
from .models import WishlistItem, Profile


class RegisterSerializer(serializers.ModelSerializer):
    name = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True, min_length=8)
    phone = serializers.CharField(required=False, allow_blank=True, write_only=True)

    class Meta:
        model = User
        fields = ["name", "email", "password", "phone"]

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value

    def create(self, validated_data):
        name = validated_data.pop("name")
        phone = validated_data.pop("phone", "")
        user = User.objects.create_user(
            username=validated_data["email"],
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=name,
        )
        Profile.objects.create(user=user, phone=phone)
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(username=attrs["email"], password=attrs["password"])
        if not user:
            raise serializers.ValidationError("Invalid email or password.")
        if not user.is_active:
            raise serializers.ValidationError("This account is inactive.")
        attrs["user"] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="first_name")
    phone = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "name", "email", "phone"]

    def get_phone(self, obj):
        return getattr(getattr(obj, "profile", None), "phone", "")


class WishlistItemSerializer(serializers.ModelSerializer):
    # Nests the same shape used on the product detail page, so the frontend
    # doesn't need a second fetch to render wishlist items.
    product = ProductDetailSerializer(read_only=True)

    class Meta:
        model = WishlistItem
        fields = ["id", "product", "created_at"]
