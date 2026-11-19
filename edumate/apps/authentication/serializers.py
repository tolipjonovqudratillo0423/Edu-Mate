from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError

from apps.users.models import User

class LoginSerializer(serializers.Serializer):
    
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def validate_email(self, value):
        return value.strip().lower()
    


class RegisterSerializer(serializers.ModelSerializer):

    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=30)
    last_name = serializers.CharField(max_length=30)
    second_name = serializers.CharField(max_length=30, required=False, allow_blank=True)
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    
    class Meta:
        
        model = User
        fields = [
            "email",
            "first_name",
            "last_name",
            "second_name",
            "password",
            "password2"
        ]
        extra_kwargs = {
            "password": {"write_only": True}
        }
    

    def validate_email(self, value):
        value = value.strip().lower()
       
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists")
        return value


    def validate(self, attrs):
            
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError("Passwords do not match")
        
        if attrs["password"].strip() == "":
            raise serializers.ValidationError("Password cannot be empty")
        
        if attrs["password2"].strip() == "":
            raise serializers.ValidationError("Password cannot be empty")
        try:
            validate_password(attrs["password"])  # runs AUTH_PASSWORD_VALIDATORS
        except DjangoValidationError as exc:      # Django's error is not DRF's -> convert
            raise serializers.ValidationError({"password": list(exc.messages)})
        return attrs
    
    
    def create(self, validated_data):
        
        password2 = validated_data.pop("password2")
        
        user = User.objects.create_user(
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            password=validated_data["password"]
            )
        user.save()
        return user
    


class VCodeSerializer(serializers.Serializer):
    
    code = serializers.CharField()
    
    

class RefreshTokenSerializer(serializers.Serializer):
    
    refresh = serializers.CharField()
    
    