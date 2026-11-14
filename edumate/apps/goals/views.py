from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from drf_spectacular.utils import extend_schema

from apps.goals.serializers import GoalSerializer
from apps.goals.services import GoalService
from apps.common.utils import ResponseMessage


@extend_schema(tags=["Goals"])
class GoalListCreateView(APIView):
    """
    GET  /goals/   → list the authenticated user's own goals
    POST /goals/   → create a new goal (user = request.user)
    """

    permission_classes = [IsAuthenticated]
    serializer_class = GoalSerializer

    @extend_schema(summary="List my goals")
    def get(self, request):
        goals = GoalService.list_my_goals(request.user)
        serializer = self.serializer_class(goals, many=True)
        return ResponseMessage.success(
            message="Goals retrieved successfully.",
            data=serializer.data,
        )

    @extend_schema(summary="Create a goal", request=GoalSerializer)
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Cross-field validation + DB write happen inside the service
        goal = GoalService.create_goal(request.user, serializer.validated_data)
        out = self.serializer_class(goal)
        return ResponseMessage.success(
            message="Goal created successfully.",
            data=out.data,
            status=status.HTTP_201_CREATED,
        )


@extend_schema(tags=["Goals"])
class GoalDetailView(APIView):
    """
    GET         /goals/<id>/  → any authenticated user; 404 if owner is hidden
    PUT / PATCH /goals/<id>/  → owner only; track immutable
    DELETE      /goals/<id>/  → owner only
    """

    permission_classes = [IsAuthenticated]
    serializer_class = GoalSerializer

    @extend_schema(summary="Retrieve a goal")
    def get(self, request, pk):
        goal = GoalService.get_goal(pk, request.user)
        serializer = self.serializer_class(goal)
        return ResponseMessage.success(
            message="Goal retrieved successfully.",
            data=serializer.data,
        )

    @extend_schema(summary="Update a goal (full or partial)", request=GoalSerializer)
    def put(self, request, pk):
        return self._update(request, pk, partial=False)

    @extend_schema(summary="Partially update a goal", request=GoalSerializer)
    def patch(self, request, pk):
        return self._update(request, pk, partial=True)

    def _update(self, request, pk, partial: bool):
        serializer = self.serializer_class(data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        goal = GoalService.update_goal(
            pk, request.user, serializer.validated_data, partial=partial
        )
        out = self.serializer_class(goal)
        return ResponseMessage.success(
            message="Goal updated successfully.",
            data=out.data,
        )

    @extend_schema(summary="Delete a goal")
    def delete(self, request, pk):
        GoalService.delete_goal(pk, request.user)
        return ResponseMessage.success(
            message="Goal deleted successfully.",
            status=status.HTTP_204_NO_CONTENT,
        )
