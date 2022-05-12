import json
from requests.exceptions import Timeout, MissingSchema, ConnectionError
from threading import Thread
from concurrent.futures import ThreadPoolExecutor
from time import sleep
from best_routes.transport_utils.avia_routes import get_avia_routes
from best_routes.database_interaction import *
from best_routes.database_interaction.models import User


class DirectionsManagerThread(Thread):
    def __init__(self, interval: float) -> None:
        super().__init__()
        self.interval = interval
        self.is_working = True

    def run(self) -> None:
        while self.is_working:
            checking_thread = Thread(target=_checking_task)
            checking_thread.start()
            checking_thread.join()
            sleep(self.interval)


def _user_task(user: User) -> list:
    result = []
    for user_direction in get_directions_by_user_id(user.id):
        if not user_direction.in_trip:
            if user_direction.departure_date >= date.today():
                routes = get_avia_routes(user_direction.to_request_form())
                if len(routes) != 0 and routes[0]["minPrice"] != user_direction.direction_min_cost:
                    content = {
                        "type": "direction",
                        "oldPrice": user_direction.direction_min_cost,
                        "newPrice": routes[0]["minPrice"],
                        "directionId": user_direction.id,
                        "userId": user.id
                    }
                    update_avia_direction_cost(user_direction.id, routes[0]["minPrice"])
                    result.append(content)
            else:
                delete_avia_direction(user_direction.id)

    for user_trip in get_trips_by_user_id(user.id):
        direction_to = user_trip.direction_to
        direction_back = user_trip.direction_back
        if direction_to.departure_date >= date.today() and direction_back.departure_date >= date.today():
            routes_to = get_avia_routes(direction_to.to_request_form())
            routes_back = get_avia_routes(direction_back.to_request_form())

            if len(routes_to) != 0 and len(routes_back) != 0:
                if routes_to[0]["minPrice"] != direction_to.direction_min_cost:
                    update_avia_direction_cost(direction_to.id, routes_to[0]["minPrice"])

                if routes_back[0]["minPrice"] != direction_back.direction_min_cost:
                    update_avia_direction_cost(direction_back.id, routes_back[0]["minPrice"])
                potential_new_cost = direction_to.direction_min_cost + direction_back.direction_min_cost
                if potential_new_cost != user_trip.trip_min_cost:
                    content = {
                        "type": "trip",
                        "oldPrice": user_trip.trip_min_cost,
                        "newPrice": potential_new_cost,
                        "tripId": user_trip.id,
                        "userId": user.id
                    }
                    update_avia_trip_cost(user_trip.id, potential_new_cost)
                    result.append(content)
        else:
            delete_avia_trip(user_trip.id)
    return result


def _checking_task() -> None:
    users = get_all_users()
    with ThreadPoolExecutor() as executor:
        results = executor.map(_user_task, users)
        executor.shutdown(wait=True)
        content = []
        for result in results:
            content.extend(result)
        if len(content) != 0:
            _send_to_all_services(content)


def _send_to_service(tt: tuple) -> None:
    service, content, headers = tt
    if service.is_active:
        try:
            requests.post(url=service.url, data=json.dumps(content), headers=headers, timeout=3.15)
        except (Timeout, MissingSchema, ConnectionError):
            deactivate_service(service.id)


def _send_to_all_services(content: dict) -> None:
    services = get_all_services()
    headers = {
        "Content-Type": "application/json"
    }
    with ThreadPoolExecutor() as executor:
        executor.map(_send_to_service, [(service, content, headers) for service in services])
        executor.shutdown(wait=True)
