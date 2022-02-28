from datetime import datetime, time
from api_routes.base_route import BaseRoute


class Segment(BaseRoute):
    """Describe a part of an air travel, that is.
    It is necessary if a transfer occurs during the flight """
    def __init__(self, departure: str, departure_code: str, arrival: str,
                 arrival_code: str, departure_datetime: datetime,
                 arrival_datetime: datetime, duration: time, plane: str) -> None:

        super().__init__(departure, arrival, departure_datetime, arrival_datetime)
        self.departure_code = departure_code
        self.arrival_code = arrival_code
        self.duration = duration
        self.plane = plane

    def __str__(self) -> str:
        return f"Departure: {self.departure}; " \
               f"Arrival: {self.arrival}; " \
               f"Departure date: {self.departure_datetime}; " \
               f"Arrival date: {self.arrival_datetime}; " \
               f"Duration: {self.duration}; Plane: {self.plane}"
