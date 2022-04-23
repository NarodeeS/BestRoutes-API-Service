import requests
from requests.exceptions import Timeout, MissingSchema
from threading import Thread
from datetime import date
from best_routes.transport_utils.avia_routes import get_avia_routes, get_avia_trips
from concurrent.futures import ThreadPoolExecutor
from best_routes.database_interaction import *
from best_routes.database_interaction.models import User
from time import sleep


def user_task(user: User) -> None:
    print("checking user " + str(user.id))
    for user_direction in get_directions_by_user_id(user.id):
        print("checking user direction " + str(user_direction.id))
        if user_direction.departure_date >= date.today():
            routes = get_avia_routes(user_direction.to_request_form())
            if routes[0]["minPrice"] < user_direction.direction_min_cost:
                content = {
                    "type": "direction",
                    "oldPrice": user_direction.direction_min_cost,
                    "newPrice": routes[0]["minPrice"],
                    "directionId": user_direction.id,
                    "userId": user.id
                }
                update_avia_direction_cost(user_direction.id, routes[0]["minPrice"])
                __send_to_all_services(content)
        else:
            delete_avia_direction(user_direction.id)

    for user_trip in get_trips_by_user_id(user.id):
        trips = get_avia_trips(user_trip.to_request_form())
        if trips[0]["tripMinCost"] < user_trip.trip_min_cost:
            content = {
                "type": "trip",
                "oldPrice": user_trip.trip_min_cost,
                "newPrice": trips[0]["tripMinCost"],
                "tripId": user_trip.id,
                "userId": user.id
            }
            update_avia_trip_cost(user_trip.id, trips[0]["tripMinCost"])
            __send_to_all_services(content)


def checking_task_new() -> None:
    pass


def checking_task() -> None:
    users = get_all_users()
    futures = []
    with ThreadPoolExecutor() as executor:
        for user in users:
            futures.append(executor.submit(user_task, user))
        executor.shutdown(wait=True)


def __send_to_all_services(content: dict) -> None:
    services = get_all_services()
    for service in services:
        try:
            requests.post(url=service.url, data=content, timeout=3.15)
        except (Timeout, MissingSchema):
            deactivate_service(service.id)
        except Exception as e:
            print(type(e))


class DirectionsManagerThread(Thread):
    def __init__(self, interval: float):
        super().__init__()
        self.interval = interval
        self.is_working = True

    def run(self) -> None:
        while self.is_working:
            checking_thread = Thread(target=checking_task)
            checking_thread.start()
            checking_thread.join()
            sleep(self.interval)
