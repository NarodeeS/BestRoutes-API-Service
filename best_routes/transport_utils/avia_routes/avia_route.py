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
               f"URL: {self.url}\nSegments " + self.get_segments_info() + "Places [\n" \
               + self.get_places_info()+"\n]"

    def get_segments_info(self) -> str:
        result = "[\n"
        for segment in self.segments:
            result += "\t" + str(segment) + "\n"
        result += "\n]\n"
        return result

