from datetime import date
from best_routes.models import TrackedAviaTrip, TrackedAviaDirection
from best_routes import db


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

    db.session.add(direction_to)

    db.session.add(direction_back)

    avia_trip = TrackedAviaTrip(user_id=user_id, to_direction_id=direction_to.id,
                                back_direction_id=direction_back.id,
                                trip_min_cost=direction_to.direction_min_cost + direction_back.direction_min_cost)

    db.session.add(avia_trip)
    db.session.commit()
    return avia_trip


def update_avia_trip_cost(trip_id: int, new_cost: int) -> None:
    trip = TrackedAviaTrip.query.filter_by(id=trip_id).first()
    trip.trip_min_cost = new_cost
    db.session.commit()


def get_trips_by_user_id(user_id: int) -> list:
    return TrackedAviaTrip.query.filter_by(user_id=user_id)
