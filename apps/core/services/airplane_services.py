from dataclasses import dataclass, asdict
from typing import Optional

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.core.models import Airplane
from apps.core.selectors.flight_selector import list_flights


@dataclass(frozen=True)
class AirplaneCreateInput:
    tail_number     : str
    model           : str
    capacity        : int
    production_year : int
    status          : bool = True
@transaction.atomic
def create_airplane(inp: AirplaneCreateInput):

    tail = (inp.tail_number or "").strip().upper()

    airplane = Airplane(
        tail_number=tail,
        model=inp.model,
        capacity=inp.capacity,
        production_year=inp.production_year,
        status=inp.status,
    )

    airplane.full_clean()
    airplane.save()

    return airplane

@dataclass(frozen=True)
class AirplaneUpdateInput:
    tail_number : Optional[str] = None
    model : Optional[str] = None
    capacity : Optional[int] = None
    production_year : Optional[int] = None
    status : bool = True


@transaction.atomic
def update_airplane(airplane: Airplane, inp: AirplaneUpdateInput):
    changes = {k: v for k, v in asdict(inp).items() if v is not None}
    if not changes:
        return airplane
    for field, value in changes.items():
        setattr(airplane, field, value)

    active_flights = list_flights(airplane_id=airplane.id).filter().count()

    if active_flights > airplane.capacity:
        raise ValidationError({"capacity": "There are %s active flights."})

    airplane.full_clean()

    airplane.save(update_fields=list(changes.keys()))
    return airplane


def has_active_flights_now(airplane):

    now = timezone.now()

    return list_flights(airplane_id=airplane.id, arrival_time_min=now).exists()


@transaction.atomic
def soft_delete_airplane(airplane: Airplane):

    has_active_flights = has_active_flights_now(airplane)

    if has_active_flights:
        raise ValidationError({"airplane": "There are active flights with airplane."})

    airplane.status = False
    airplane.deleted = False

    airplane.save()









