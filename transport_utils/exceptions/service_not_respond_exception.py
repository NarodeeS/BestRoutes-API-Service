class ServiceNotRespondException(Exception):
    def __init__(self, service_type, msg="", code=0):
        self.code = code
        self.message = f"Service {service_type} not responding! " + msg

    def __str__(self):
        return f"Message: {self.message}\nException code: {self.code}"
