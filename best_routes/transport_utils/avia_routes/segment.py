from datetime import datetime
from best_routes.transport_utils import BaseRoute


class Segment(BaseRoute):
    def __init__(self, departure: str, departure_code: str, arrival: str,
                 arrival_code: str, departure_datetime: datetime,
                 arrival_datetime: datetime, duration_in_minutes: int,
                 airline: str,  plane: str) -> None:

        super().__init__(departure, arrival, departure_datetime, arrival_datetime)
        self.departure_code = departure_code
        self.arrival_code = arrival_code
        self.duration_in_minutes = duration_in_minutes
        self.airline = airline
        self.plane = plane

    def to_json(self) -> dict:
        return {
            "departure": self.departure,
            "departureCode": self.departure_code,
            "arrival": self.arrival,
            "arrivalCode": self.arrival_code,
            "departureDateTime": self.departure_datetime.isoformat(),
            "arrivalDateTime": self.arrival_datetime.isoformat(),
            "duration": self.duration_in_minutes,
            "airline": self.airline,
            "plane": self.plane
        }

