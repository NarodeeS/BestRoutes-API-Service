import requests
from datetime import date, datetime
from array import array
from train_route import TrainRoute
from api_routes.place import Place


def __make_url(from_city_node_id: str, to_city_node_id: str, dep_date: date) -> str:
    url_endpoint = "https://ticket.rzd.ru/searchresults/v/1/"

    return url_endpoint + f"{from_city_node_id}/{to_city_node_id}" \
                          f"/{dep_date.strftime('%Y-%m-%d')}"


def __get_places(places_json: array) -> array:
    places = []
    for place in places_json:
        if place["CarType"] != "Baggage":
            place_type = place["CarTypeName"].title()
            count = place["TotalPlaceQuantity"]
            min_price = place["MinPrice"]
            max_price = place["MaxPrice"]
            places.append(Place(place_type, count, min_price, max_price))

    return places


def __get_routes(trains: array, url: str) -> array:
    _routes = []
    for train in trains:
        if train["HasElectronicRegistration"]:
            from_station = train["OriginStationInfo"]["StationName"].title()
            to_station = train["DestinationStationInfo"]["StationName"].title()
            train_number = train["TrainNumber"]
            dep_datetime = datetime.fromisoformat(train["LocalDepartureDateTime"])
            arr_datetime = datetime.fromisoformat(train["LocalArrivalDateTime"])
            _route = TrainRoute(from_station, to_station, train_number, dep_datetime, arr_datetime, url)
            _route.places = __get_places(train["CarGroups"])
            if dep_datetime > datetime.now():
                _routes.append(_route)

    return _routes


# By default, sorted by departure time
def get_routes_from_rzd(from_station_code: str, from_station_node_id: str,
                        to_station_code: str, to_station_node_id: str,
                        dep_date: datetime) -> array:

    api_endpoint = "https://ticket.rzd.ru/apib2b/p/Railway/V1/Search/TrainPricing"
    params = {
        "service_provider": "B2B_RZD"
    }
    body = {
        "Origin": from_station_code,
        "Destination": to_station_code,
        "DepartureDate": str(dep_date),
        "TimeFrom": 0,
        "TimeTo": 24,
        "CarGrouping": "Group",
        "GetByLocalTime": True,
        "SpecialPlacesDemand": "StandardPlacesAndForDisabledPersons"
    }
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:97.0) Gecko/20100101 Firefox/97.0"}

    response = requests.post(url=api_endpoint, params=params, json=body, headers=headers)
    data = response.json()
    url = __make_url(from_station_node_id, to_station_node_id, dep_date)
    return __get_routes(data["Trains"], url)


def get_routes_from_rzd_sorted_by_price(from_station_code: str, from_station_node_id: str,
                                        to_station_code: str, to_station_node_od: str,
                                        dep_date: datetime) -> array:

    basic_routes = get_routes_from_rzd(from_station_code, from_station_node_id,
                                       to_station_code, to_station_node_od, dep_date)

    return sorted(basic_routes, key=lambda _route: _route.get_cheapest_place())


# By default, without any sorting
def get_routes_from_rzd_return(from_station_code: str, from_station_node_id: str,
                               to_station_code: str, to_station_node_id: str,
                               dep_date1: datetime, dep_date2: datetime) -> array:

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
                    "There": there,
                    "Back": back,
                    "TripMinCost": round(trip_min_amount, 1)
                }
                result.append(trip)
            else:
                print(there)
                print(back)
    return result


def get_routes_from_rzd_return_sorted_by_price(from_station_code: str, from_station_node_id: str,
                                               to_station_code: str, to_station_node_id: str,
                                               dep_date1: datetime, dep_date2: datetime) -> dict:

    basic_trips = get_routes_from_rzd_return(from_station_code, from_station_node_id,
                                             to_station_code, to_station_node_id,
                                             dep_date1, dep_date2)

    return sorted(basic_trips, key=lambda trip: trip["TripMinCost"])
