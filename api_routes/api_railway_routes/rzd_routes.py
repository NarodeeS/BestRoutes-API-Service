from itertools import count
import requests
from datetime import date, datetime
from array import array
from train_route import TrainRoute
from train_place import TrainPlace


def __make_url(from_city_nodeId: str, to_city_nodeId: str, dep_date: date) -> str: 
    URL_ENDPOINT = "https://ticket.rzd.ru/searchresults/v/1/"
    
    return URL_ENDPOINT + f"{from_city_nodeId}/{to_city_nodeId}" \
        f"/{dep_date.strftime('%Y-%m-%d')}"


def __get_places(places_json: array) -> array:
    places = []
    for place in places_json:
        if place["CarType"] != "Baggage": 
            place_type = place["CarTypeName"].title()
            count = place["TotalPlaceQuantity"]
            min_price = place["MinPrice"]
            max_price = place["MaxPrice"]
            places.append(TrainPlace(place_type, count, min_price, max_price))
    
    return places


def __get_routes(trains: array, url: str) -> array:
    routes = []
    for train in trains:
        from_station = train["OriginStationInfo"]["StationName"].title()
        to_station = train["DestinationStationInfo"]["StationName"].title()
        train_number = train["TrainNumber"]
        dep_datetime = datetime.fromisoformat(train["LocalDepartureDateTime"])
        arr_datetime = datetime.fromisoformat(train["LocalArrivalDateTime"])
        route = TrainRoute(from_station, to_station, train_number, dep_datetime, arr_datetime, url)
        route.places = __get_places(train["CarGroups"])
        routes.append(route)
    
    return routes


def __sort_routes_by_price(routes: array) -> array:
    return sorted(routes, key=lambda route: route.get_cheapiest_place())
        

# By default sorted by departure time
def get_routes_from_rzd(from_station_code: str, from_station_nodeId: str, 
    to_station_code: str, to_station_nodeId: str, dep_date: datetime) -> array:

    API_ENDPOINT = "https://ticket.rzd.ru/apib2b/p/Railway/V1/Search/TrainPricing"
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

    response = requests.post(url=API_ENDPOINT, params=params, json=body)
    data = response.json()
    url = __make_url(from_station_nodeId, to_station_nodeId, dep_date)
    return __get_routes(data["Trains"], url)


def get_routes_from_rzd_sorted_by_price(from_station_code: str, from_station_nodeId: str, 
    to_station_code: str, to_station_nodeId: str, dep_date: datetime) -> array:

    basic_routes = get_routes_from_rzd(from_station_code, from_station_nodeId,
        to_station_code, to_station_nodeId, dep_date)

    return __sort_routes_by_price(basic_routes)


# By default without any sorting 
def get_routes_from_rzd_return(from_station_code: str, from_station_nodeId: str, 
    to_station_code: str, to_station_nodeId: str, 
    dep_date1: datetime, dep_date2: datetime) -> dict:

    routes_there = get_routes_from_rzd(from_station_code, from_station_nodeId, 
        to_station_code, to_station_nodeId, dep_date1)

    routes_back = get_routes_from_rzd(to_station_code, to_station_nodeId, 
        from_station_code, from_station_nodeId, dep_date2)
    
    result_dict = {}
    count = 0
    for there in routes_there:
        for back in routes_back:
            trip_min_amount = there.get_cheapiest_place().min_price + \
                back.get_cheapiest_place().min_price

            trip = {
                "There": there,
                "Back": back,
                "TripMinAmount": trip_min_amount
            }

            result_dict[count] = trip
    
    return result_dict


def get_routes_from_rzd_return_sorted_by_price(from_station_code: str, 
    from_station_nodeId: str, to_station_code: str, to_station_nodeId: str, 
    dep_date1: datetime, dep_date2: datetime) -> dict:

    basic_trips = get_routes_from_rzd_return(from_station_code, 
        from_station_nodeId, to_station_code, to_station_nodeId,
        dep_date1, dep_date2)

    return sorted(basic_trips["TripMinAmount"])

    
