from django.contrib import admin

from django.contrib import admin
from .models import Airplane, Flight, Reservation

@admin.register(Airplane)
class AirplaneAdmin(admin.ModelAdmin):
    list_display  = ("id", "tail_number", "model", "capacity", "production_year", "status")
    search_fields = ("tail_number", "model")
    list_filter   = ("status", "production_year")
    ordering      = ("tail_number",)

@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display  = ("id", "flight_number", "departure", "destination",
                        "departure_time", "arrival_time", "airplane")
    search_fields = ("flight_number", "departure", "destination", "airplane__tail_number")
    list_filter   = ("departure", "destination", "airplane")
    ordering      = ("-departure_time",)