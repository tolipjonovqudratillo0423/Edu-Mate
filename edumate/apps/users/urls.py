from django.urls import path

from apps.users.views import MeView

urlpatterns = [
    path("about-me/", MeView.as_view(), name="about-me"),
]
