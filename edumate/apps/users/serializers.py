from rest_framework import serializers

from apps.users.models import (
    User, Profile
)


class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        
        model = User
        fields = [
            "email",
            "last_login",
            "first_name",
            "second_name",
            "last_name",
            "telegram_id",
            "telegram_username",
            "phone_number",
            "is_active",
            "is_verified",
        ]
        
    

class ProfileSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False)
    class Meta:
        
        model = Profile
        fields = [
            "user",
            "full_name",
            "city",
            "bio",
            "image",
            "age_group",
            "sessions_completed",
            "avg_rating",
        ]     
        extra_kwargs = {
            "avg_rating": {"read_only":True},
            "sessions_completed": {"read_only":True},
            "user": {"read_only":True} 
        }
    
    def create(self, validated_data):
        
        profile = Profile.objects.create(
            **validated_data
        )
        return profile
    

        
        
