from enum import Enum

from .errors import EnumParsingError


class _BaseEnum(Enum):
    def __str__(self):
        return self.name


class DatabaseOperation(_BaseEnum):
    '''
    enum{ CREATE=0, UPDATE, DELETE, NOP }
    '''
    CREATE = 0
    UPDATE = 1
    DELETE = 2
    NOP    = 3

    @classmethod
    def parse(cls, value):
        if not value:
            return None
        if isinstance(value, cls):
            return value
        if isinstance(value, int):
            return cls(value)
        if isinstance(value, str):
            try:
                return cls(int(value))
            except ValueError:
                try:
                    return cls[value.upper()]
                except KeyError:
                    pass
        raise EnumParsingError(f'Unable to parse value to Operation Enum: `{value}`')

    def __eq__(self, other):
        return super().__eq__(other) or \
                self.to_past_tense() == other.upper()

    def to_past_tense(self):
        if self == DatabaseOperation.CREATE:
            return 'CREATED'
        if self == DatabaseOperation.UPDATE:
            return 'UPDATED'
        if self == DatabaseOperation.DELETE:
            return 'DELETED'
        if self == DatabaseOperation.NOP:
            return 'NOP'
        raise ValueError(f'Unable to get past tense for Operation Enum: `{self}`')


class CardCondition(_BaseEnum):
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
        if not value:
            return None
        if isinstance(value, cls):
            return value
        if isinstance(value, int):
            return cls(value)
        if isinstance(value, str):
            try:
                return cls(int(value))
            except ValueError:
                try:
                    value = value \
                            .replace(' ', '_') \
                            .replace('-', '_') \
                            .upper()
                    if '_' in value:
                        value = ''.join([ word[0] for word in value.split('_') ]) # `NEAR_MINT` -> `NM`
                    return cls[value]
                except KeyError:
                    pass
        raise EnumParsingError(f'Unable to parse value to Condition Enum: `{value}`')
