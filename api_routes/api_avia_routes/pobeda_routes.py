import requests
import json
import os
from datetime import date, datetime, time
from array import array
from api_routes.exceptions.service_not_respond_exception import ServiceNotRespondException
from api_routes.exceptions.no_such_routes_exception import NoSuchRoutesException
from station_name import get_airport_name_by_code
from segment import Segment
from api_routes.place import Place
from avia_route import AviaRoute
from dotenv import load_dotenv


load_dotenv()


def __make_url(departure_code: str, arrival_code: str, departure_date: date,
               adult: int, teens: int, child: int, inf: int):
    url_endpoint = "https://www.pobeda.aero/ru/booking/select/?"
    return url_endpoint + f"origin1={departure_code}&destination1={arrival_code}" \
                          f"&departure1={str(departure_date)}&adt1={adult}" \
                          f"&tng1={teens}&chd1={child}&inf1={inf}" \
                          f"&exst1=0&adt2=0&tng2=0&chd2=0&inf2=0&exst2=0" \
                          f"&currency=RUB"


def __get_places(fares: array) -> array:
    places = []
    for fare in fares:
        name = ""
        if fare["serviceBundleCode"] == "STD":
            name = "Базовый"
        elif fare["serviceBundleCode"] == "PLS2":
            name = "Выгодный"
        elif fare["serviceBundleCode"] == "PRE1":
            name = "Максимум"
        count = fare["availableSeats"]
        price = fare["totalAmount"]
        place = Place(name, count, price, price)
        places.append(place)
    return places


def __get_routes(journeys: array, url: str) -> array:
    _routes = []
    for journey in journeys[0:-1]:
        departure_code = journey["origin"]
        arrival_code = journey["destination"]
        airports_names = get_airport_name_by_code(departure_code, arrival_code)
        departure = airports_names[departure_code]
        arrival = airports_names[arrival_code]
        departure_datetime = datetime.fromisoformat(journey["std"])
        arrival_datetime = datetime.fromisoformat(journey["sta"])
        duration = time.fromisoformat(journey["duration"])

        segments = []
        for segment in journey["segments"]:
            segment_departure_code = segment["origin"]
            segment_arrival_code = segment["destination"]
            segment_airports_names = get_airport_name_by_code(segment_departure_code, segment_arrival_code)
            segment_departure = segment_airports_names[segment_departure_code]
            segments_arrival = segment_airports_names[segment_arrival_code]
            segment_departure_datetime = segment["std"]
            segment_arrival_datetime = segment["sta"]
            segment_duration = time.fromisoformat(segment["duration"])
            plane = segment["transport"]["carrier"]["code"] + segment["transport"]["number"]
            _segment = Segment(segment_departure, segment_departure_code,
                               segments_arrival, segment_arrival_code,
                               segment_departure_datetime, segment_arrival_datetime,
                               segment_duration, plane)
            segments.append(_segment)
        places = __get_places(journey["fares"])
        _route = AviaRoute(departure, departure_code, arrival, arrival_code,
                           departure_datetime, arrival_datetime, duration, segments, url)
        _route.places = places
        _routes.append(_route)
    return _routes


def __get_data(departure_code: str, arrival_code: str,
               departure_date: date, adult: int, teens: int, child: int,
               infant: int) -> dict:

    api_endpoint = "https://www.pobeda.aero/pricing/api/v1/journeys"
    headers = {
        "apiKey": os.environ.get("POBEDA_API_KEY"),
        "Content-Type": "application/json"
    }
    payload = json.dumps({
        "customerId": os.environ.get("POBEDA_CUSTOMER_ID"),
        "journeyPriceRequests": [
            {
                "currency": "RUB",
                "destination": arrival_code,
                "origin": departure_code,
                "pax": {
                    "ADT": adult,  # age > 18
                    "TNG": teens,  # 12 <= age <= 17
                    "CHD": child,  # 2 <= age <= 12
                    "INF": infant,  # age < 2
                    "EXT": 0
                },
                "details": {
                    "allPrice": [
                        {
                            "begin": str(departure_date),
                            "end": str(departure_date)
                        }
                    ],
                    "lowestPrice": [
                        {
                            "begin": str(departure_date),
                            "end": str(departure_date)
                        }
                    ]
                },
                "id": "1"
            }
        ]
    })
    response = requests.request("POST", url=api_endpoint, headers=headers, data=payload)
    return response.json()


def get_routes_from_pobeda_airlines(departure_code: str, arrival_code: str,
                                    departure_date: date, adult: int, teens: int, child: int,
                                    infant: int) -> array:

    data = __get_data(departure_code, arrival_code, departure_date,
                      adult, teens, child, infant)
    if data["success"]:
        schedule = data["journeyPriceResponses"][0]["schedules"][0]
        if schedule["availability"] == "Available":
            journeys = schedule["journeys"]
            url = __make_url(departure_code, arrival_code, departure_date,
                             adult, teens, child, infant)
            return __get_routes(journeys, url)
        else:
            raise NoSuchRoutesException()
    else:
        raise ServiceNotRespondException(1, "Pobeda Airlines")

