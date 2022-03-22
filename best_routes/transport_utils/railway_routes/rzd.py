import requests
import os
from datetime import date, datetime
from dotenv import load_dotenv
from .train_route import TrainRoute
from best_routes.transport_utils import Place


load_dotenv()


def get_routes_from_rzd(from_station_code: str, from_station_node_id: str,
                        to_station_code: str, to_station_node_id: str,
                        dep_date: datetime) -> list:

    api_endpoint = os.environ.get("RZD_API_ENDPOINT")
    params = {
        "service_provider": "B2B_RZD"
    }
    body = {
        "Origin": from_station_code,
        "Destination": to_station_code,
        "DepartureDate": str(dep_date),
        "TimeFrom": 0,
        "TimeTo": 24,
        "CarGrouping": "DontGroup",
        "GetTrainsFromSchedule": True,
        "GetByLocalTime": True,
        "SpecialPlacesDemand": "StandardPlacesAndForDisabledPersons"
    }
    headers = {"User-Agent": os.environ.get("USER_AGENT")}

    response = requests.request(method="POST", url=api_endpoint,
                                params=params, json=body, headers=headers)
    data = response.json()
    url = __make_url(from_station_node_id, to_station_node_id, dep_date)
    routes = __get_routes(data["Trains"], url)
    sorted(routes, key=lambda _route: _route.get_cheapest_place())


# By default, without any sorting
def get_routes_from_rzd_return(from_station_code: str, from_station_node_id: str,
                               to_station_code: str, to_station_node_id: str,
                               dep_date1: datetime, dep_date2: datetime) -> list:

    routes_there = get_routes_from_rzd(from_station_code, from_station_node_id,
                                       to_station_code, to_station_node_id, dep_date1)

    routes_back = get_routes_from_rzd(to_station_code, to_station_node_id,
                                      from_station_code, from_station_node_id, dep_date2)

    result = []
    for there in routes_there:
        for back in routes_back:
            if len(there.places) != 0 and len(back.places) != 0:
                trip_min_amount = there.get_cheapest_place().min_price + back.get_cheapest_place().min_price
                trip = {
                    "to": there,
                    "back": back,
                    "tripMinCost": round(trip_min_amount, 1)
                }
                result.append(trip)
            else:
                print(there)
                print(back)
    return sorted(result, key=lambda _trip: _trip["TripMinCost"])


def __make_url(from_city_node_id: str, to_city_node_id: str, dep_date: date) -> str:
    url_endpoint = "https://ticket.rzd.ru/searchresults/v/1/"

    return url_endpoint + f"{from_city_node_id}/{to_city_node_id}" \
                          f"/{dep_date.strftime('%Y-%m-%d')}"


def __get_places(places_json: list) -> list:
    places = []
    for place in places_json:
        if place["CarType"] != "Baggage":
            place_type = place["CarTypeName"].title()
            count = place["TotalPlaceQuantity"]
            min_price = place["MinPrice"]
            max_price = place["MaxPrice"]
            places.append(Place(place_type, count, min_price, max_price))

    return places


def __get_routes(trains: list, url: str) -> list:
    _routes = []
    for train in trains:
        has_electronic_registration = train["HasElectronicRegistration"]
        from_station = train["OriginStationInfo"]["StationName"].title()
        to_station = train["DestinationStationInfo"]["StationName"].title()
        train_number = train["TrainNumber"]
        dep_datetime = datetime.fromisoformat(train["LocalDepartureDateTime"])
        arr_datetime = datetime.fromisoformat(train["LocalArrivalDateTime"])
        _route = TrainRoute(from_station, to_station, train_number, has_electronic_registration,
                            dep_datetime, arr_datetime, url)
        _route.places = __get_places(train["CarGroups"])
        if dep_datetime > datetime.now():
            _routes.append(_route)

    return _routes
