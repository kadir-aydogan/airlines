from rest_framework.routers import DefaultRouter

from apps.core.api.airplanes.views import AirplaneViewSet

router = DefaultRouter()
router.register(r"airplane", AirplaneViewSet, basename="airplane")

urlpatterns = router.urls