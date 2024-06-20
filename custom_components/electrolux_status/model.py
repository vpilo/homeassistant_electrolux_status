"""Define Electrolux Status data models."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ElectroluxDevice:
    """Define class for main domain information."""

    capability_info: dict[str, any] = field(default_factory=dict)  # 0
    category: str | None = None  # 1
    device_class: str | None = None  # 2
    unit: str | None = None  # 3
    entity_category: str | None = None  # 4
    entity_icon: str | None = None  # 5
