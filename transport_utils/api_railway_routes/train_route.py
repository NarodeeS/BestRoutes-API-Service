from datetime import datetime
from transport_utils.route import Route


class TrainRoute(Route):
    def __init__(self, departure: str,
                 arrival: str, train_number: int,
                 departure_datetime: datetime, arrival_datetime: datetime, url: str) -> None:

        super().__init__(departure, arrival, departure_datetime, arrival_datetime, url)
        self.train_number = train_number

    def __str__(self) -> str:
        return f"From: {self.departure}\n" \
               f"To: {self.arrival}\n" \
               f"Train: {self.train_number}\n" \
               f"Departure date: {self.departure_datetime}\n" \
               f"Arrival date: {self.arrival_datetime}\n" \
               f"URL: {self.url}\n" \
               "Places: {\n" + self.get_places_info() + "\n}"
