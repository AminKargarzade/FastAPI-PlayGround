from typing import Annotated

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
    """
    Resolve the request language.

    Priority:
    1. Query parameter: ?lang=fa
    2. Accept-Language header
    3. Default language
    """
    if lang is not None:
        normalized = lang.strip().lower()

        if normalized in SUPPORTED_LANGUAGES:
            return normalized

        return DEFAULT_LANGUAGE

    accept_language = request.headers.get("Accept-Language", "")

    # Parse language tags and their optional quality values.
    candidates = []

    for item in accept_language.split(","):
        parts = item.strip().split(";")
        language_tag = parts[0].strip().lower()

        if not language_tag:
            continue

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

        candidates.append((language_tag, quality))

    # Prefer higher quality values, preserving header order for ties.
    candidates.sort(key=lambda item: item[1], reverse=True)

    for language_tag, quality in candidates:
        if quality == 0:
            continue

        # Support tags such as fa-IR and en-US.
        primary_language = language_tag.split("-")[0]

        if primary_language in SUPPORTED_LANGUAGES:
            return primary_language

    return DEFAULT_LANGUAGE


def get_language(
    language: Annotated[str, Depends(resolve_language)],
):
    """Provide a translator for the selected request language."""
    return get_translator(language)
