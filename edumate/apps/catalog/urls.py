from django.urls import path

from apps.catalog.views import TrackListView

urlpatterns = [
    path("tracks/", TrackListView.as_view(), name="track-list"),
]
