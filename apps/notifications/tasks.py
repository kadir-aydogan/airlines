from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone

@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=5)
def send_reservation_email_task(self, *, passenger_email: str, passenger_name: str,
                                flight_id: int, departure: str, departure_time: str):
    subject = f"Reservation Confirmed (#{flight_id})"
    body = (
        f"Hello {passenger_name},\n\n"
        f"Your reservation for flight #{flight_id} is confirmed.\n"
        f"Departure: {departure} at {departure_time}\n\n"
        f"Have a nice trip!"
    )
    send_mail(subject, body, None, [passenger_email], fail_silently=False)
    return "sent"


