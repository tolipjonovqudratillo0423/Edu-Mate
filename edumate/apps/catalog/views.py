from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

from apps.catalog.models import Track
from apps.common.utils import ResponseMessage


@extend_schema(tags=["Catalog"])
class TrackListView(APIView):
    """
    GET /catalog/tracks/  → list available tracks for goals and partner matching
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tracks = list(Track.objects.all().values("id", "slug", "name", "category"))
        return ResponseMessage.success(
            message="Tracks retrieved successfully.",
            data=tracks,
        )
