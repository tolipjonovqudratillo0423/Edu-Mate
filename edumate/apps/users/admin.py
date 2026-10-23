from django.contrib import admin

from apps.users.models import User, Profile

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email',  'telegram_username', 'is_verified', 'is_active')
    list_editable = ["is_active", "is_verified"]
    

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'city', 'bio', 'image', 'is_hidden')


