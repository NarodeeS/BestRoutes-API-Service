from enum import Enum
from datetime import date
from .tuturu import get_request_to_tuturu, get_city_id, get_routes_from_tuturu
from .kupibilet import get_request_to_kupibilet, get_routes_from_kupibilet
from best_routes.exceptions import NoSuchRoutesException


def get_all_services() -> list:
    return [AviaService.TUTU,
            AviaService.KUPIBILET]


def prepare_content_routes(content: dict) -> dict:
    departure_date = date.fromisoformat(content["departureDate"])
    if departure_date < date.today():
        raise NoSuchRoutesException(101, "you entered an already expired date")

    return {
        "departure_code": content["departureCode"],
        "arrival_code": content["arrivalCode"],
        "departure_date": departure_date,
        "adult": content["adult"],
        "child": content["child"],
        "infant": content["infant"],
        "service_class": content["serviceClass"],
    }


class AviaService(Enum):
    TUTU = 1
    KUPIBILET = 2

    def get_request_object(self, content: dict) -> dict:
        if self.name == AviaService.TUTU.name:
            departure_city_id = get_city_id(content["departureCode"], "from")
            arrival_city_id = get_city_id(content["arrivalCode"], "to")
            return {
                "request": get_request_to_tuturu(**prepare_content_routes(content)),
                "callback": get_routes_from_tuturu,
                "additionalInfo": {
                    "departureId": departure_city_id,
                    "arrivalId": arrival_city_id
                }
            }
        elif self.name == AviaService.KUPIBILET.name:
            return {
                "request": get_request_to_kupibilet(**prepare_content_routes(content)),
                "callback": get_routes_from_kupibilet,
                "additionalInfo": {}
            }
