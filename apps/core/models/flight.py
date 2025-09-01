from django.db import models
from django.core.exceptions import ValidationError

from .airplane import Airplane

class Flight(models.Model):
    id = models.BigAutoField(primary_key=True)
    flight_number = models.CharField(unique=True, null=False, blank=False, db_index=True, max_length=20)
    departure = models.CharField(max_length = 20, null = False, blank = False, unique = False)
    destination = models.CharField(max_length = 20, null = False, blank = False, unique = False)
    departure_time = models.DateTimeField(null = False, blank = False, unique = False)
    arrival_time = models.DateTimeField(null = False, blank = False, unique = False)
    airplane = models.ForeignKey(Airplane, null = False, blank = False, on_delete=models.PROTECT)
    deleted = models.BooleanField(null = False, blank = False, default = False)

    class Meta:
        ordering = ['departure_time']
        indexes = [models.Index(fields=['flight_number']), ]

    def clean(self):
        if self.arrival_time <= self.departure_time:
            raise ValidationError({"arrival_time": "Arrival must be after departure."})

        if self.destination.strip().upper() == self.departure.strip().upper():
            raise ValidationError({"destination": "Destination must differ from departure."})


