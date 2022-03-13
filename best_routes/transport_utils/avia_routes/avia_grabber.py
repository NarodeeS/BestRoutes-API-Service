from datetime import date
from .tuturu import get_routes_from_tuturu
from .kupibilet import get_routes_from_kupibilet
from .avia_service import AviaService


def get_routes_from(service: AviaService, content: dict) -> list:
    departure_code = content["departureCode"]
    arrival_code = content["arrivalCode"]
    departure_date = date.fromisoformat(content["departureDate"])
    adult = content["adult"]
    child = content["child"]
    infant = content["infant"]
    service_class = content["serviceClass"]
    routes = None
    if service == AviaService.TUTU:
        routes = get_routes_from_tuturu(departure_code, arrival_code,
                                        departure_date, adult, child, infant, service_class)

    elif service == AviaService.KUPIBILET:
        routes = get_routes_from_kupibilet(departure_code, arrival_code,
                                           departure_date, adult, child, infant, service_class)

    return [route.to_json() for route in routes]
