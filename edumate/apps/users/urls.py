from django.urls import path

from apps.users.views import (
    MeView, ProfileView,
)

urlpatterns = [
    path("about-me/", MeView.as_view(), name="about-me"),
    
    # Profile urls
    path("profile/", ProfileView.as_view(), name="user-profile"),
    ]
