class ServiceNotRespondException(Exception):
    def __init__(self, service_type: str, msg: str = "", code: int = 0) -> None:
        self.code = code
        self.message = f"Service {service_type} not responding! " + msg

    def __str__(self) -> str:
        return f"{self.message}\nException code: {self.code}"
