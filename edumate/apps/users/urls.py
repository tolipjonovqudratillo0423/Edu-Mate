from django.urls import path

from apps.users.views import UserView

urlpatterns = [
    path("about-me/", UserView.as_view(), name="about-me"),
]
