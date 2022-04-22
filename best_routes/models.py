from best_routes import db


class User(db.Model):
    id = db.Column(db.Integer, unique=True, primary_key=True, nullable=False, autoincrement=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    telegram_id = db.Column(db.String(255), default=None)
    is_developer = db.Column(db.Boolean, nullable=False)
    tokens = db.relationship("Token", cascade="all")
    tracked_avia_directions = db.relationship("TrackedAviaDirection", cascade="all")
    tracked_avia_trips = db.relationship("TrackedAviaTrip", cascade="all")
    services = db.relationship("Service", cascade="all")


class Token(db.Model):
    value = db.Column(db.String(255), nullable=False, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, primary_key=True)


class TrackedAviaDirection(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    departure_code = db.Column(db.String(3), nullable=False)
    arrival_code = db.Column(db.String(3), nullable=False)
    departure_date = db.Column(db.Date, nullable=False)
    service_class = db.Column(db.String(1), nullable=False)
    adult = db.Column(db.Integer, nullable=False)
    child = db.Column(db.Integer, nullable=False)
    infant = db.Column(db.Integer, nullable=False)
    direction_min_cost = db.Column(db.Integer, nullable=False)
    in_trip = db.Column(db.Boolean, nullable=False)

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


class TrackedAviaTrip(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    to_direction_id = db.Column(db.Integer, db.ForeignKey("tracked_avia_direction.id"), nullable=False)
    back_direction_id = db.Column(db.Integer, db.ForeignKey("tracked_avia_direction.id"), nullable=False)
    trip_min_cost = db.Column(db.Integer, nullable=False)

    direction_to = db.relationship("TrackedAviaDirection", foreign_keys=[to_direction_id])
    direction_back = db.relationship("TrackedAviaDirection", foreign_keys=[back_direction_id])

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


class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    developer_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False)
