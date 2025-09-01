from django.db import models
import uuid
from django.core.exceptions import ValidationError

from .flight import Flight

def generate_reservation_code() -> str:
    # sonradan, db seq'ten çekeriz.
    return uuid.uuid4().hex[:8].upper()


class Reservation(models.Model):
    id = models.BigAutoField(primary_key=True, editable=False)
    reservation_code = models.CharField(unique=True, null=False, blank=False, db_index=True, max_length=40, default=generate_reservation_code)
    passenger_name = models.CharField(unique=False, null=False, blank=False, db_index=True, max_length=40)
    passenger_email = models.CharField(unique=False, null=False, blank=False, db_index=True, max_length=40)
    flight = models.ForeignKey(Flight, null = False, blank = False, on_delete=models.PROTECT)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(editable=False, auto_now_add=True)
    deleted = models.BooleanField(default=False, null=False, blank=False)
