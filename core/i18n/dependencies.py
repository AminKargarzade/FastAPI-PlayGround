from typing import Annotated
from gettext import NullTranslations

from fastapi import Depends, Query, Request

from i18n.translator import (
    DEFAULT_LANGUAGE,
    SUPPORTED_LANGUAGES,
    get_translator,
)


def resolve_language(
    request: Request,
    lang: Annotated[str | None, Query()] = None,
) -> str:
    if lang is not None:
        normalized = lang.strip().lower()
        return normalized if normalized in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE

    accept_language = request.headers.get("Accept-Language", "")
    candidates = []

    for item in accept_language.split(","):
        parts = item.strip().split(";")
        language_tag = parts[0].strip().lower()
        quality = 1.0

        for parameter in parts[1:]:
            parameter = parameter.strip()
            if parameter.startswith("q="):
                try:
                    quality = float(parameter[2:])
                except ValueError:
                    quality = 0.0

        if not 0.0 <= quality <= 1.0:
            quality = 0.0

        if language_tag:
            candidates.append((language_tag, quality))

    candidates.sort(key=lambda item: item[1], reverse=True)

    for language_tag, quality in candidates:
        if quality == 0:
            continue

        primary_language = language_tag.split("-")[0]
        if primary_language in SUPPORTED_LANGUAGES:
            return primary_language

    return DEFAULT_LANGUAGE


def get_language(
    language: Annotated[str, Depends(resolve_language)],
) -> NullTranslations:
    return get_translator(language)
