from django.db import models
from django.db.models import Q
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

from apps.common.models import BaseModel

class UserManager(BaseUserManager):
    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields["is_staff"] is not True:
            raise ValueError("Superuser must have is_staff=True")
        if extra_fields["is_superuser"] is not True:
            raise ValueError("Superuser must have is_superuser=True")
        return self.create_user(email, password, **extra_fields)
        

class User(AbstractBaseUser, PermissionsMixin, BaseModel):
    
    email = models.EmailField(unique=True, null=True, blank=True)
    telegram_id = models.BigIntegerField(unique=True, null=True, blank=True)
    telegram_username = models.CharField(max_length=64, blank=True)
    # Only set after Telegram confirmed it (request_contact), never user-typed
    phone_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
 
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_onboarded = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
 
    objects = UserManager()
 
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"    
            
        constraints = [
           
            models.CheckConstraint(
                condition=Q(email__isnull=False) | Q(telegram_id__isnull=False),
                name="user_has_email_or_telegram",
            )
        ]


class Profile(BaseModel):
    
    class AgeGroup(models.TextChoices):
        UNDER_18 = "under_18", "Under 18"
        ADULT = "adult", "18+"
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )
    full_name = models.CharField(
        max_length=100
    )
    city = models.CharField(
        max_length=100,
        blank=True
    )
    bio = models.TextField(
        max_length=500,
        blank=True
    )
    image = models.ImageField(
        upload_to="profile/",
        null=True,
        blank=True
    )
    age_group = models.CharField(
        max_length=10,
        choices=AgeGroup.choices,
    )
    is_hidden = models.BooleanField(
        default=False
    )
    sessions_completed = models.PositiveIntegerField(
        default=0
    )
    avg_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True
    )
 
    def __str__(self):
        return self.full_name
 
    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"
        
        indexes = [
            
            models.Index(
                fields=["age_group", "user"],
                name="age_group_user_idx"
            ),                                  
            models.Index(
                fields=["city", "user"],
                name="city_user_idx"
            ),
            
        ]
        