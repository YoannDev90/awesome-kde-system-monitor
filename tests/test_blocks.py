"""Tests for KConfig block generators."""

from generate_pages.blocks import (
    blk_appearance,
    blk_colors,
    blk_facegrid,
    blk_labels,
    blk_linechart,
    blk_page,
    blk_piechart,
    blk_row,
    blk_sensors,
    blk_textonly,
    blk_title_row,
)
from generate_pages.i18n import set_lang


class TestBlkAppearance:
    def setup_method(self) -> None:
        set_lang("fr")

    def test_basic(self) -> None:
        result = blk_appearance(2101, "org.kde.ksysguard.linechart",
                                "face.cpu.total_usage", "fr")
        assert "[Face-2101][Appearance]" in result
        assert "chartFace=org.kde.ksysguard.linechart" in result
        assert "Title=Utilisation totale" in result
        assert "Title[en]=Total usage" in result

    def test_no_title(self) -> None:
        result = blk_appearance(2101, "org.kde.ksysguard.linechart",
                                "face.cpu.total_usage", "fr", show_title=False)
        assert "showTitle=false" in result


class TestBlkSensors:
    def test_basic(self) -> None:
        result = blk_sensors(2101, ["cpu/cpu0/usage", "cpu/cpu1/usage"])
        assert "highPrioritySensorIds=[\"cpu/cpu0/usage\",\"cpu/cpu1/usage\"]" in result
        assert "lowPrioritySensorIds=[]" in result


class TestBlkColors:
    def test_basic(self) -> None:
        result = blk_colors(2101, {"cpu/all/usage": (41, 128, 185)})
        assert "[Face-2101][SensorColors]" in result
        assert "cpu/all/usage=41,128,185" in result


class TestBlkLabels:
    def test_basic(self) -> None:
        result = blk_labels(2101, {"cpu/all/usage": "Total"})
        assert "[Face-2101][SensorLabels]" in result
        assert "cpu/all/usage=Total" in result


class TestBlkLinechart:
    def test_defaults(self) -> None:
        result = blk_linechart(2101)
        assert "historyAmount=300" in result
        assert "lineChartFillOpacity=20" in result
        assert "rangeAutoY=true" in result

    def test_override(self) -> None:
        result = blk_linechart(2101, rangeAutoY="false", rangeFromY=0)
        assert "rangeAutoY=false" in result
        assert "rangeFromY=0" in result


class TestBlkTextonly:
    def test_default(self) -> None:
        result = blk_textonly(2101)
        assert "groupByTotal=false" in result

    def test_group(self) -> None:
        result = blk_textonly(2101, group=True)
        assert "groupByTotal=true" in result


class TestBlkFacegrid:
    def test_basic(self) -> None:
        result = blk_facegrid(2101, ncols=4)
        assert "columnCount=4" in result
        assert "historyAmount=120" in result


class TestBlkPiechart:
    def test_basic(self) -> None:
        result = blk_piechart(2101)
        assert "showLegend=true" in result


class TestBlkPage:
    def setup_method(self) -> None:
        set_lang("fr")

    def test_basic(self) -> None:
        result = blk_page("page.cpu", "cpu", "fr")
        assert "[page]" in result
        assert "Title=Processeur" in result
        assert "Title[en]=CPU" in result
        assert "icon=cpu" in result
        assert "loadType=ondemand" in result


class TestBlkTitleRow:
    def setup_method(self) -> None:
        set_lang("fr")

    def test_basic(self) -> None:
        result = blk_title_row("page.cpu", "fr")
        assert "[page][row-0]" in result
        assert "Title=Processeur" in result
        assert "isTitle=true" in result


class TestBlkRow:
    def test_single_face(self) -> None:
        result = blk_row(1, [2101])
        assert "[page][row-1]" in result
        assert "face=Face-2101" in result
        assert "column-0" in result

    def test_two_faces(self) -> None:
        result = blk_row(2, [2101, 2102])
        assert "column-0" in result
        assert "column-1" in result
        assert "face=Face-2101" in result
        assert "face=Face-2102" in result
