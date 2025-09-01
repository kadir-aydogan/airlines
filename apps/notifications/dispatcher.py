from django.db import transaction
from apps.notifications.tasks import send_reservation_email_task

ROUTES = {
    "reservation.booked": [
        lambda payload: send_reservation_email_task.delay(**payload),
        ## ileride sms vs. de atarız.
    ],
}

def publish_event(event_type: str, payload: dict) -> None:

    if event_type not in ROUTES:
        return

    def _fan_out():
        for handler in ROUTES[event_type]:
            handler(payload)

    transaction.on_commit(_fan_out)
