from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date
from sqlalchemy.orm import relationship
from .database import Base, engine


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, unique=True, primary_key=True, nullable=False, autoincrement=True)
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    is_developer = Column(Boolean, nullable=False)
    tokens = relationship("Token", cascade="all")
    tracked_avia_directions = relationship("TrackedAviaDirection", cascade="all")
    tracked_avia_trips = relationship("TrackedAviaTrip", cascade="all")
    services = relationship("Service", cascade="all")


class Token(Base):
    __tablename__ = "token"
    value = Column(String(255), nullable=False, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, primary_key=True)


class TrackedAviaDirection(Base):
    __tablename__ = "tracked_avia_direction"
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    departure_code = Column(String(3), nullable=False)
    departure = Column(String(255), nullable=False)
    arrival_code = Column(String(3), nullable=False)
    arrival = Column(String(255), nullable=False)
    departure_date = Column(Date, nullable=False)
    service_class = Column(String(1), nullable=False)
    adult = Column(Integer, nullable=False)
    child = Column(Integer, nullable=False)
    infant = Column(Integer, nullable=False)
    direction_min_cost = Column(Integer, nullable=False)
    in_trip = Column(Boolean, nullable=False)

    def to_request_form(self) -> dict:
        return {
            "departureCode": self.departure_code,
            "arrivalCode": self.arrival_code,
            "departureDate": str(self.departure_date),
            "adult": self.adult,
            "child": self.child,
            "infant": self.infant,
            "serviceClass": self.service_class,
            "count": -1
        }

    def to_json(self) -> dict:
        base = self.to_request_form()
        base.pop("count")
        base["departure"] = self.departure
        base["arrival"] = self.arrival
        base["id"] = self.id
        base["directionMinCost"] = self.direction_min_cost
        return base


class TrackedAviaTrip(Base):
    __tablename__ = "tracked_avia_trip"
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    to_direction_id = Column(Integer, ForeignKey("tracked_avia_direction.id"), nullable=False)
    back_direction_id = Column(Integer, ForeignKey("tracked_avia_direction.id"), nullable=False)
    trip_min_cost = Column(Integer, nullable=False)

    direction_to = relationship("TrackedAviaDirection", foreign_keys=[to_direction_id], cascade="all,delete")
    direction_back = relationship("TrackedAviaDirection", foreign_keys=[back_direction_id], cascade="all,delete")

    def to_request_form(self) -> dict:
        return {
            "departureCode": self.direction_to.departure_code,
            "arrivalCode": self.direction_to.arrival_code,
            "departureDate1": str(self.direction_to.departure_date),
            "departureDate2": str(self.direction_back.departure_date),
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
    __tablename__ = "service"
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String(255), nullable=False)
    developer_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    url = Column(String(255), nullable=False)
    is_active = Column(Boolean, nullable=False)


Base.metadata.create_all(bind=engine)

