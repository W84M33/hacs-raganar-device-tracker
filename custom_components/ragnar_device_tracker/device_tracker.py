"""Device tracker entities for Ragnar scan hosts."""

from __future__ import annotations

from homeassistant.components.device_tracker import SOURCE_TYPE_ROUTER, TrackerEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_NAME_FORMAT, DEFAULT_NAME_FORMAT, DOMAIN
from .coordinator import RagnarDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Create entities as hosts are discovered."""
    coordinator: RagnarDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    added: set[str] = set()

    def add_discovered() -> None:
        new_entities = [
            RagnarDevice(coordinator, ip)
            for ip in coordinator.data
            if ip not in added
        ]
        if new_entities:
            added.update(entity.ip_address for entity in new_entities)
            async_add_entities(new_entities)

    add_discovered()
    coordinator.async_add_listener(add_discovered)


class RagnarDevice(CoordinatorEntity[RagnarDataUpdateCoordinator], TrackerEntity):
    """A discovered Ragnar host."""

    _attr_source_type = SOURCE_TYPE_ROUTER

    def __init__(self, coordinator: RagnarDataUpdateCoordinator, ip: str) -> None:
        super().__init__(coordinator)
        self.ip_address = ip
        self._attr_unique_id = f"{DOMAIN}_{ip}"

    @property
    def _host(self) -> dict:
        return self.coordinator.data.get(self.ip_address, {})

    @property
    def name(self) -> str:
        host = self._host
        values = {
            "hostname": host.get("hostname", ""),
            "vendor": host.get("vendor", ""),
            "ip": host.get("ip", self.ip_address),
            "mac": host.get("mac", ""),
        }
        name_format = self.coordinator.entry.options.get(
            CONF_NAME_FORMAT,
            self.coordinator.entry.data.get(CONF_NAME_FORMAT, DEFAULT_NAME_FORMAT),
        )
        try:
            formatted_name = name_format.format(**values)
        except (KeyError, ValueError):
            formatted_name = DEFAULT_NAME_FORMAT.format(**values)
        return " | ".join(part.strip() for part in formatted_name.split("|") if part.strip())

    @property
    def is_connected(self) -> bool:
        return bool(self._host.get("available", False))

    @property
    def extra_state_attributes(self) -> dict[str, str]:
        return {
            key: value
            for key, value in self._host.items()
            if key not in {"available", "status"} and value not in (None, "")
        }