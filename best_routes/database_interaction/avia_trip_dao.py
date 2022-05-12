from datetime import date
from langdetect import detect
from .models import TrackedAviaTrip, TrackedAviaDirection
from .util_functions import check_station_existence
from .database import db_session


def add_avia_trip(user_id: int, departure_code: str,
                  arrival_code: str, departure_date1: date,
                  departure_date2: date, service_class: str,
                  adult: int, child: int, infant: int,
                  min_cost1: int, min_cost2: int) -> TrackedAviaTrip:

    if departure_date1 < date.today() or departure_date1 > departure_date2 \
            or departure_date1 == departure_date2:
        raise ValueError()
    if not check_station_existence(departure_code, "from") \
            or not check_station_existence(arrival_code, "to"):
        raise ValueError()
    if len(service_class) > 1:
        raise ValueError()
    if service_class == "Y" or (service_class == "C" and detect(service_class) == "en"):
        direction_to = TrackedAviaDirection(user_id=user_id, departure_code=departure_code,
                                            arrival_code=arrival_code, departure_date=departure_date1,
                                            service_class=service_class, adult=adult, child=child, infant=infant,
                                            direction_min_cost=min_cost1, in_trip=True)

        direction_back = TrackedAviaDirection(user_id=user_id, departure_code=arrival_code,
                                              arrival_code=departure_code, departure_date=departure_date2,
                                              service_class=service_class, adult=adult, child=child, infant=infant,
                                              direction_min_cost=min_cost2, in_trip=True)

        db_session.add(direction_to)
        db_session.commit()
        db_session.add(direction_back)
        db_session.commit()
        avia_trip = TrackedAviaTrip(user_id=user_id, to_direction_id=direction_to.id,
                                    back_direction_id=direction_back.id,
                                    trip_min_cost=direction_to.direction_min_cost + direction_back.direction_min_cost)

        db_session.add(avia_trip)
        db_session.commit()
        return avia_trip
    raise ValueError()


def update_avia_trip_cost(trip_id: int, new_cost: int) -> None:
    trip = db_session.query(TrackedAviaTrip).filter(TrackedAviaTrip.id == trip_id).first()
    trip.trip_min_cost = new_cost
    db_session.commit()


def delete_avia_trip(trip_id: int):
    avia_trip = db_session.query(TrackedAviaTrip) \
        .filter(TrackedAviaTrip.id == trip_id).first()
    db_session.delete(avia_trip)
    db_session.commit()


def get_trips_by_user_id(user_id: int) -> list:
    return db_session.query(TrackedAviaTrip).filter(TrackedAviaTrip.user_id == user_id)
