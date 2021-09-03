# import json

class UserDoesNotExist(ValueError):
    pass
class UserAlreadyExists(ValueError):
    pass
class BooleanParsingError(ValueError):
    pass
class EnumParsingError(ValueError):
    pass
