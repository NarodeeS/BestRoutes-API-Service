class Place:
    def __init__(self, name: str, count: int,
                 min_price: float, max_price: float) -> None:

        self.name = name
        self.count = count
        self.min_price = min_price
        self.max_price = max_price

    def to_json(self):
        return {
            "name": self.name,
            "count": self.count,
            "minPrice": self.min_price,
            "maxPrice": self.max_price
        }

    def __lt__(self, other) -> bool:
        if isinstance(other, Place):
            if self.min_price < other.min_price:
                return True
            return False
        return False

    def __str__(self) -> str:
        return f"Type: {self.name}, " \
            f"Count: {self.count}, " \
            f"Min price: {self.min_price}, " \
            f"Max price: {self.max_price}\n"
