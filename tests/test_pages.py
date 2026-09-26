"""Tests for page generators."""

from collections import defaultdict
from typing import Any

from generate_pages.pages import GENERATORS
from generate_pages.pages.cpu import generate as cpu_gen
from generate_pages.pages.memory import generate as mem_gen
from generate_pages.pages.disks import generate as disk_gen
from generate_pages.pages.network import generate as net_gen
from generate_pages.pages.gpu import generate as gpu_gen
from generate_pages.pages.power import generate as power_gen
from generate_pages.pages.os import generate as os_gen
from generate_pages.pages.overview import generate as overview_gen
from generate_pages.pages.temperatures import generate as temp_gen


def _empty_groups() -> dict[str, Any]:
    return {
        "cpu_cores": [],
        "cpu_all": {},
        "memory": {},
        "swap": {},
        "disk_all": {},
        "disk_per": defaultdict(set),
        "net_all": {},
        "net_per": defaultdict(set),
        "gpu": defaultdict(dict),
        "lmsensors": {},
        "power": {},
        "os": {},
    }


class TestCpuGenerator:
    def test_returns_none_without_sensors(self) -> None:
        g = _empty_groups()
        assert cpu_gen(g) is None

    def test_generates_with_cores(self) -> None:
        g = _empty_groups()
        g["cpu_cores"] = ["cpu/cpu0/usage", "cpu/cpu1/usage"]
        result = cpu_gen(g)
        assert result is not None
        assert "[page]" in result
        assert "cpu/cpu\\\\d+/usage" in result

    def test_generates_with_lang_en(self) -> None:
        g = _empty_groups()
        g["cpu_cores"] = ["cpu/cpu0/usage"]
        result = cpu_gen(g, lang="en")
        assert result is not None
        assert "CPU" in result


class TestMemoryGenerator:
    def test_returns_none_without_sensors(self) -> None:
        g = _empty_groups()
        assert mem_gen(g) is None

    def test_generates_with_memory(self) -> None:
        g = _empty_groups()
        g["memory"] = {"memory/physical/usedPercent": True}
        result = mem_gen(g)
        assert result is not None
        assert "[page]" in result
        assert "memory/physical/usedPercent" in result

    def test_includes_swap_when_available(self) -> None:
        g = _empty_groups()
        g["memory"] = {"memory/physical/usedPercent": True}
        g["swap"] = {"memory/swap/usedPercent": True}
        result = mem_gen(g)
        assert result is not None
        assert "memory/swap/usedPercent" in result


class TestDisksGenerator:
    def test_returns_none_without_sensors(self) -> None:
        g = _empty_groups()
        assert disk_gen(g) is None

    def test_generates_with_disk_all(self) -> None:
        g = _empty_groups()
        g["disk_all"] = {"disk/all/read": True, "disk/all/write": True}
        result = disk_gen(g)
        assert result is not None
        assert "[page]" in result


class TestNetworkGenerator:
    def test_returns_none_without_sensors(self) -> None:
        g = _empty_groups()
        assert net_gen(g) is None

    def test_generates_with_interface(self) -> None:
        g = _empty_groups()
        g["net_per"]["wlan0"] = {"network/wlan0/download", "network/wlan0/upload"}
        result = net_gen(g)
        assert result is not None
        assert "[page]" in result


class TestGpuGenerator:
    def test_returns_none_without_sensors(self) -> None:
        g = _empty_groups()
        assert gpu_gen(g) is None

    def test_generates_with_gpu(self) -> None:
        g = _empty_groups()
        g["gpu"]["gpu0"] = {"usage": "gpu/gpu0/usage"}
        result = gpu_gen(g)
        assert result is not None
        assert "[page]" in result


class TestPowerGenerator:
    def test_returns_none_without_sensors(self) -> None:
        g = _empty_groups()
        assert power_gen(g) is None

    def test_generates_with_power(self) -> None:
        g = _empty_groups()
        g["power"]["power/BAT0/charge"] = True
        g["power"]["power/BAT0/voltage"] = True
        result = power_gen(g)
        assert result is not None
        assert "[page]" in result


class TestOsGenerator:
    def test_returns_none_without_sensors(self) -> None:
        g = _empty_groups()
        assert os_gen(g) is None

    def test_generates_with_os(self) -> None:
        g = _empty_groups()
        g["os"]["os/kernel/hostname"] = True
        result = os_gen(g)
        assert result is not None
        assert "[page]" in result


class TestOverviewGenerator:
    def test_returns_none_without_sensors(self) -> None:
        g = _empty_groups()
        assert overview_gen(g) is None

    def test_generates_with_cpu(self) -> None:
        g = _empty_groups()
        g["cpu_all"]["cpu/all/usage"] = True
        result = overview_gen(g)
        assert result is not None
        assert "[page]" in result
        assert "cpu/all/usage" in result

    def test_includes_multiple_sections(self) -> None:
        g = _empty_groups()
        g["cpu_all"]["cpu/all/usage"] = True
        g["memory"]["memory/physical/used"] = True
        g["net_per"]["wlan0"] = {"network/wlan0/download"}
        result = overview_gen(g)
        assert result is not None
        assert result.count("piechart") >= 2


class TestTemperaturesGenerator:
    def test_returns_none_without_sensors(self) -> None:
        g = _empty_groups()
        assert temp_gen(g) is None

    def test_generates_with_cpu(self) -> None:
        g = _empty_groups()
        g["cpu_all"]["cpu/all/averageTemperature"] = True
        result = temp_gen(g)
        assert result is not None
        assert "[page]" in result

    def test_generates_with_lmsensors(self) -> None:
        g = _empty_groups()
        g["lmsensors"]["lmsensors/coretemp/temp1"] = True
        result = temp_gen(g)
        assert result is not None
        assert "[page]" in result


class TestGeneratorRegistry:
    def test_all_generators_registered(self) -> None:
        assert len(GENERATORS) == 9
        assert "Page.page" in GENERATORS
        assert "CPU.page" in GENERATORS
        assert "Memoire.page" in GENERATORS
        assert "Disques.page" in GENERATORS
        assert "Reseau.page" in GENERATORS
        assert "GPU.page" in GENERATORS
        assert "Temperatures.page" in GENERATORS
        assert "Alimentation.page" in GENERATORS
        assert "Systeme.page" in GENERATORS

    def test_all_generators_callable(self) -> None:
        g = _empty_groups()
        for fname, gen in GENERATORS.items():
            result = gen(g)
            assert result is None  # empty groups = no output
