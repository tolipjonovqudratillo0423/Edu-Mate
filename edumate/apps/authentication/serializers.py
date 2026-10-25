from rest_framework import serializers

from apps.users.models import User

class LoginSerializer(serializers.Serializer):
    
    email = serializers.CharField()
    password = serializers.CharField()
    


class RegisterSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    
    class Meta:
        
        model = User
        fields = [
            "email",
            "first_name",
            "last_name",
            "password",
            "password2"
        ]
        extra_kwargs = {
            "password": {"write_only": True}
        }
    
    def validate(self, attrs):
        
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError("Passwords do not match")
        
        if attrs["password"].strip() == "":
            raise serializers.ValidationError("Password cannot be empty")
        
        if attrs["password2"].strip() == "":
            raise serializers.ValidationError("Password cannot be empty")
    
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
    
    