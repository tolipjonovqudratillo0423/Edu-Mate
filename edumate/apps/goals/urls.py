from django.urls import path

from apps.goals.views import (
    GoalListCreateView,
    GoalDetailView,
    AvailabilityListCreateView,
    AvailabilityDetailView,
)

urlpatterns = [
    # Goals
    path("", GoalListCreateView.as_view(), name="goal-list-create"),
    path("<int:pk>/", GoalDetailView.as_view(), name="goal-detail"),

    # Availability
    path("availability/", AvailabilityListCreateView.as_view(), name="availability-list-create"),
    path("availability/", AvailabilityListCreateView.as_view(), name="availability"),
    path("availability/<int:pk>/", AvailabilityDetailView.as_view(), name="availability-detail"),
]
