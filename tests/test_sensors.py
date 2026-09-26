"""Tests for sensor grouping."""

from collections import defaultdict

from generate_pages.sensors import group_sensors


class TestGroupSensors:
    def test_empty(self) -> None:
        g = group_sensors([])
        assert g["cpu_cores"] == []
        assert g["cpu_all"] == {}
        assert g["memory"] == {}

    def test_cpu_cores(self) -> None:
        ids = ["cpu/cpu0/usage", "cpu/cpu1/usage", "cpu/cpu0/frequency"]
        g = group_sensors(ids)
        assert "cpu/cpu0/usage" in g["cpu_cores"]
        assert "cpu/cpu1/usage" in g["cpu_cores"]
        assert "cpu/cpu0/frequency" in g["cpu_cores"]
        assert len(g["cpu_cores"]) == 3

    def test_cpu_all(self) -> None:
        ids = ["cpu/all/usage", "cpu/all/averageFrequency"]
        g = group_sensors(ids)
        assert "cpu/all/usage" in g["cpu_all"]
        assert "cpu/all/averageFrequency" in g["cpu_all"]

    def test_memory(self) -> None:
        ids = ["memory/physical/used", "memory/physical/free"]
        g = group_sensors(ids)
        assert "memory/physical/used" in g["memory"]
        assert "memory/physical/free" in g["memory"]

    def test_swap(self) -> None:
        ids = ["memory/swap/used"]
        g = group_sensors(ids)
        assert "memory/swap/used" in g["swap"]

    def test_disk_per(self) -> None:
        ids = ["disk/abc123/used", "disk/abc123/read", "disk/def456/used"]
        g = group_sensors(ids)
        assert "abc123" in g["disk_per"]
        assert "def456" in g["disk_per"]
        assert len(g["disk_per"]["abc123"]) == 2

    def test_disk_all(self) -> None:
        ids = ["disk/all/used"]
        g = group_sensors(ids)
        assert "disk/all/used" in g["disk_all"]

    def test_net_per(self) -> None:
        ids = ["network/wlan0/download", "network/eth0/download"]
        g = group_sensors(ids)
        assert "wlan0" in g["net_per"]
        assert "eth0" in g["net_per"]

    def test_net_all(self) -> None:
        ids = ["network/all/totalDownload"]
        g = group_sensors(ids)
        assert "network/all/totalDownload" in g["net_all"]

    def test_gpu(self) -> None:
        ids = ["gpu/gpu0/usage", "gpu/gpu1/temperature"]
        g = group_sensors(ids)
        assert "gpu0" in g["gpu"]
        assert "gpu1" in g["gpu"]
        assert g["gpu"]["gpu0"]["usage"] == "gpu/gpu0/usage"
        assert g["gpu"]["gpu1"]["temperature"] == "gpu/gpu1/temperature"

    def test_lmsensors(self) -> None:
        ids = ["lmsensors/coretemp/temp1"]
        g = group_sensors(ids)
        assert "lmsensors/coretemp/temp1" in g["lmsensors"]

    def test_power(self) -> None:
        ids = ["power/BAT0/charge"]
        g = group_sensors(ids)
        assert "power/BAT0/charge" in g["power"]

    def test_os(self) -> None:
        ids = ["os/kernel/hostname"]
        g = group_sensors(ids)
        assert "os/kernel/hostname" in g["os"]

    def test_sorted_cores(self) -> None:
        ids = ["cpu/cpu3/usage", "cpu/cpu1/usage", "cpu/cpu0/usage"]
        g = group_sensors(ids)
        assert g["cpu_cores"] == [
            "cpu/cpu0/usage",
            "cpu/cpu1/usage",
            "cpu/cpu3/usage",
        ]
