from datetime import datetime
from best_routes.transport_utils import Route


class AviaRoute(Route):
    def __init__(self, departure: str, departure_code: str, arrival: str,
                 arrival_code: str, departure_datetime: datetime,
                 arrival_datetime: datetime, duration: int, segments: list, places: list, url: str, source: str) -> None:

        super().__init__(departure, arrival, departure_datetime, arrival_datetime, url)
        self.departure_code = departure_code
        self.arrival_code = arrival_code
        self.duration = duration
        self.segments = segments
        self.places = places
        self.source = source

    def __eq__(self, other):
        if isinstance(other, AviaRoute):
            if self.departure_datetime == other.departure_datetime:
                for i in range(min(len(self.segments), len(other.segments))):
                    if self.segments[i].departure_datetime != other.segments[i].departure_datetime and \
                            self.segments[i].plane == other.segments[i].plane:
                        return False
                return True
        return False

    def get_segments_info(self) -> str:
        result = "[\n"
        for segment in self.segments:
            result += "\t" + str(segment) + "\n"
        result += "\n]\n"
        return result

    def to_json(self) -> dict:
        return {
            "departure": self.departure,
            "departureCode": self.departure_code,
            "arrival": self.arrival,
            "arrivalCode": self.arrival_code,
            "departureDateTime": self.departure_datetime.isoformat(),
            "arrivalDateTime": self.arrival_datetime.isoformat(),
            "segments": [segment.to_json() for segment in self.segments],
            "places": [place.to_json() for place in self.places],
            "minPrice": self.get_cheapest_place().min_price,
            "duration": self.duration,
            "source": self.source,
            "url": self.url,
        }
