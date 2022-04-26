from datetime import datetime
from best_routes.transport_utils.place import Place
from best_routes.transport_utils.base_route import BaseRoute


class Route(BaseRoute):
    def __init__(self, departure: str, arrival: str,
                 departure_datetime: datetime, arrival_datetime: datetime,
                 url: str) -> None:

        super().__init__(departure, arrival, departure_datetime, arrival_datetime)
        self.url = url
        self.places = []

    def __lt__(self, other) -> bool:
        if isinstance(other, Route):
            if self.get_cheapest_place().min_price < other.get_cheapest_place().min_price:
                return True
            return False

    def get_cheapest_place(self) -> Place:
        if len(self.places) == 0:
            return
        min_place = self.places[0]
        for place in self.places:
            if place.min_price < min_place.min_price:
                min_place = place
        
        return min_place

    def get_places_info(self) -> str:
        result = ""
        for place in self.places:
            result += "\t" + place.__str__() + "\n"
        
        return result
