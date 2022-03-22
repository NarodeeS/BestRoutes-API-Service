from datetime import date
from .tuturu import get_routes_from_tuturu
from .kupibilet import get_routes_from_kupibilet
from .avia_service import AviaService
from .avia_service import get_all_services
from best_routes.exceptions import NoSuchRoutesException


def get_avia_routes_from_service(service: AviaService, content: dict) -> list:
    routes = __get_raw_routes_from_service(service, content)
    return [route.to_json() for route in routes]


def get_avia_trips_from_service(service: AviaService, content: dict) -> list:
    departure_date1 = content["departureDate1"]
    content["departureDate"] = departure_date1
    routes_to = __get_raw_routes_from_service(service, content)
    departure_date2 = content["departureDate2"]
    content["departureDate"] = departure_date2
    content["departureCode"], content["arrivalCode"] = content["arrivalCode"], content["departureCode"]
    routes_back = __get_raw_routes_from_service(service, content)
    return __make_trips(routes_to, routes_back)


def get_avia_routes(content: dict) -> list:
    routes = []
    for service in get_all_services():
        new_routes = get_avia_routes_from_service(service, content)
        for new_route in new_routes:
            if routes.count(new_route):
                index = routes.index(new_route)
                old_route = routes[index]
                if new_route.get_cheapest_place() < old_route.get_cheapest_place():
                    routes[index] = new_route
            else:
                routes.append(new_route)

    sorted_routes = sorted(routes, key=lambda _route: _route.get_cheapest_place())
    return [route.to_json() for route in sorted_routes]


def get_avia_trips(content: dict) -> list:
    departure_date1 = content["departureDate1"]
    content["departureDate"] = departure_date1
    routes_to = []
    for avia_service in get_all_services():
        routes_to.extend(__get_raw_routes_from_service(avia_service, content))
    routes_to_sorted = sorted(routes_to, key=lambda _route: _route.get_cheapest_place())
    routes_back = []
    departure_date2 = content["departureDate2"]
    content["departureDate"] = departure_date2
    content["departureCode"], content["arrivalCode"] = content["arrivalCode"], content["departureCode"]
    for avia_service in get_all_services():
        routes_back.extend(__get_raw_routes_from_service(avia_service, content))
    routes_back_sorted = sorted(routes_back, key=lambda _route: _route.get_cheapest_place())
    return __make_trips(routes_to_sorted, routes_back_sorted)


def __make_trips(routes_to: list, routes_back: list):
    result = []
    for i in range(min(len(routes_to), len(routes_back))):
        trip = {
            "to": routes_to[i].to_json(),
            "back": routes_back[i].to_json(),
            "tripMinCost": routes_to[i].get_cheapest_place() + routes_back[i].get_cheapest_place()
        }
        result.append(trip)
    return result


def __get_raw_routes_from_service(service: AviaService, content: dict):
    departure_code = content["departureCode"]
    arrival_code = content["arrivalCode"]
    departure_date = date.fromisoformat(content["departureDate"])
    if departure_date < date.today():
        raise NoSuchRoutesException(101, "you entered an already expired date")
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

    return routes
