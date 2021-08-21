from enum import Enum

class CardOperation(Enum):
    '''
    enum{ CREATE=0, UPDATE, DELETE }
    '''
    CREATE = 0
    UPDATE = 1
    DELETE = 2

    @classmethod
    def parse(cls, value):
        if isinstance(value, cls):
            return value
        if isinstance(value, int):
            return cls(value)
        if isinstance(value, str):
            try:
                return cls(int(value))
            except ValueError:
                return cls[value.upper()]
        raise ValueError(f'Unable to parse value to Operation Enum: {value}')
