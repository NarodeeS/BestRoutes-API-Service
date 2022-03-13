from datetime import datetime
from best_routes.transport_utils import Route


class AviaRoute(Route):
    def __init__(self, departure: str, departure_code: str, arrival: str,
                 arrival_code: str, departure_datetime: datetime,
                 arrival_datetime: datetime, duration: int, segments: list,  url: str, source: str) -> None:

        super().__init__(departure, arrival, departure_datetime, arrival_datetime, url)
        self.departure_code = departure_code
        self.arrival_code = arrival_code
        self.duration = duration
        self.segments = segments
        self.source = source

    def __str__(self) -> str:
        return f"Departure: {self.departure}" \
               f"{'('+ self.departure_code + ')' if self.departure_code is not None else ''}\n" \
               f"Arrival: {self.arrival}" \
               f"{'(' + self.arrival_code + ')' if self.arrival_code is not None else ''}\n" \
               f"Departure date: {self.departure_datetime}\n" \
               f"Arrival date: {self.arrival_datetime}\n" \
               f"Duration: {self.duration}\n" \
               f"Source: {self.source}\n" \
               f"URL: {self.url}\n" \
               f"Segments {self.get_segments_info()}\n" \
               f"Places [\n{self.get_places_info()}\n]"

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
            "departureDateTime": str(self.departure_datetime),
            "arrivalDateTime": str(self.arrival_datetime),
            "segments": [segment.to_json() for segment in self.segments],
            "places": [place.to_json() for place in self.places],
            "duration": self.duration,
            "source": self.source,
            "url": self.url,
        }

