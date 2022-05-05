import json
from datetime import date, datetime
from requests import Response
from requests.exceptions import JSONDecodeError
from .segment import Segment
from best_routes.database_interaction import get_city_id
from .avia_route import AviaRoute
from best_routes.utils import logger
from best_routes.utils import Log
from best_routes.transport_utils import Place


def get_request_to_tuturu(departure_code: str, arrival_code: str,
                          departure_date: date, adult: int, child: int,
                          infant: int, service_class: str) -> dict:

    api_endpoint = "https://offers-api.tutu.ru/avia/offers"
    departure_city_id = get_city_id(departure_code, "from")
    arrival_city_id = get_city_id(arrival_code, "to")

    payload = json.dumps({
        "passengers": {
            "child": int(child),
            "infant": int(infant),
            "full": int(adult)
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


def get_routes_from_tuturu(response: Response, **additional_info: dict) -> list:
    try:
        data = response.json()
        data[0]["departure_id"] = additional_info["departureId"]
        data[0]["arrival_id"] = additional_info["arrivalId"]
        routes = _get_routes(data)
        return sorted(routes)
    except JSONDecodeError:
        logger.add_log(Log("JSONDecodeError", "-", "get_routes_from_tuturu", "tuturu.py"))
        return []


def _get_segments(_route: dict, _segments: dict, points: dict,
                  cities: dict, carriers: dict) -> list:

    segments = []
    for _segment_id in _route["segmentIds"]:
        _segment = _segments[_segment_id]

        segment_departure_airport = points[str(_segment["departureGeoPointId"])]
        segment_departure_airport_name = segment_departure_airport["name"]["nominative"]
        segment_departure_city = cities[str(segment_departure_airport["cityId"])]["name"]["nominative"]
        segment_departure_datetime = _get_datetime_without_tz(_segment["departureDateTime"])
        segment_departure_datetime = datetime.fromisoformat(segment_departure_datetime)
        segment_departure = f"{segment_departure_airport_name} ({segment_departure_city})"

        segment_arrival_airport = points[str(_segment["arrivalGeoPointId"])]
        segment_arrival_airport_name = segment_arrival_airport["name"]["nominative"]
        segment_arrival_city = cities[str(segment_arrival_airport["cityId"])]["name"]["nominative"]
        segment_arrival_datetime = _get_datetime_without_tz(_segment["arrivalDateTime"])
        segment_arrival_datetime = datetime.fromisoformat(segment_arrival_datetime)

        segment_arrival = f"{segment_arrival_airport_name} ({segment_arrival_city})"

        segment_duration_in_minutes = _segment["duration"]
        segment_plane = _segment["voyageNumber"]
        segment_airline = carriers[_segment["carriers"][1]["id"]]["name"]
        segments.append(Segment(segment_departure, None, segment_arrival,
                                None, segment_departure_datetime, segment_arrival_datetime,
                                segment_duration_in_minutes, segment_airline, segment_plane))
    return segments


def _get_routes(data: list) -> list:
    dictionary = data[0]["dictionary"]
    points = dictionary["avia"]["points"]
    common = dictionary["common"]
    cities = common["cities"]
    carriers = common["carriers"]
    _routes = common["routes"]
    result_routes = []
    for _route_key in _routes.keys():
        route_segments = _get_segments(_routes[_route_key], common["segments"],
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
        url = _make_url(data[0]["departure_id"], data[0]["arrival_id"], departure_datetime.date())
        source = "https://www.tutu.ru/"
        places = _get_places(segments_id, common["fareApplications"],
                             dictionary["avia"]["conditions"], data[0]["offers"])
        _route = AviaRoute(departure, None, arrival, None, departure_datetime,
                           arrival_datetime, duration_in_minutes, route_segments, places, url, source)
        result_routes.append(_route)

    return sorted(result_routes)


def _get_datetime_without_tz(datetime_string: str) -> str:
    date_string = datetime_string[0:10]
    time_string = datetime_string[11:]
    tz_pos = (time_string.find('-') + 1 or time_string.find('+') + 1)
    result_time = time_string[:tz_pos-1] if tz_pos > 0 else time_string
    return date_string+"T"+result_time


def _make_url(departure_city_id: int, arrival_city_id: int, departure_date: date) -> str:
    url_endpoint = "https://avia.tutu.ru/offers/?"
    formatted_date = "".join(reversed(str(departure_date).split("-")))
    return url_endpoint + f"class=Y&passengers=100&route[0]=" \
                          f"{departure_city_id}-{formatted_date}-{arrival_city_id}&changes=all"


def _get_places(places_id: str, fare_applications: dict,
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
            if  conditions[condition_id]["fareFamily"] is None:
                continue
            name = conditions[condition_id]["fareFamily"]["value"]
        places.append(Place(name, price_exact, price_exact))

    return places
