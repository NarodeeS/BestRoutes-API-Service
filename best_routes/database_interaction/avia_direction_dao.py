from langdetect import detect
from datetime import date
from .models import TrackedAviaDirection
from .util_functions import check_station_existence
from .database import db_session


def add_avia_direction(user_id: int, departure_code: str,
                       arrival_code: str, departure_date: date, service_class: str,
                       adult: int, child: int, infant: int,
                       direction_min_cost: int) -> TrackedAviaDirection:
    if departure_date < date.today():
        raise ValueError()
    if not check_station_existence(departure_code, "from") \
            or not check_station_existence(arrival_code, "to"):
        raise ValueError()

    if len(service_class) > 1:
        raise ValueError()
    if service_class == "Y" or (service_class == "C" and detect(service_class) == "en"):
        avia_direction = TrackedAviaDirection(user_id=user_id, departure_code=departure_code,
                                              arrival_code=arrival_code, departure_date=departure_date,
                                              service_class=service_class, adult=adult, child=child, infant=infant,
                                              direction_min_cost=direction_min_cost, in_trip=False)
        db_session.add(avia_direction)
        db_session.commit()
        return avia_direction
    raise ValueError()


def delete_avia_direction(direction_id: int) -> None:
    avia_direction = db_session.query(TrackedAviaDirection) \
        .filter(TrackedAviaDirection.id == direction_id).first()
    db_session.delete(avia_direction)
    db_session.commit()


def update_avia_direction_cost(direction_id: int, new_cost: int) -> None:
    avia_direction = db_session.query(TrackedAviaDirection) \
        .filter(TrackedAviaDirection.id == direction_id).first()
    avia_direction.direction_min_cost = new_cost
    db_session.commit()


def get_directions_by_user_id(user_id: int) -> list:
    directions = db_session.query(TrackedAviaDirection).filter(TrackedAviaDirection.user_id == user_id)
    return directions
