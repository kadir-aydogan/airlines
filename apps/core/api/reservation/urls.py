from rest_framework.routers import DefaultRouter

from apps.core.api.reservation.views import ReservationViewSet

router = DefaultRouter()
router.register(r"reservations", ReservationViewSet, basename="reservation")
urlpatterns = router.urls