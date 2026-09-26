"""Internationalization (i18n) module.

Loads translations from JSON files in generate_pages/i18n/.
Default language is French. Automatic fallback if a key is missing.

Usage:
    from .i18n import set_lang, t
    set_lang("en")  # optional, "fr" by default
    print(t("page.cpu"))  # "Processeur" or "CPU"
    print(t("sensor.cpu.core", lang="en"))  # "Core"
    print(t("sensor.cpu.core", n=3))  # "Cœur 3"
"""

import json
import os

_DIR = os.path.dirname(__file__)

_current_lang: str = "fr"
_cache: dict[str, dict[str, str]] = {}


def set_lang(lang: str) -> None:
    """Set the active language and load its translations.

    Translations are cached to avoid re-reading JSON on every t() call.

    Args:
        lang: Language code ("fr" or "en" for now).
    """
    global _current_lang
    _current_lang = lang
    _load(lang)


def _load(lang: str) -> dict[str, str]:
    """Load and cache translations for a given language."""
    if lang in _cache:
        return _cache[lang]
    path = os.path.join(_DIR, f"{lang}.json")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            _cache[lang] = json.load(f)
    else:
        _cache[lang] = {}
    return _cache[lang]


def t(key: str, lang: str | None = None, **kwargs: object) -> str:
    """Return the translation for the given key.

    If the key doesn't exist in the target language, returns the key itself.
    Supports formatting: t("sensor.cpu.core", n=3) -> "Cœur 3".

    Args:
        key: Translation key (e.g. "page.cpu").
        lang: Language override (None = active language via set_lang).
        **kwargs: Optional formatting parameters.

    Returns:
        Translated string, or the key if absent.
    """
    store = _load(lang or _current_lang)
    value = store.get(key, key)
    if kwargs:
        try:
            return value.format(**kwargs)
        except (KeyError, IndexError):
            return value
    return value
