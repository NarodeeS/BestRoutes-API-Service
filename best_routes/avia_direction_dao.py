from datetime import date
from best_routes.models import TrackedAviaDirection
from best_routes import db


def add_avia_direction(user_id: int, departure_code: str,
                       arrival_code: str, departure_date: date, service_class: str,
                       adult: int, child: int, infant: int,
                       direction_min_cost: int, in_trip: bool) -> TrackedAviaDirection:

    avia_direction = TrackedAviaDirection(user_id=user_id, departure_code=departure_code,
                                          arrival_code=arrival_code, departure_date=departure_date,
                                          service_class=service_class, adult=adult, child=child, infant=infant,
                                          direction_min_cost=direction_min_cost, in_trip=in_trip)
    db.session.add(avia_direction)
    db.session.commit()
    return avia_direction


def delete_avia_direction(direction_id: int):
    avia_direction = TrackedAviaDirection.query.filter_by(id=direction_id).first()
    db.session.delete(avia_direction)
    db.session.commit()


def update_avia_direction_cost(direction_id: int, new_cost: int) -> None:
    avia_direction = TrackedAviaDirection.query.filter_by(id=direction_id).first()
    avia_direction.direction_min_cost = new_cost
    db.session.commit()


def get_directions_by_user_id(user_id: int) -> list:
    return TrackedAviaDirection.query.filter_by(user_id=user_id)




