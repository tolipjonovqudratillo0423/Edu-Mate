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
            "is_onboarded",
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
            "is_hidden",
        ]     
        extra_kwargs = {
            "avg_rating": {"read_only":True},
            "sessions_completed": {"read_only":True},
            "user": {"read_only":True} 
        }
        
    def validate_age_group(self, value):
        if self.instance and self.instance.age_group != value:
            raise serializers.ValidationError("Age group cannot be changed")
        return value
    
    def create(self, validated_data):
        
        profile = Profile.objects.create(
            **validated_data
        )
        return profile
    

    def update(self,  instance, validated_data):
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
    
    

        
        
