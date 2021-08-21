from enum import Enum

class CardCondition(Enum):
    '''
    enum{ NP=0, LP, MP, HP, DAMAGED }
    '''
    NM      = 0
    LP      = 1
    MP      = 2
    HP      = 3
    DAMAGED = 4

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
                value = value.replace(' ', '_').upper()
                if '_' in value:
                    value = ''.join([ word[0] for word in value.split('_') ]) # `NEAR_MINT` -> `NM`
                return cls[value]
        raise ValueError(f'Unable to parse value to Condition Enum: {value}')
