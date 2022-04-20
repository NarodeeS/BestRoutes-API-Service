from datetime import date
from best_routes.models import TrackedAviaTrip
from .create_tracked_avia_direction import  create_tracked_avia_direction
from best_routes.database import session


def create_tracked_avia_trip(user_id: int, departure_code: str,
                             arrival_code: str, departure_date1: date,
                             departure_date2: date, service_class: str,
                             adult: int, child: int, infant: int,
                             min_cost1: int, min_cost2: int) -> TrackedAviaTrip:
    to_direction = create_tracked_avia_direction(user_id, departure_code, arrival_code,
                                                 departure_date1, service_class,
                                                 adult, child, infant, min_cost1, True)

    back_direction = create_tracked_avia_direction(user_id, arrival_code, departure_code,
                                                   departure_date2, service_class, adult,
                                                   child, infant, min_cost2, True)

    avia_trip = TrackedAviaTrip(user_id=user_id, to_direction_id=to_direction.id,
                                back_direction_id=back_direction.id,
                                trip_min_cost=to_direction.direction_min_cost + back_direction.direction_min_cost)

    session.add(avia_trip)
    session.commit()
    session.rollback()
    return avia_trip
