from rest_framework.routers import DefaultRouter

from apps.core.api.flight.views import FlightViewSet

router = DefaultRouter()
router.register(r"flights", FlightViewSet, basename="flights")

urlpatterns = router.urls