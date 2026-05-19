"""Binary sensor platform voor de Ecoforest warmtepomp."""
from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import COIL_SENSORS, DEFAULT_NAME, DOMAIN, WRITABLE_COILS
from .coordinator import EcoforestCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: EcoforestCoordinator = hass.data[DOMAIN][entry.entry_id]
    name = entry.data.get("name", DEFAULT_NAME)
    entities = []

    for addr, (friendly, icon, invert) in COIL_SENSORS.items():
        # Coil 180 is schrijfbaar => wordt Switch, niet BinarySensor
        if addr in WRITABLE_COILS:
            continue
        entities.append(
            EcoforestBinarySensor(coordinator, entry, addr, friendly, icon, invert, name)
        )

    async_add_entities(entities)


class EcoforestBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Read-only binaire sensor gebaseerd op een Modbus coil."""

    def __init__(
        self,
        coordinator: EcoforestCoordinator,
        entry: ConfigEntry,
        address: int,
        friendly_name: str,
        icon: str,
        invert: bool,
        device_name: str,
    ) -> None:
        super().__init__(coordinator)
        self._address = address
        self._invert = invert
        self._attr_name = f"{device_name} {friendly_name}"
        self._attr_unique_id = f"{entry.entry_id}_binary_{address}"
        self._attr_icon = icon
        # Alarmstatus krijgt device class 'problem'
        self._attr_device_class = (
            BinarySensorDeviceClass.PROBLEM if invert else None
        )
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=device_name,
            manufacturer="Ecoforest",
            model="ecoAIR",
        )

    @property
    def is_on(self) -> bool | None:
        raw = self.coordinator.get_coil(self._address)
        if raw is None:
            return None
        return (not raw) if self._invert else raw
