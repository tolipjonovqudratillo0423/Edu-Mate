from django.urls import path

from apps.goals.views import GoalListCreateView, GoalDetailView

urlpatterns = [
    path("", GoalListCreateView.as_view(), name="goal-list-create"),
    path("<int:pk>/", GoalDetailView.as_view(), name="goal-detail"),
]
