"""Plugin contracts for future iterations."""

from dataclasses import dataclass, field
from typing import Protocol


class PluginCommand(Protocol):
    """A plugin command contract."""

    name: str

    def execute(self, payload: dict[str, str]) -> dict[str, str]:
        """Execute command and return output payload."""


@dataclass(slots=True)
class PluginRegistry:
    """In-memory plugin registry placeholder."""

    plugins: dict[str, PluginCommand] = field(default_factory=dict)

    def register(self, plugin: PluginCommand) -> None:
        self.plugins[plugin.name] = plugin
