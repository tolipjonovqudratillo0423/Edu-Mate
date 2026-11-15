from django.urls import path

from apps.matching.views import PartnersView

urlpatterns = [
    path("partners/", PartnersView.as_view(), name="partners"),
]
