class Place:
    def __init__(self, name: str, min_price: float, max_price: float) -> None:

        self.name = name
        self.min_price = min_price
        self.max_price = max_price

    def to_json(self) -> dict:
        return {
            "name": self.name,
            "minPrice": self.min_price,
            "maxPrice": self.max_price
        }

    def __lt__(self, other) -> bool:
        if isinstance(other, Place):
            if self.min_price < other.min_price:
                return True
            return False
        return False

    def __add__(self, other) -> float:
        if isinstance(other, Place):
            return self.min_price + other.min_price
