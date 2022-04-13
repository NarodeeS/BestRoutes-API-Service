from datetime import datetime
from best_routes.transport_utils import Route


class TrainRoute(Route):
    def __init__(self, departure: str,
                 arrival: str, train_number: int, has_electronic_registration: bool,
                 departure_datetime: datetime, arrival_datetime: datetime, url: str) -> None:

        super().__init__(departure, arrival, departure_datetime, arrival_datetime, url)
        self.has_electronic_registration = has_electronic_registration
        self.train_number = train_number

    def to_json(self) -> dict:
        return {
            "departure": self.departure,
            "arrival": self.arrival,
            "trainNumber": self.train_number,
            "hasElectronicRegistration": self.has_electronic_registration,
            "departureDatetime": self.departure_datetime.isoformat(),
            "arrivalDatetime": self.arrival_datetime.isoformat(),
            "url": self.url,
            "places": [place.to_json() for place in self.places]
        }