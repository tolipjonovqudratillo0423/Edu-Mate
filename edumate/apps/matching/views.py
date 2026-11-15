from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from drf_spectacular.utils import extend_schema, OpenApiParameter

from apps.matching.serializers import PartnerSerializer
from apps.matching.services import PartnersService
from apps.common.utils import ResponseMessage


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
            data=serializer.data,
        )
