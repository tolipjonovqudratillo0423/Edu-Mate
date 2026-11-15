from django.urls import path

from apps.matching.views import (
    PartnersView,
    MatchRequestListCreateView,
    MatchRequestDetailView,
    MateListView,
    MateDetailView,
)

urlpatterns = [
    # Partners
    path("partners/", PartnersView.as_view(), name="partners"),

    # Match Requests
    path("match-requests/", MatchRequestListCreateView.as_view(), name="match-request-list-create"),
    path("match-requests/", MatchRequestListCreateView.as_view(), name="match-requests"),
    path("match-requests/<int:pk>/", MatchRequestDetailView.as_view(), name="match-request-detail"),

    # Mates
    path("mates/", MateListView.as_view(), name="mate-list"),
    path("mates/", MateListView.as_view(), name="mates"),
    path("mates/<int:pk>/", MateDetailView.as_view(), name="mate-detail"),
]
