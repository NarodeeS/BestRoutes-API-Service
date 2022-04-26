class NoSuchRoutesException(Exception):
    def __init__(self, code="0", message="No such routes"):
        self.code = code
        self.message = message

    def __str__(self):
        return f"We could not find routes for your request. " \
               f"Message: {self.message}. " \
               f"Exception code: {self.code}"
