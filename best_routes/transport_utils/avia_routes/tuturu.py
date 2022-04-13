import json
import requests
from datetime import date, datetime
from .segment import Segment
from best_routes.exceptions import NoSuchAirportException, NoSuchRoutesException
from .avia_route import AviaRoute
from best_routes.transport_utils import Place
from requests import Response


#  service_class = Y or C. Y - эконом. C - бизнес
def get_request_to_tuturu(departure_code: str, arrival_code: str,
                          departure_date: date, adult: int, child: int,
                          infant: int, service_class: str) -> dict:

    api_endpoint = "https://offers-api.tutu.ru/avia/offers"
    departure_city_id = get_city_id(departure_code, "from")
    arrival_city_id = get_city_id(arrival_code, "to")
    payload = json.dumps({
        "passengers": {
            "child": child,
            "infant": infant,
            "full": adult
        },
        "serviceClass": service_class,
        "routes": [
            {
                "departureCityId": departure_city_id,
                "arrivalCityId": arrival_city_id,
                "departureDate": str(departure_date)
            }
        ],
        "userData": {
            "referenceToken": "anonymous_ref"
        },
        "source": "offers"
    })
    headers = {
        'Content-Type': 'application/json'
    }
    request = {
        "url": api_endpoint,
        "data": payload,
        "headers": headers
    }
    return request


def get_routes_from_tuturu(response: Response, count: int, **additional_info: dict) -> list:
    data = response.json()
    data[0]["departure_id"] = additional_info["departureId"]
    data[0]["arrival_id"] = additional_info["arrivalId"]
    routes = __get_routes(data, count)
    if len(routes) == 0:
        raise NoSuchRoutesException
    return sorted(routes, key=lambda _route: _route.get_cheapest_place())


def __make_url(departure_city_id: int, arrival_city_id: int, departure_date: date) -> str:
    url_endpoint = "https://avia.tutu.ru/offers/?"
    formatted_date = "".join(reversed(str(departure_date).split("-")))
    return url_endpoint + f"class=Y&passengers=100&route[0]=" \
                          f"{departure_city_id}-{formatted_date}-{arrival_city_id}&changes=all"


def __get_min_place(places_id: str, fare_applications: dict,
                    conditions: dict, offers: dict) -> list:

    actual_offers = offers["actual"][places_id]["offerVariants"]
    places = []
    for offer in actual_offers:
        price = offer["price"]["value"]["amount"]
        fraction = offer["price"]["value"]["fraction"]
        price_exact = round(price / fraction)
        fares = offer["fareApplications"]
        name = ""
        for fare_id in fares.values():
            fare_application = fare_applications[fare_id[0]]
            condition_id = fare_application["segmentConditions"]
            name = conditions[condition_id]["fareFamily"]["value"]
        places.append(Place(name, None, price_exact, price_exact))

    return places


def get_city_id(code: str, direction: str) -> int:
    api_endpoint = "https://avia.tutu.ru/suggest/city/v5/"
    params = {
        "name": code,
        "direction": direction
    }
    response = requests.get(url=api_endpoint, params=params)
    data = response.json()
    if isinstance(data, list):
        for offer in data:
            if offer["code"] == code:
                return int(offer["id"])

        raise NoSuchAirportException(code)


def __get_segments(_route: dict, _segments: dict, points: dict,
                   cities: dict, carriers: dict) -> list:

    segments = []
    for _segment_id in _route["segmentIds"]:
        _segment = _segments[_segment_id]

        segment_departure_airport = points[str(_segment["departureGeoPointId"])]
        segment_departure_airport_name = segment_departure_airport["name"]["nominative"]
        segment_departure_city = cities[str(segment_departure_airport["cityId"])]["name"]["nominative"]
        segment_departure_datetime = datetime.fromisoformat(_segment["departureDateTime"])
        segment_departure = f"{segment_departure_airport_name} ({segment_departure_city})"

        segment_arrival_airport = points[str(_segment["arrivalGeoPointId"])]
        segment_arrival_airport_name = segment_arrival_airport["name"]["nominative"]
        segment_arrival_city = cities[str(segment_arrival_airport["cityId"])]["name"]["nominative"]
        segment_arrival_datetime = datetime.fromisoformat(_segment["arrivalDateTime"])
        segment_arrival = f"{segment_arrival_airport_name} ({segment_arrival_city})"

        segment_duration_in_minutes = _segment["duration"]
        segment_plane = _segment["voyageNumber"]
        segment_airline = carriers[_segment["carriers"][1]["id"]]["name"]
        segments.append(Segment(segment_departure, None, segment_arrival,
                                None, segment_departure_datetime, segment_arrival_datetime,
                                segment_duration_in_minutes, segment_airline, segment_plane))
    return segments


def __get_routes(data: list, count: int) -> list:
    dictionary = data[0]["dictionary"]
    points = dictionary["avia"]["points"]
    common = dictionary["common"]
    cities = common["cities"]
    carriers = common["carriers"]
    _routes = common["routes"]
    result_routes = []
    for _route_key in _routes.keys():
        route_segments = __get_segments(_routes[_route_key], common["segments"],
                                        points, cities, carriers)
        departure = route_segments[0].departure
        departure_datetime = route_segments[0].departure_datetime
        arrival = route_segments[len(route_segments) - 1].arrival
        arrival_datetime = route_segments[len(route_segments) - 1].arrival_datetime
        duration_in_minutes = 0
        segments_id = ""
        for _segment_id in _routes[_route_key]["segmentIds"]:
            segments_id += _segment_id + "+"
        segments_id = segments_id[0: len(segments_id)-1]
        for segment in route_segments:
            duration_in_minutes += segment.duration_in_minutes
        url = __make_url(data[0]["departure_id"], data[0]["arrival_id"], departure_datetime.date())
        source = "https://www.tutu.ru/"
        _route = AviaRoute(departure, None, arrival, None, departure_datetime,
                           arrival_datetime, duration_in_minutes, route_segments, url, source)
        _route.places = __get_min_place(segments_id, common["fareApplications"],
                                        dictionary["avia"]["conditions"], data[0]["offers"])
        result_routes.append(_route)

    return sorted(result_routes)[0:count]

