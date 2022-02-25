from itertools import count


class Place:
    def __init__(self, name: str, count: int, 
        min_price: float, max_price: float) -> None:

        self.name = name
        self.count = count
        self.min_price = min_price
        self.max_price = max_price
    
    def __str__(self) -> str:
        return f"Type: {self.name}, " \
            f"Count: {self.count}, " \
            f"Min price: {self.min_price}, " \
            f"Max price: {self.max_price}\n"
