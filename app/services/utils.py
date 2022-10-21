import re
from datetime import datetime
from typing import Any, Iterable, Literal, Pattern

from bson import ObjectId
from bson.errors import InvalidId


def compile_case_sensitive_str(pattern: str,
                               ignorecase: bool = True,
                               match_whole_word: bool = False) -> Pattern[str]:
    return re.compile(
        fr'^{re.escape(pattern)}$' if match_whole_word else re.escape(pattern),
        re.IGNORECASE if ignorecase else 0
    )


def compile_case_sensitive_list(patterns: Iterable[str],
                                ignorecase: bool = True,
                                match_whole_word: bool = False,
                                match_all_items: bool = True) -> dict[Literal['$all', '$in'], Pattern[str]]:
    key = '$all' if match_all_items else '$in'
    return {
        key: [
            compile_case_sensitive_str(value, ignorecase, match_whole_word)
            for value in patterns
        ]
    }


def compile_case_sensitive_dict(patterns: dict[str, Any],
                                ignorecase: bool = True,
                                match_whole_word: bool = False) -> dict[str, Any | Pattern[str]]:
    patterns = patterns.copy()

    for key, value in patterns.items():
        try:
            patterns[key] = ObjectId(value)

        except (TypeError, InvalidId):
            if isinstance(value, bool | int | float | datetime | None):
                continue
            elif isinstance(value, dict):
                patterns[key] = compile_case_sensitive_dict(value, ignorecase, match_whole_word)
            elif isinstance(value, list | tuple):
                patterns[key] = compile_case_sensitive_list(value, ignorecase, match_whole_word, match_all_items=True)
            else:
                patterns[key] = compile_case_sensitive_str(str(value), ignorecase, match_whole_word)

    return patterns
