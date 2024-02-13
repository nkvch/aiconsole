from typing import Annotated

from pydantic import StringConstraints

LanguageStr = Annotated[
    str, StringConstraints(strip_whitespace=True, to_lower=True, pattern=r"^(python|applescript|react_ui)$")
]
