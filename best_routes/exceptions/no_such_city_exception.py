class NoSuchCityException(Exception):
    def __init__(self, city_code: str) -> None:
        self.city_code = city_code

    def __str__(self) -> str:
        return f"Can't find city presented in the request. " \
               f"City code: {self.city_code}"
