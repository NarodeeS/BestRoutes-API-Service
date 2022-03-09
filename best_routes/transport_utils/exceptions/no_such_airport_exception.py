class NoSuchAirportException(Exception):
    def __init__(self, airport_code: str) -> None:
        self.airport_code = airport_code

    def __str__(self) -> str:
        return f"Airport code: {self.airport_code}\n"
