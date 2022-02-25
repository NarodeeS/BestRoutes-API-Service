from datetime import datetime
from place import Place

class Route:
    def __init__(self, from_station: str,  
        to_station: str, train_number: int, 
        dep_datetime: datetime, arr_datetime: datetime, url: str) -> None:
        
        self.from_s = from_station
        self.to_s = to_station
        self.train_number = train_number
        self.dep_date = dep_datetime
        self.arr_date = arr_datetime
        self.url = url
        self.places = []

    def add_place(self, name: str, count: int, whole: int, cents: int) -> None:
        self.places.append(Place(name, count, whole, cents))
    
    
    def __str__(self) -> str:
        return f"From: {self.from_s}\n" \
            f"To: {self.to_s}\n" \
            f"Train: {self.train_number}\n" \
            f"Departure date: {self.dep_date}\n" \
            f"Arrival date: {self.arr_date}\n" \
            f"URL: {self.url}\n" \
            "Places: {\n" + self.__get_places_info() + "\n}"

    def __get_places_info(self) -> str:
        result = ""
        for place in self.places:
            result += place.__str__() + "\n"
        
        return result