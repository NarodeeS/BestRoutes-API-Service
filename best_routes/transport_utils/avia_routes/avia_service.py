from enum import Enum
from datetime import date
from .tuturu import get_request_to_tuturu, get_routes_from_tuturu
from .kupibilet import get_request_to_kupibilet, get_routes_from_kupibilet
from .onetwotrip import get_request_to_onetwotrip, get_routes_from_onetwotrip
from best_routes.utils import logger
from best_routes.utils import Log
from best_routes.exceptions import NoSuchRoutesException, NoSuchCityException
from best_routes.database_interaction import get_city_id


def get_all_services() -> list:
    return [AviaService.TUTU,
            AviaService.KUPIBILET, AviaService.ONE_TWO_TRIP]


def prepare_content_routes(content: dict) -> dict:
    departure_date = date.fromisoformat(content["departureDate"])
    if departure_date < date.today():
        raise NoSuchRoutesException(message="you entered an already expired date")

    if int(content["adult"]) < 0 or int(content["child"]) < 0 or int(content["infant"]) < 0:
        raise KeyError()

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
    ONE_TWO_TRIP = 3

    def get_request_object(self, content: dict) -> dict:
        if self.name == AviaService.TUTU.name:
            departure_city_id = None
            arrival_city_id = None
            try:
                departure_city_id = get_city_id(content["departureCode"], "from")
                arrival_city_id = get_city_id(content["arrivalCode"], "to")
            except NoSuchCityException as e:
                logger.add_log(Log("NoSuchAirportException", f"Code: {e.city_code}",
                                   "get_request_object", "avia_service.py"))
            return {
                "request": get_request_to_tuturu(**prepare_content_routes(content)),
                "callback": get_routes_from_tuturu,
                "additionalInfo": {
                    "departureId": departure_city_id,
                    "arrivalId": arrival_city_id
                },
                "method": "GET"
            }

        elif self.name == AviaService.KUPIBILET.name:
            return {
                "request": get_request_to_kupibilet(**prepare_content_routes(content)),
                "callback": get_routes_from_kupibilet,
                "additionalInfo": {},
                "method": "POST"
            }
        elif self.name == AviaService.ONE_TWO_TRIP.name:
            return {
                "request": get_request_to_onetwotrip(**prepare_content_routes(content)),
                "callback": get_routes_from_onetwotrip,
                "additionalInfo": {},
                "method": "GET"
            }
