"""Tests for kconfig escaping helpers."""

from generate_pages.kconfig import kk, kp


class TestKp:
    def test_no_backslash(self) -> None:
        assert kp("cpu/all/usage") == "cpu/all/usage"

    def test_single_backslash(self) -> None:
        # kp: 1 input \ → 4 output \
        result = kp(r"cpu/cpu\d+/usage")
        assert result.count("\\") == 4
        assert "d+/usage" in result

    def test_double_backslash(self) -> None:
        # kp: 2 input \ → 8 output \
        result = kp(r"cpu/cpu\\d+/usage")
        assert result.count("\\") == 8

    def test_lookahead(self) -> None:
        result = kp(r"network/(?!all).*/download")
        assert "(?!" in result


class TestKk:
    def test_no_backslash(self) -> None:
        assert kk("cpu/all/usage") == "cpu/all/usage"

    def test_single_backslash(self) -> None:
        # kk: 1 input \ → 2 output \
        result = kk(r"cpu/cpu\d+/usage")
        assert result.count("\\") == 2
        assert "d+/usage" in result

    def test_lookahead(self) -> None:
        result = kk(r"network/(?!all).*/download")
        assert "(?!" in result
