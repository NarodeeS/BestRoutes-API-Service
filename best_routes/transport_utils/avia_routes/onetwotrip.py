import os
from datetime import date, datetime
from requests import Response
from best_routes.transport_utils import Place
from .segment import Segment
from .avia_route import AviaRoute


def get_request_to_onetwotrip(departure_code: str, arrival_code: str,
                              departure_date: date, adult: int, child: int,
                              infant: int, service_class: str) -> dict:

    api_endpoint = "https://www.onetwotrip.com/_avia-search-proxy/search/v3"
    route = f"{'%02d' % departure_date.day}{'%02d' % departure_date.month}{departure_code}{arrival_code}"
    if service_class == "Y":
        service_class = "E"
    elif service_class == "B":
        service_class = "C"
    params = {
        "route": route,
        "ad": adult,
        "cn": child,
        "in": infant,
        "cs": service_class,
        "source": "organic_ru",
        "noMix": True,
        "priceIncludeBaggage": False,
        "noClearNoBags": True
    }
    headers = {
        "User-Agent": os.environ.get("USER_AGENT")
    }
    request = {
        "url": api_endpoint,
        "params": params,
        "headers": headers
    }
    return request


def get_routes_from_onetwotrip(response: Response):
    data = response.json()
    if "error" in data.keys():
        return []
    routes = __get_routes(data)
    return sorted(routes)


def __get_routes(data: list) -> list:
    url = __get_url(data["requestInfo"]["routeKey"])
    source = "https://www.onetwotrip.com/"
    routes = []
    for transport_variant in data["transportationVariants"].values():
        total_duration = transport_variant["totalJourneyTimeMinutes"]
        min_price = __get_min_cost(data["prices"], transport_variant["id"])
        places = [Place("Минимальный", min_price, min_price)]
        segments = []
        for segment in transport_variant["tripRefs"]:
            segments.append(__get_segment(data["trips"], data["references"]["airports"], segment["tripId"]))
        departure = segments[0].departure
        departure_code = segments[0].departure_code
        arrival = segments[len(segments)-1].arrival
        arrival_code = segments[len(segments)-1].arrival_code
        departure_datetime = segments[0].departure_datetime
        arrival_datetime = segments[0].arrival_datetime
        routes.append(AviaRoute(departure, departure_code, arrival, arrival_code, departure_datetime,
                                arrival_datetime, total_duration, segments, places, url, source))

    return sorted(routes)


def __get_segment(trips: dict, airports: dict, segment_id: str) -> Segment:
    basic_segment = trips[segment_id]
    from_station_code = basic_segment["from"]
    from_station = airports[from_station_code]["name"]
    to_station_code = basic_segment["to"]
    to_station = airports[to_station_code]["name"]
    departure_datetime = datetime.fromisoformat(basic_segment["startDateTime"])
    arrival_datetime = datetime.fromisoformat(basic_segment["endDateTime"])
    duration = basic_segment["tripTimeMinutes"]
    airline = basic_segment["carrier"]
    plane = f"{airline}-{basic_segment['carrierTripNumber']}"
    return Segment(from_station, from_station_code, to_station, to_station_code,
                   departure_datetime, arrival_datetime, duration, airline, plane)


def __get_min_cost(prices: dict, transport_variant_id: str) -> Place:
    for price_key in prices.keys():
        if transport_variant_id in prices[price_key]["transportationVariantIds"]:
            return prices[price_key]["totalAmount"]


def __get_url(route_key: str):
    url_endpoint = "https://www.onetwotrip.com/ru/f/search/"
    return f"{url_endpoint}{route_key}"
