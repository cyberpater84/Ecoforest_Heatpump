"""Number platform voor de Ecoforest warmtepomp."""
from __future__ import annotations

import logging

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ANALOG_SETPOINTS,
    DEFAULT_NAME,
    DOMAIN,
    INTEGER_SETPOINTS,
)
from .coordinator import EcoforestCoordinator

_LOGGER = logging.getLogger(__name__)

# Demand-waarden als selectie-opties voor de integer setpoints
_DEMAND_OPTIONS = {
    5181: {0: "Uit", 1: "Aan"},
    5182: {0: "Uit", 1: "Aan"},
    5183: {0: "Geen vraag", 1: "Verwarmen", 2: "Koelen"},
    5184: {0: "Geen vraag", 1: "Verwarmen", 2: "Koelen"},
    5185: {0: "Geen vraag", 1: "Verwarmen", 2: "Koelen"},
    5188: {0: "Geen programma", 1: "Winter", 2: "Zomer"},
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: EcoforestCoordinator = hass.data[DOMAIN][entry.entry_id]
    name = entry.data.get("name", DEFAULT_NAME)
    entities: list[NumberEntity] = []

    # Analog setpoints (temperatuursetpoints via BUS)
    for addr, (friendly, min_v, max_v, step, unit) in ANALOG_SETPOINTS.items():
        entities.append(
            EcoforestAnalogNumber(
                coordinator, entry, addr, friendly, min_v, max_v, step, unit, name
            )
        )

    # Integer setpoints (demands en programma)
    for addr, (friendly, min_v, max_v, step) in INTEGER_SETPOINTS.items():
        entities.append(
            EcoforestIntegerNumber(
                coordinator, entry, addr, friendly, min_v, max_v, step, name
            )
        )

    async_add_entities(entities)


class EcoforestAnalogNumber(CoordinatorEntity, NumberEntity):
    """Temperatuursetpoint: raw waarde = instelling * 10."""

    def __init__(
        self,
        coordinator: EcoforestCoordinator,
        entry: ConfigEntry,
        address: int,
        friendly_name: str,
        min_val: float,
        max_val: float,
        step: float,
        unit: str,
        device_name: str,
    ) -> None:
        super().__init__(coordinator)
        self._address = address
        self._attr_name = f"{device_name} {friendly_name}"
        self._attr_unique_id = f"{entry.entry_id}_number_{address}"
        self._attr_native_min_value = min_val
        self._attr_native_max_value = max_val
        self._attr_native_step = step
        self._attr_native_unit_of_measurement = unit
        self._attr_mode = NumberMode.BOX
        self._attr_icon = "mdi:thermometer-lines"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=device_name,
            manufacturer="Ecoforest",
            model="ecoAIR",
        )

    @property
    def native_value(self) -> float | None:
        return self.coordinator.get_analog(self._address)

    async def async_set_native_value(self, value: float) -> None:
        raw = int(round(value * 10))
        try:
            await self.coordinator.async_write_register(self._address, raw)
        except RuntimeError as err:
            _LOGGER.error("Kan setpoint %d niet schrijven: %s", self._address, err)


class EcoforestIntegerNumber(CoordinatorEntity, NumberEntity):
    """Integer demand/programma register."""

    def __init__(
        self,
        coordinator: EcoforestCoordinator,
        entry: ConfigEntry,
        address: int,
        friendly_name: str,
        min_val: int,
        max_val: int,
        step: int,
        device_name: str,
    ) -> None:
        super().__init__(coordinator)
        self._address = address
        self._attr_name = f"{device_name} {friendly_name}"
        self._attr_unique_id = f"{entry.entry_id}_integer_{address}"
        self._attr_native_min_value = min_val
        self._attr_native_max_value = max_val
        self._attr_native_step = step
        self._attr_mode = NumberMode.SLIDER
        self._attr_icon = "mdi:tune"
        self._options = _DEMAND_OPTIONS.get(address, {})
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=device_name,
            manufacturer="Ecoforest",
            model="ecoAIR",
        )

    @property
    def native_value(self) -> int | None:
        return self.coordinator.get_integer(self._address)

    @property
    def extra_state_attributes(self) -> dict:
        """Voeg leesbare betekenis toe aan de waarde."""
        val = self.native_value
        if val is not None and self._options:
            return {"betekenis": self._options.get(val, str(val))}
        return {}

    async def async_set_native_value(self, value: float) -> None:
        try:
            await self.coordinator.async_write_register(self._address, int(value))
        except RuntimeError as err:
            _LOGGER.error("Kan register %d niet schrijven: %s", self._address, err)
