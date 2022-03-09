import json
import requests
from datetime import date, datetime
from segment import Segment
from best_routes.transport_utils.exceptions import ServiceNotRespondException
from avia_route import AviaRoute
from best_routes.transport_utils import Place


def __make_url(data: dict) -> str:
    site_endpoint = "https://www.kupibilet.ru/search/"
    part1 = data["search"]["cache_key"].split(":")[0]
    part2 = data["urn"].split(":")[1]
    return site_endpoint + part1 + "/" + part2


def __get_segment(_segment: dict, codes: dict) -> Segment:
    segment_flight_time = _segment["flight_time"]
    segment_departure_code = _segment["departure_airport"]
    segment_arrival_code = _segment["arrival_airport"]
    segment_departure_airport = codes["airports"][segment_departure_code]
    segment_departure = segment_departure_airport["airport"] + \
        f" ({segment_departure_airport['city']['city']}, " \
        f"{segment_departure_airport['country']})"
    segment_arrival_airport = codes["airports"][segment_arrival_code]
    segment_arrival = segment_arrival_airport["airport"] + \
        f" ({segment_arrival_airport['city']['city']}, " \
        f"{segment_arrival_airport['country']})"
    segment_departure_datetime = datetime.fromisoformat(_segment["departure_time"])
    segment_arrival_datetime = datetime.fromisoformat(_segment["arrival_time"])
    airline_code = _segment["airline"]
    airline = codes["airlines"][airline_code]["name"]
    plane = airline_code + "-" + _segment["flight_number"]
    return Segment(segment_departure, segment_departure_code,
                   segment_arrival, segment_arrival_code,
                   segment_departure_datetime, segment_arrival_datetime,
                   segment_flight_time, airline, plane)


def __get_min_price(index: int, tickets: list) -> int:
    for ticket in tickets:
        if ticket["trip_id"] == index:
            return ticket["min_price"]
    return -1


def __get_routes(data: dict) -> list:
    _routes = []
    for _route in data["timetable"][0]:
        segments = []
        for _segment in _route["segments"]:
            segments.append(__get_segment(_segment, data["codes"]))
        departure = segments[0].departure
        arrival = segments[len(segments)-1].arrival
        departure_code = segments[0].departure_code
        arrival_code = segments[len(segments)-1].arrival_code
        departure_datetime = segments[0].departure_datetime
        arrival_datetime = segments[len(segments)-1].arrival_datetime
        duration_in_minutes = 0
        for segment in segments:
            duration_in_minutes += segment.duration_in_minutes
        url = __make_url(data)
        index = _route["raw"]["index"]
        min_price = round(__get_min_price(index, data["tickets"]) / data["currency_rate"])
        places = [Place("Минимальный", None, min_price, min_price)]
        avia_route = AviaRoute(departure, departure_code, arrival, arrival_code,
                               departure_datetime, arrival_datetime, duration_in_minutes,
                               segments, url, "https://www.kupibilet.ru/")
        avia_route.places = places
        _routes.append(avia_route)

    return _routes


#  service_class = Y or C. Y - эконом. C - бизнес
def get_routes_from_kupibilet(departure_code: str, arrival_code: str,
                              departure_date: date, adult: int, child: int,
                              infant: int,  service_class: str):

    api_endpoint = "https://flights-api-shopping-target-site.kupibilet.ru/v4/search/new"
    payload = json.dumps({
        "passengers": {
            "adult": adult,
            "child": child,
            "infant": infant
        },
        "parts": [
            {
                "departure": departure_code,
                "arrival": arrival_code,
                "date": str(departure_date)
            }
        ],
        "options": {
            "cabin_class": service_class,
            "features": [
                "seat_selection"
            ],
            "connection_search": True,
            "client_name": "site_d",
            "locale": "ru",
            "country": "RU"
        }
    })
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request(method="POST", url=api_endpoint, headers=headers, data=payload)
    data = response.json()
    if data["status"] == "fail":
        raise ServiceNotRespondException("Kupibilet.ru", data["error"])  # emptyResult - нет билетов по данному запросу
    return __get_routes(data)


