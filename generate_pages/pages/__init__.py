"""Page generator registry.

Each generator has the signature:
    generate(groups, lang="fr") -> str | None

groups: dict returned by group_sensors()
lang:   language code ("fr" or "en")
Return: .page content or None if insufficient sensors.
"""

from collections.abc import Callable

from . import cpu, disks, gpu, memory, network, temperatures

GENERATORS: dict[str, Callable[..., str | None]] = {
    "CPU.page": cpu.generate,
    "Memoire.page": memory.generate,
    "Disques.page": disks.generate,
    "Reseau.page": network.generate,
    "GPU.page": gpu.generate,
    "Temperatures.page": temperatures.generate,
}
