import requests
from requests.exceptions import Timeout
from threading import Thread
from datetime import date
from best_routes.transport_utils.avia_routes import get_avia_routes, get_avia_trips
from concurrent.futures import ThreadPoolExecutor
from best_routes.database import session
from best_routes.database.models import User, Service
from time import sleep


def user_task(user: User) -> None:
    for user_route in user.tracked_avia_directions:
        if user_route.departure_date <= date.today():
            routes = get_avia_routes(user_route.to_request_form())
            if routes[0]["minPrice"] < user_route.direction_min_cost:
                content = {
                    "type": "direction",
                    "oldPrice": user_route.direction_min_cost,
                    "newPrice": routes[0]["minPrice"],
                    "id": user_route.id
                }
                user_route.direction_min_cost = routes[0].get_cheapest_place().min_price
                session.commit()
                session.rollback()
                __send_to_all_services(content)

    for user_trip in user.tracked_avia_trips:
        trips = get_avia_trips(user_trip.to_request_form())
        if trips[0]["tripMinCost"] < user_trip.trip_min_cost:
            content = {
                "type": "trip",
                "oldPrice": user_trip.trip_min_cost,
                "newPrice": trips[0]["tripMinCost"],
                "id": user_trip.id
            }
            user_trip.trip_min_cost = trips[0]["tripMinCost"]
            session.commit()
            session.rollback()
            __send_to_all_services(content)


def __send_to_all_services(content: dict) -> None:
    services = session.query(Service)
    for service in services:
        try:
            requests.post(url=service.url, data=content, timeout=3.15)
        except Timeout:
            print(f"Service {service.name} is not responding")
            service.is_active = False
            session.commit()
            session.rollback()


class DirectionsManagerThread(Thread):
    def __init__(self, interval: float):
        super().__init__()
        self.interval = interval
        self.is_working = True

    def run(self) -> None:
        while self.is_working:
            users = session.query(User)
            futures = []
            with ThreadPoolExecutor() as executor:
                for user in users:
                    futures.append(executor.submit(user_task, user))
                executor.shutdown(wait=True)
            sleep(self.interval)
