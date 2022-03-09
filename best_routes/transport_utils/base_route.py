from datetime import datetime


class BaseRoute:
    """Contains base fields for any route"""
    def __init__(self, departure: str, arrival: str,
                 departure_datetime: datetime, arrival_datetime: datetime):

        self.departure = departure
        self.arrival = arrival
        self.departure_datetime = departure_datetime
        self.arrival_datetime = arrival_datetime
