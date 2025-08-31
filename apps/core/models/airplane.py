from django.core.exceptions import ValidationError
from django.db import models

class Airplane(models.Model):
    id = models.BigAutoField(primary_key=True)
    tail_number = models.CharField(unique=True, null=False, blank=False, max_length=20)
    model = models.CharField(max_length = 20, null = False, blank = False, unique = False)
    capacity = models.PositiveIntegerField(null = False, blank = False, unique = False)
    production_year = models.PositiveIntegerField(null = False, blank = False, unique = False)
    status = models.BooleanField(default=True)
    deleted = models.BooleanField(default=False, null = False, blank = False)

    class Meta:
        indexes = [
            models.Index(fields=['tail_number']),
            models.Index(fields=['model']),
        ]
        ordering = ['tail_number']

    def __str__(self):
        return f"{self.tail_number} ({self.model})"

    def clean(self):
        import datetime
        if self.production_year < 1950 or self.production_year > datetime.date.today().year:
            raise ValidationError({"production_year": "Invalid production year range"})
