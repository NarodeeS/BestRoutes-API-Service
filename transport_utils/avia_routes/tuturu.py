import json
import requests
from datetime import date, datetime
from dotenv import load_dotenv
from segment import Segment
from transport_utils.exceptions import NoSuchAirportException
from avia_route import AviaRoute


load_dotenv()


def __make_url(departure_city_id: int, arrival_city_id: int, departure_date: date) -> str:
    url_endpoint = "https://avia.tutu.ru/offers/?"
    formatted_date = "".join(reversed(str(departure_date).split("-")))
    return url_endpoint + f"class=Y&passengers=100&route[0]=" \
                          f"{departure_city_id}-{formatted_date}-{arrival_city_id}&changes=all"


def __get_city_id(code: str, direction: str) -> int:
    api_endpoint = "https://avia.tutu.ru/suggest/city/v5/"
    params = {
        "code": code,
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
        segment_airline = carriers[_segment["carriers"][1]["id"]]
        segments.append(Segment(segment_departure, None, segment_arrival,
                                None, segment_departure_datetime, segment_arrival_datetime,
                                segment_duration_in_minutes, segment_airline, segment_plane))
    return segments


def __get_routes(data: list) -> list:
    dictionary = data[0]["dictionary"]
    points = dictionary["avia"]["points"]
    common = dictionary["common"]
    cities = common["cities"]
    carriers = common["carriers"]
    routes = common["routes"]
    result_routes = []
    for _route_key in routes.keys():
        route_segments = __get_segments(routes[_route_key], common["segments"],
                                        points, cities, carriers)
        departure = route_segments[0].departure
        departure_datetime = route_segments[0].departure_datetime
        arrival = route_segments[len(route_segments) - 1].arrival
        arrival_datetime = route_segments[len(route_segments) - 1].arrival_datetime
        duration_in_minutes = 0
        for segment in route_segments:
            duration_in_minutes += segment.duration_in_minutes
        url = __make_url(data[0]["departure_id"], data[0]["arrival_id"], departure_datetime.date())
        source = "tutu.ru"
        result_routes.append(AviaRoute(departure, None, arrival, None, departure_datetime,
                                       arrival_datetime, duration_in_minutes, route_segments, url, source))
    return result_routes


def get_routes_from_tuturu(departure_code: str, arrival_code: str,
                           departure_date: date, adult: int, child: int,
                           infant: int) -> list:

    api_endpoint = "https://offers-api.tutu.ru/avia/offers"
    departure_city_id = __get_city_id(departure_code, "from")
    arrival_city_id = __get_city_id(arrival_code, "to")
    payload = json.dumps({
        "passengers": {
            "child": child,
            "infant": infant,
            "full": adult
        },
        "serviceClass": "Y",
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
    response = requests.post(url=api_endpoint, headers=headers, data=payload)
    data = response.json()
    data[0]["departure_id"] = departure_city_id
    data[0]["arrival_id"] = arrival_city_id
    return __get_routes(data)


routes = get_routes_from_tuturu("MOW", "LED", date.today(), 1, 0, 0)
for route in routes:
    print(route)




