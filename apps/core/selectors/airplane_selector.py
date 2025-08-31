from typing import Optional

from django.db.models import QuerySet, Q

from apps.core.models import Airplane

def list_airplanes(
        *,
        airplane_id: Optional[int] = None,
        tail_number: Optional[str] = None,
        model: Optional[str] = None,
        min_capacity: Optional[int] = None,
        max_capacity: Optional[int] = None,
        status: Optional[bool] = True,
        deleted: Optional[bool] = False,
) -> QuerySet[Airplane]:

    qs = Airplane.objects.all()

    if airplane_id is not None:
        qs = qs.filter(id=airplane_id)

    if tail_number:
        qs = qs.filter(tail_number=tail_number)

    if model:
        qs = qs.filter(model=model)

    if min_capacity is not None:
        qs = qs.filter(capacity__gte=min_capacity)

    if max_capacity is not None:
        qs = qs.filter(capacity__lte=max_capacity)

    if status is not None:
        qs = qs.filter(status=status)

    if deleted is not None:
        qs = qs.filter(deleted=deleted)

    return qs


