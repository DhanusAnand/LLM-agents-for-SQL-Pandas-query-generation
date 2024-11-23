class InvalidInputException(Exception):
    def __init__(self, message="Invalid Input"):
        super().__init__(message)

class UserAlreadyExistsException(Exception):
    def __init__(self, username=""):
        message = f"{username} already exists! Please login instead!!"
        super().__init__(message)