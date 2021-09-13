from typing import Iterable


class MyDict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.strict_multi_key_query = False

    def __getitem__(self, key):
        if isinstance(key, Iterable) and not isinstance(key, str):
            return [ self[k] for k in key ] if self.strict_multi_key_query \
                                            else [ self[k] for k in key if k in self ]
        else:
            return self[key]
    
    def __delitem__(self, key):
        if isinstance(key, Iterable) and not isinstance(key, str):
            [ self.__delitem__(k) for k in key ] if self.strict_multi_key_query \
                                     else [ self.__delitem__(k) for k in key if k in self ]
        else:
            self.__delitem__(key)
