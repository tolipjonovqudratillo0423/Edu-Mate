from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter

from apps.matching.serializers import (
    PartnerSerializer,
    MatchRequestCreateSerializer,
    MatchRequestUpdateSerializer,
    MatchRequestSerializer,
    MateSerializer,
)
from apps.matching.services import (
    PartnersService,
    MAX_SCORE,
    MatchRequestService,
    MatesService,
)
from apps.matching.models import Match
from apps.common.utils import ResponseMessage


# ======================================================================
# Partners Discovery View
# ======================================================================

@extend_schema(
    tags=["Partners"],
    parameters=[
        OpenApiParameter(
            name="track",
            type=int,
            location=OpenApiParameter.QUERY,
            required=True,
            description="Track ID to find matching study partners for",
        )
    ],
    responses={200: PartnerSerializer(many=True)},
)
class PartnersView(APIView):
    """
    GET /partners/?track=<id>
    Find potential study partners for a specific track.
    Candidates must:
      - have a Goal in the same track
      - have a non-hidden profile
      - not be the requesting user
      - not share an active Match with the user in this track
      - not have a pending MatchRequest with the user in this track (either direction)
    Results are sorted by matching score descending (top 20).
    """

    permission_classes = [IsAuthenticated]
    serializer_class = PartnerSerializer

    @extend_schema(summary="Find matching study partners")
    def get(self, request):
        track_param = request.query_params.get("track")
        if not track_param:
            raise ValidationError({"track": "track query parameter is required."})

        try:
            track_id = int(track_param)
        except (ValueError, TypeError):
            raise ValidationError({"track": "track query parameter must be a valid integer."})

        partners = PartnersService.find_partners(request.user, track_id)
        serializer = self.serializer_class(partners, many=True)
        return ResponseMessage.success(
            message="Partners retrieved successfully.",
            data={"max_score": MAX_SCORE, "results": serializer.data},
        )


# ======================================================================
# MatchRequest Views
# ======================================================================

@extend_schema(tags=["Match Requests"])
class MatchRequestListCreateView(APIView):
    """
    GET  /match-requests/?box=sent|received  → list my requests (default: received)
    POST /match-requests/                   → send a match request (from_user = request.user)
    """

    permission_classes = [IsAuthenticated]
    serializer_class = MatchRequestSerializer

    @extend_schema(
        summary="List match requests",
        parameters=[
            OpenApiParameter(
                name="box",
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Box filter: 'sent' or 'received' (default: 'received')",
            )
        ],
        responses={200: MatchRequestSerializer(many=True)},
    )
    def get(self, request):
        box = request.query_params.get("box", "received")
        requests_qs = MatchRequestService.list_requests(request.user, box=box)
        serializer = self.serializer_class(requests_qs, many=True)
        return ResponseMessage.success(
            message="Match requests retrieved successfully.",
            data=serializer.data,
        )

    @extend_schema(
        summary="Create a match request",
        request=MatchRequestCreateSerializer,
        responses={201: MatchRequestSerializer},
    )
    def post(self, request):
        input_serializer = MatchRequestCreateSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        match_request = MatchRequestService.create_request(request.user, input_serializer.validated_data)
        out = self.serializer_class(match_request)
        return ResponseMessage.success(
            message="Match request created successfully.",
            data=out.data,
            status=status.HTTP_201_CREATED,
        )


@extend_schema(tags=["Match Requests"])
class MatchRequestDetailView(APIView):
    """
    PATCH /match-requests/<id>/  → update request status (accept, decline, cancel)
    Only parties of the request may touch it (others get 404).
    No DELETE allowed.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = MatchRequestSerializer

    @extend_schema(
        summary="Update match request status",
        request=MatchRequestUpdateSerializer,
        responses={200: MatchRequestSerializer},
    )
    def patch(self, request, pk):
        input_serializer = MatchRequestUpdateSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        new_status = input_serializer.validated_data["status"]
        updated_request = MatchRequestService.update_request_status(pk, request.user, new_status)
        out = self.serializer_class(updated_request)
        return ResponseMessage.success(
            message="Match request updated successfully.",
            data=out.data,
        )


# ======================================================================
# Mates Views
# ======================================================================

@extend_schema(tags=["Mates"])
class MateListView(APIView):
    """
    GET /mates/?status=active|ended  → list matches I belong to (default: active)
    """

    permission_classes = [IsAuthenticated]
    serializer_class = MateSerializer

    @extend_schema(
        summary="List mates",
        parameters=[
            OpenApiParameter(
                name="status",
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Status filter: 'active' or 'ended' (default: 'active')",
            )
        ],
        responses={200: MateSerializer(many=True)},
    )
    def get(self, request):
        status_filter = request.query_params.get("status", Match.Status.ACTIVE)
        matches = MatesService.list_mates(request.user, status=status_filter)
        serializer = self.serializer_class(matches, many=True, context={"request": request})
        return ResponseMessage.success(
            message="Mates retrieved successfully.",
            data=serializer.data,
        )


@extend_schema(tags=["Mates"])
class MateDetailView(APIView):
    """
    DELETE /mates/<id>/  → soft-end match (status = ended, row kept for sessions/reviews)
    Only parties of the match may end it (others get 404).
    No POST, PUT, PATCH allowed.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = MateSerializer

    @extend_schema(summary="End match (soft-delete)")
    def delete(self, request, pk):
        ended_match = MatesService.end_mate(pk, request.user)
        out = self.serializer_class(ended_match, context={"request": request})
        return ResponseMessage.success(
            message="Match ended successfully.",
            data=out.data,
        )
