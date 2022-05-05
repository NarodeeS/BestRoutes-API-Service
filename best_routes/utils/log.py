class Log:
    def __init__(self, error_type: str, message: str, function_name: str, file_name: str) -> None:
        self.error_type = error_type
        self.message = message
        self.function_name = function_name
        self.file_name = file_name

    def __str__(self) -> str:
        return f"Error: {self.error_type}\n" \
               f"With message: {self.message}\n" \
               f"In file: {self.file_name}\n" \
               f"Inside function: {self.function_name}"
