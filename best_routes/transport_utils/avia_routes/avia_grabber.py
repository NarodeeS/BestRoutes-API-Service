from datetime import date
from .tuturu import get_routes_from_tuturu
from .kupibilet import get_routes_from_kupibilet
from .avia_service import AviaService
from .avia_service import get_all_services


def get_routes_from_service(service: AviaService, content: dict) -> list:
    departure_code = content["departureCode"]
    arrival_code = content["arrivalCode"]
    departure_date = date.fromisoformat(content["departureDate"])
    adult = content["adult"]
    child = content["child"]
    infant = content["infant"]
    service_class = content["serviceClass"]
    count = content["count"]
    if count == 0:
        return []
    routes = []
    if service == AviaService.TUTU:
        routes = get_routes_from_tuturu(departure_code, arrival_code,
                                        departure_date, adult, child, infant,
                                        service_class, count)

    elif service == AviaService.KUPIBILET:
        routes = get_routes_from_kupibilet(departure_code, arrival_code,
                                           departure_date, adult, child, infant,
                                           service_class, count)

    return [route.to_json() for route in routes]


def get_routes(content: dict) -> list:
    routes = []
    for service in get_all_services():
        routes.extend(get_routes_from_service(service, content))
    return routes
