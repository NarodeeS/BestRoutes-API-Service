class NoSuchRoutesException(Exception):
    def __init__(self, code="0", message="No such routes"):
        self.code = code
        self.message = message

    def __str__(self):
        return f"Message: {self.message}\nException code: {self.code}"