from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone

@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=5)
def send_reservation_email_task(self, reservation_id: int):
    # import'u fonksiyon içinde tut: circular dependency'yi önler
    from apps.core.models import Reservation

    res = Reservation.objects.select_related("flight").get(pk=reservation_id)

    subject = f"Reservation Confirmed #{res.id}"
    body = (
        f"Hello {res.passenger_name},\n"
        f"Your reservation for flight {res.flight.id} is confirmed.\n"
        f"Departure: {res.flight.departure} at {res.flight.departure_time}\n"
    )

    send_mail(subject, body, None, [res.passenger_email], fail_silently=False)

