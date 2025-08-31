from dataclasses import dataclass, asdict
from datetime import timedelta

from rest_framework.exceptions import ValidationError

from apps.core.models import Flight
from django.utils import timezone
from apps.core.models import Airplane
from apps.core.selectors.flight_selector import list_flights
from apps.core.selectors.reservation_selector import list_reservations

BUFFER = timedelta(hours=1)


@dataclass(frozen=True)
class FlightCreateInput:
    flight_number: str
    departure: str
    destination: str
    departure_time: timezone.datetime
    arrival_time: timezone.datetime
    airplane_id: int


def check_conflict(airplane_id: int, departure_time, arrival_time) -> bool:
    dep_minus = departure_time - BUFFER
    arr_plus = arrival_time + BUFFER

    return Flight.objects.filter(
        airplane_id=airplane_id,
        departure_time__lt=arr_plus,
        arrival_time__gt=dep_minus,
    ).exists()

def check_conflict_with_existing_flight(airplane_id: int, departure_time, arrival_time, flight_id) -> bool:
    dep_minus = departure_time - BUFFER
    arr_plus = arrival_time + BUFFER

    return (Flight.objects.filter(
            airplane_id=airplane_id,
            departure_time__lt=arr_plus,
            arrival_time__gt=dep_minus,)
        .exclude(id=flight_id)
        .exists())


def create_flight(inp: FlightCreateInput) -> Flight:
    try:
        airplane = Airplane.objects.get(pk=inp.airplane_id, deleted=False, status=True)
    except Airplane.DoesNotExist:
        raise ValidationError(f"Airplane {inp.airplane_id} does not exist or active.")

    if check_conflict(airplane.id, inp.departure_time, inp.arrival_time):
        raise ValidationError({"airplane_id": "This airplane has another flight within ±1h window."})

    flight = Flight(
        airplane=airplane,
        flight_number=inp.flight_number,
        departure=inp.departure,
        destination=inp.destination,
        departure_time=inp.departure_time,
        arrival_time=inp.arrival_time,
    )

    flight.full_clean()
    flight.save()

    return flight

@dataclass(frozen=True)
class FlightUpdateInput:
    flight_number: str
    departure: str
    destination: str
    departure_time: timezone.datetime
    arrival_time: timezone.datetime
    airplane_id: int

def update_flight(flight: Flight, inp: FlightUpdateInput) -> Flight:
    
    changes = {k: v for k, v in asdict(inp).items() if v is not None}
    
    if not changes:
        return flight
    for field, value in changes.items():
        setattr(flight, field, value)

    try:
        airplane = Airplane.objects.get(pk=inp.airplane_id, deleted=False)
    except Airplane.DoesNotExist:
        raise ValidationError(f"Airplane {inp.airplane_id} does not exist")

    has_conflict = check_conflict_with_existing_flight(airplane.id, flight.departure_time, flight.arrival_time, flight.id)

    if has_conflict:
        raise ValidationError({"airplane_id": "This airplane has another flight within ±1h window."})

    flight.full_clean()

    flight.save(update_fields=list(changes.keys()))

    return flight

def check_if_flight_is_passed(flight_id: int) -> bool:
    now = timezone.now()
    return Flight.objects.filter(pk=flight_id, arrival_time__lte=now).exists()

def check_if_there_active_reservations(flight_id: int) -> bool:
    return list_reservations(flight_id=flight_id).exists()

def soft_delete_flight(flight: Flight):

    # uçuş bitti ise, silinebilir
    # uçuş bitmedi ancak, reservasyon yoska silinebilir.

    passed = check_if_flight_is_passed(flight.id)

    if not passed and check_if_there_active_reservations(flight.id):
        raise ValidationError("This flight has active reservations.")

    if not flight.deleted:
        flight.deleted = True
        flight.save()



