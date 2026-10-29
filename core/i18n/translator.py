import gettext
from functools import lru_cache
from pathlib import Path

SUPPORTED_LANGUAGES = {"en", "fa"}
DEFAULT_LANGUAGE = "en"

LOCALES_DIR = Path(__file__).resolve().parents[1] / "locales"


@lru_cache(maxsize=len(SUPPORTED_LANGUAGES))
def get_translator(language: str) -> gettext.NullTranslations:
    if language not in SUPPORTED_LANGUAGES:
        language = DEFAULT_LANGUAGE

    return gettext.translation(
        domain="messages",
        localedir=LOCALES_DIR,
        languages=[language],
        fallback=True,
    )
