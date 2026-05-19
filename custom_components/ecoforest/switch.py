"""Switch platform voor de Ecoforest warmtepomp."""
from __future__ import annotations

import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import COIL_SENSORS, DEFAULT_NAME, DOMAIN, WRITABLE_COILS
from .coordinator import EcoforestCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: EcoforestCoordinator = hass.data[DOMAIN][entry.entry_id]
    name = entry.data.get("name", DEFAULT_NAME)
    entities = []

    for addr in WRITABLE_COILS:
        if addr not in COIL_SENSORS:
            continue
        friendly, icon, _ = COIL_SENSORS[addr]
        entities.append(
            EcoforestSwitch(coordinator, entry, addr, friendly, icon, name)
        )

    async_add_entities(entities)


class EcoforestSwitch(CoordinatorEntity, SwitchEntity):
    """Schakelaar voor een schrijfbare Modbus coil (bijv. warmtepomp aan/uit)."""

    def __init__(
        self,
        coordinator: EcoforestCoordinator,
        entry: ConfigEntry,
        address: int,
        friendly_name: str,
        icon: str,
        device_name: str,
    ) -> None:
        super().__init__(coordinator)
        self._address = address
        self._attr_name = f"{device_name} {friendly_name}"
        self._attr_unique_id = f"{entry.entry_id}_switch_{address}"
        self._attr_icon = icon
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=device_name,
            manufacturer="Ecoforest",
            model="ecoAIR",
        )

    @property
    def is_on(self) -> bool | None:
        return self.coordinator.get_coil(self._address)

    async def async_turn_on(self, **kwargs) -> None:
        try:
            await self.coordinator.async_write_coil(self._address, True)
        except RuntimeError as err:
            _LOGGER.error("Kan warmtepomp niet inschakelen: %s", err)

    async def async_turn_off(self, **kwargs) -> None:
        try:
            await self.coordinator.async_write_coil(self._address, False)
        except RuntimeError as err:
            _LOGGER.error("Kan warmtepomp niet uitschakelen: %s", err)
