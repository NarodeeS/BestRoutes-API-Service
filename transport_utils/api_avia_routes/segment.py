from datetime import datetime
from transport_utils.base_route import BaseRoute


class Segment(BaseRoute):
    """Describe a part of an air travel, that is.
    It is necessary if a transfer occurs during the flight """
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

    def __str__(self) -> str:
        return f"Departure: {self.departure}; " \
               f"Arrival: {self.arrival}; " \
               f"Departure date: {self.departure_datetime}; " \
               f"Arrival date: {self.arrival_datetime}; " \
               f"Duration: {self.duration_in_minutes} minutes; " \
               f"Airline: {self.airline}' " \
               f"Plane: {self.plane}"
