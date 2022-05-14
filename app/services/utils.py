import re
from typing import Any, Pattern

from bson import ObjectId
from bson.errors import InvalidId


def compile_case_sensitive(pattern: str,
                           ignorecase: bool = True,
                           match_whole_word: bool = False) -> Pattern[str]:
    return re.compile(
        fr'^{re.escape(pattern)}$' if match_whole_word else re.escape(pattern),
        re.IGNORECASE if ignorecase else 0
    )


def compile_case_sensitive_dict(patterns: dict[str, Any],
                                ignorecase: bool = True,
                                match_whole_word: bool = False) -> dict[str, Any | Pattern[str]]:
    patterns = patterns.copy()

    for key, value in patterns.items():
        try:
            patterns[key] = ObjectId(value)

        except (TypeError, InvalidId):
            if isinstance(value, str):
                patterns[key] = compile_case_sensitive(pattern=value,
                                                       ignorecase=ignorecase,
                                                       match_whole_word=match_whole_word)

    return patterns
