from datetime import date
from best_routes.models import TrackedAviaDirection
from best_routes.database import session


def create_tracked_avia_direction(user_id: int, departure_code: str,
                                  arrival_code: str, departure_date: date, service_class: str,
                                  adult: int, child: int, infant: int,
                                  direction_min_cost: int, in_trip: bool) -> TrackedAviaDirection:

    avia_direction = TrackedAviaDirection(user_id=user_id, departure_code=departure_code,
                                          arrival_code=arrival_code, departure_date=departure_date,
                                          service_class=service_class, adult=adult, child=child, infant=infant,
                                          direction_min_cost=direction_min_cost, in_trip=in_trip)
    session.add(avia_direction)
    session.commit()
    session.rollback()
    return avia_direction
