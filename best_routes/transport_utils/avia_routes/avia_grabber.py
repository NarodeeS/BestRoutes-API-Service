import copy
from requests_futures.sessions import FuturesSession
from concurrent.futures import as_completed
from .avia_service import AviaService, get_all_services


def get_avia_routes_from_service(service: AviaService, content: dict) -> list:
    count = content["count"]
    routes = []
    session = FuturesSession()
    request_object = service.get_request_object(content)
    callback = request_object["callback"]
    additional_info = request_object["additionalInfo"]
    future = session.post(**request_object["request"])
    response = future.result()
    routes.extend(callback(response, count, **additional_info))
    return [route.to_json() for route in routes]


def get_avia_trips_from_service(service: AviaService, content: dict) -> list:
    count = content["count"]
    content_to = content
    content_back = copy.deepcopy(content)
    __fill_contents(content_to, content_back, content)

    request_object_to = service.get_request_object(content_to)
    request_object_back = service.get_request_object(content_back)

    future_to = FuturesSession().post(**request_object_to["request"])
    future_back = FuturesSession().post(**request_object_back["request"])

    routes_to = request_object_to["callback"](future_to.result(), count,
                                              **request_object_to["additionalInfo"])
    routes_back = request_object_back["callback"](future_back.result(), count,
                                                  **request_object_back["additionalInfo"])
    return __make_trips(routes_to, routes_back)


def get_avia_routes(content: dict) -> list:
    count = content["count"]
    routes = []
    request_objects = {}
    for service in get_all_services():
        session = FuturesSession()
        request_object = service.get_request_object(content)
        future = session.post(**request_object["request"])
        request_objects[future] = {
            "callback": request_object["callback"],
            "additionalInfo": request_object["additionalInfo"]
        }

    for future in as_completed(request_objects.keys()):
        response = future.result()
        callback = request_objects[future]["callback"]
        additional_info = request_objects[future]["additionalInfo"]
        routes.extend(callback(response, count, **additional_info))

    return [route.to_json() for route in sorted(routes)]


def get_avia_trips(content: dict) -> list:
    count = content["count"]
    content_to = content
    content_back = copy.deepcopy(content)
    __fill_contents(content_to, content_back, content)

    request_objects = {}
    for avia_service in get_all_services():
        request_object_to = avia_service.get_request_object(content_to)
        request_object_back = avia_service.get_request_object(content_back)
        future_to = FuturesSession().post(**request_object_to["request"])
        future_back = FuturesSession().post(**request_object_back["request"])
        request_objects[future_to] = {
            "where": "to",
            "callback": request_object_to["callback"],
            "additionalInfo": request_object_to["additionalInfo"]
        }
        request_objects[future_back] = {
            "where": "back",
            "callback": request_object_back["callback"],
            "additionalInfo": request_object_back["additionalInfo"]
        }

    routes_to = []
    routes_back = []
    for future in as_completed(request_objects.keys()):
        response = future.result()
        callback = request_objects[future]["callback"]
        additional_info = request_objects[future]["additionalInfo"]
        routes = callback(response, count, **additional_info)
        if request_objects[future]["where"] == "to":
            routes_to.extend(routes)
        else:
            routes_back.extend(routes)
    routes_to_sorted = sorted(routes_to, key=lambda _route: _route.get_cheapest_place())
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


def __fill_contents(content_to: dict, content_back: dict, content: dict):
    departure_date1 = content["departureDate1"]
    content_to["departureDate"] = departure_date1
    departure_date2 = content["departureDate2"]

    content_back["departureDate"] = departure_date2
    content_back["departureCode"], content_back["arrivalCode"] = \
        content_to["arrivalCode"], content_to["departureCode"]
