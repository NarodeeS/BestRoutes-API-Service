from .database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Date
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"

    id = Column(Integer(), primary_key=True, nullable=False, autoincrement=True)
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    telegram_id = Column(String(255), default=None)
    is_developer = Column(Boolean(), nullable=False)
    tokens = relationship("Token", cascade="all")
    tracked_avia_directions = relationship("TrackedAviaDirection", cascade="all")
    tracked_avia_trips = relationship("TrackedAviaTrip", cascade="all")
    services = relationship("Service", cascade="all")


class Token(Base):
    __tablename__ = "tokens"

    value = Column(String(), nullable=False, primary_key=True)
    user_id = Column(Integer(), ForeignKey(User.id), nullable=False, primary_key=True)


class TrackedAviaDirection(Base):
    __tablename__ = "tracked_avia_directions"

    id = Column(Integer(), primary_key=True, nullable=False, autoincrement=True)
    user_id = Column(Integer(), ForeignKey(User.id), nullable=False)
    departure_code = Column(String(3), nullable=False)
    arrival_code = Column(String(3), nullable=False)
    departure_date = Column(Date, nullable=False)
    service_class = Column(String(1), nullable=False)
    adult = Column(Integer(), nullable=False)
    child = Column(Integer(), nullable=False)
    infant = Column(Integer(), nullable=False)
    direction_min_cost = Column(Integer(), nullable=False)
    in_trip = Column(Boolean(), nullable=False)

    def to_request_form(self) -> dict:
        return {
            "departureCode": self.departure_code,
            "arrivalCode": self.arrival_code,
            "departureDate": self.departure_date,
            "adult": self.adult,
            "child": self.child,
            "infant": self.infant,
            "serviceClass": self.service_class,
            "count": -1
        }

    def to_json(self):
        base = self.to_request_form()
        base.pop("count")
        base["id"] = self.id
        base["directionMinCost"] = self.direction_min_cost
        return base


class TrackedAviaTrip(Base):
    __tablename__ = "tracked_avia_trips"

    id = Column(Integer(), primary_key=True, nullable=False, autoincrement=True)
    user_id = Column(Integer(), ForeignKey(User.id), nullable=False)
    to_direction_id = Column(Integer(), ForeignKey(TrackedAviaDirection.id), nullable=False)
    back_direction_id = Column(Integer(), ForeignKey(TrackedAviaDirection.id), nullable=False)
    trip_min_cost = Column(Integer(), nullable=False)

    direction_to = relationship("TrackedAviaDirection", foreign_keys=[to_direction_id])
    direction_back = relationship("TrackedAviaDirection", foreign_keys=[back_direction_id])

    def to_request_form(self) -> dict:
        return {
            "departureCode": self.direction_to.departure_code,
            "arrivalCode": self.direction_to.arrival_code,
            "departureDate1": self.direction_to.departure_date,
            "departureDate2": self.direction_back.departure_date,
            "adult": self.direction_to.adult,
            "child": self.direction_to.child,
            "infant": self.direction_to.infant,
            "serviceClass": self.direction_to.service_class,
            "count": -1
        }

    def to_json(self) -> dict:
        return {
            "to": self.direction_to.to_json(),
            "back": self.direction_back.to_json(),
            "tripMinCost": self.trip_min_cost,
            "id": self.id
        }


class Service(Base):
    __tablename__ = "services"

    id = Column(Integer(), primary_key=True, nullable=False, autoincrement=True)
    name = Column(String(255), nullable=False)
    developer_id = Column(Integer(), ForeignKey(User.id), nullable=False)
    url = Column(String(255), nullable=False)
    is_active = Column(Boolean(), nullable=False)
