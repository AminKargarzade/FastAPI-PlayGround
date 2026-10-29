# 🌐 Multi-Language Support for FastAPI

## Overview

This exercise implements multi-language support in a FastAPI application using **GNU gettext** and **Babel**.

The application supports English (`en`) and Persian (`fa`). The response language can be selected through a query parameter or negotiated using the `Accept-Language` HTTP header.

The implementation is designed to keep translation logic centralized and reusable across API endpoints.

## Features

- **Multiple languages:** English and Persian.
- **Query parameter support:** Select a language using `?lang=en` or `?lang=fa`.
- **HTTP header negotiation:** Detect the preferred supported language from `Accept-Language`.
- **Default language:** Fall back to English when no supported language is selected.
- **Reusable translation dependency:** Inject the appropriate translator into FastAPI endpoints using `Depends`.
- **Compiled translations:** Use `.po` source files and compiled `.mo` catalogs.
- **Cached translators:** Reuse translator instances through `functools.lru_cache`.
- **Centralized translation files:** Keep language-specific messages separate from application logic.

## Project Structure

```text
FastAPI-PlayGround/
├── core/
│   ├── main.py
│   ├── i18n/
│   │   ├── __init__.py
│   │   ├── translator.py
│   │   └── dependencies.py
│   ├── locales/
│   │   ├── en/
│   │   │   └── LC_MESSAGES/
│   │   │       ├── messages.po
│   │   │       └── messages.mo
│   │   └── fa/
│   │       └── LC_MESSAGES/
│   │           ├── messages.po
│   │           └── messages.mo
│   ├── expenses/
│   │   └── routes.py
│   └── users/
│       └── routes.py
├── requirements.txt
└── README.md
```

The tree above highlights the files relevant to internationalization. Other application modules, models, schemas, authentication components, and database files are omitted for brevity.

## Requirements

- Python 3.10 or newer
- pip
- The project's existing dependencies listed in `requirements.txt`

Babel must also be installed. If it is not already listed, add the following to `requirements.txt`:

```text
Babel==2.18.0
```

## Setup Guide

Follow these steps to run the project on a new machine.

### 1. Clone the repository

```bash
git clone <REPOSITORY_URL>
cd FastAPI-PlayGround
```

Replace `<REPOSITORY_URL>` with the actual Git repository URL.

### 2. Create a virtual environment

**Windows (PowerShell):**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Linux / macOS:**

```bash
python3 -m venv venv
source venv/bin/activate
```

If PowerShell blocks script execution, use an approved execution-policy configuration or activate the environment using another supported method.

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Compile translation catalogs

The `.po` files contain human-readable translations. FastAPI's translation dependency loads the compiled `.mo` files at runtime.

From the repository root, run:

```bash
python -m babel.messages.frontend compile --directory=core/locales --domain=messages
```

This command compiles the translation catalogs for the supported languages.

**Important:** Whenever you modify a `.po` file, compile the catalogs again so the changes become available to the running application.

If your repository already includes up-to-date `.mo` files, recompilation is still a useful verification step.

### 5. Configure the application

Before running the application, check the project's configuration and environment variables.

If the application requires a database URL, authentication secrets, or other environment-specific settings, configure them according to the existing project setup.

Do not commit real credentials or secret keys to version control.

### 6. Start the application

Run the following command from the repository root:

```bash
uvicorn main:app --reload --app-dir core
```

The application should be available at:

- API base URL: `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`
- Health endpoint: `http://127.0.0.1:8000/health`

If you run Uvicorn from inside the `core` directory instead, use:

```bash
uvicorn main:app --reload
```

## Selecting a Language

The language resolver supports two mechanisms.

### Option 1: Query parameter

You can explicitly select the response language using the `lang` query parameter.

**English:**

```http
GET /health?lang=en
```

Expected response:

```json
{
  "message": "Service is healthy"
}
```

**Persian:**

```http
GET /health?lang=fa
```

Expected response:

```json
{
  "message": "سرویس سالم است"
}
```

An unsupported language such as `lang=de` falls back to the default language, English, under the current implementation.

### Option 2: Accept-Language header

If the `lang` query parameter is not provided, the application checks the `Accept-Language` header.

For example:

```http
GET /health
Accept-Language: fa
```

The response message will be in Persian.

You can also provide language preferences and quality values:

```http
Accept-Language: de;q=0.9, fa;q=0.8, en;q=0.7
```

The resolver considers language preferences and selects a supported language. If no supported language is available, it falls back to English.

The primary language subtag is used, so language tags such as `fa-IR` can resolve to `fa`.

## Using Translations in Endpoints

The translation dependency can be injected into a route using FastAPI's dependency system.

For example:

```python
from gettext import NullTranslations
from typing import Annotated

from fastapi import Depends

from i18n.dependencies import get_language


@app.get("/health")
def health_check(
    translator: Annotated[NullTranslations, Depends(get_language)],
):
    return {
        "message": translator.gettext("Service is healthy")
    }
```

The `get_language` dependency resolves the requested language and returns the corresponding translator.

The `gettext()` method looks up the supplied message in the active translation catalog. If a translation is unavailable, the fallback configuration allows the original message to be returned.

For other routes, inject the same dependency and use it for user-facing messages:

```python
translator.gettext("Expense not found")
```

This keeps translation handling consistent across the application.

## Adding a New Translation

To add or update a translated message:

1. Add the message to the relevant `messages.po` files.
2. Set the appropriate `msgstr` value for each supported language.
3. Compile the translation catalogs again.
4. Restart or reload the application if necessary.
5. Test the affected endpoint in each supported language.

Example Persian entry:

```po
msgid "Expense not found"
msgstr "هزینه پیدا نشد"
```

Keep the English source message (`msgid`) consistent across translation catalogs so the same key resolves correctly in every language.

## Testing

Use the following checklist to verify the implementation:

- [ ] `/health?lang=en` returns an English message.
- [ ] `/health?lang=fa` returns a Persian message.
- [ ] An unsupported language falls back to English.
- [ ] The `Accept-Language` header selects a supported language when `lang` is omitted.
- [ ] Authentication messages are translated in both languages.
- [ ] Expense error messages, including `Expense not found`, are translated.
- [ ] Newly added translations work after recompiling the catalogs.
- [ ] Existing API response schemas and authentication behavior remain unchanged.

**Note:** Protected endpoints require valid authentication. When testing their responses, authenticate first so that authorization errors do not prevent you from reaching the behavior being tested.

## Implementation Notes

- `core/i18n/translator.py` defines supported languages, the default language, the locale directory, and cached translator instances.
- `core/i18n/dependencies.py` resolves the language from the query parameter or request headers and exposes the translator through a FastAPI dependency.
- `core/locales/` stores language-specific translation catalogs.
- `.po` files are the editable translation sources.
- `.mo` files are the compiled catalogs loaded at runtime.

## Scope

This exercise focuses on translating user-facing API messages. It does not translate JSON field names, user-provided data, or every part of the Swagger documentation.

The implementation currently supports English and Persian. Additional languages can be introduced by extending the supported-language configuration and adding their corresponding translation catalogs.

---

**Exercise:** Multi-Language Support Capability  
**Framework:** FastAPI  
**Translation tools:** GNU gettext and Babel  
**Supported languages:** English (`en`), Persian (`fa`)
