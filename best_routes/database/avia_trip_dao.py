from datetime import date
from .database_operation_wrapper import database_operation_wrapper
from .database import session
from .models import TrackedAviaTrip, TrackedAviaDirection


@database_operation_wrapper
def add_avia_trip(user_id: int, departure_code: str,
                  arrival_code: str, departure_date1: date,
                  departure_date2: date, service_class: str,
                  adult: int, child: int, infant: int,
                  min_cost1: int, min_cost2: int) -> TrackedAviaTrip:

    direction_to = TrackedAviaDirection(user_id=user_id, departure_code=departure_code,
                                        arrival_code=arrival_code, departure_date=departure_date1,
                                        service_class=service_class, adult=adult, child=child, infant=infant,
                                        direction_min_cost=min_cost1, in_trip=True)

    direction_back = TrackedAviaDirection(user_id=user_id, departure_code=arrival_code,
                                          arrival_code=departure_code, departure_date=departure_date2,
                                          service_class=service_class, adult=adult, child=child, infant=infant,
                                          direction_min_cost=min_cost2, in_trip=True)

    session.add(direction_to)

    session.add(direction_back)

    avia_trip = TrackedAviaTrip(user_id=user_id, to_direction_id=direction_to.id,
                                back_direction_id=direction_back.id,
                                trip_min_cost=direction_to.direction_min_cost + direction_back.direction_min_cost)

    session.add(avia_trip)
    return avia_trip
