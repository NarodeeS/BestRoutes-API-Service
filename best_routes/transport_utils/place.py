class Place:
    def __init__(self, name: str, count: int,
                 min_price: float, max_price: float) -> None:

        self.name = name
        self.count = count
        self.min_price = min_price
        self.max_price = max_price

    def to_json(self) -> dict:
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

    def __add__(self, other):
        if isinstance(other, Place):
            return self.min_price + other.min_price
