"""Tests for i18n module."""

from generate_pages.i18n import set_lang, t


class TestT:
    def setup_method(self) -> None:
        set_lang("fr")

    def test_french_default(self) -> None:
        assert t("page.cpu") == "Processeur"

    def test_english_override(self) -> None:
        assert t("page.cpu", lang="en") == "CPU"

    def test_missing_key_returns_key(self) -> None:
        assert t("nonexistent.key") == "nonexistent.key"

    def test_formatting(self) -> None:
        # sensor.cpu.core = "Cœur" in fr.json (no {n} placeholder)
        result = t("sensor.cpu.core", lang="fr")
        assert "Cœur" in result

    def test_formatting_with_placeholder(self) -> None:
        # test with a key that has a placeholder — use key fallback
        result = t("nonexistent {n}", n=3)
        assert "nonexistent 3" in result


class TestSetLang:
    def test_set_english(self) -> None:
        set_lang("en")
        assert t("page.cpu") == "CPU"
        set_lang("fr")

    def test_set_french(self) -> None:
        set_lang("en")
        set_lang("fr")
        assert t("page.cpu") == "Processeur"
