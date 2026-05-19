"""Sensor platform voor de Ecoforest warmtepomp."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfEnergy,
    UnitOfPower,
    UnitOfPressure,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ANALOG_SENSORS,
    ANALOG_SETPOINTS,
    DEFAULT_NAME,
    DOMAIN,
    INTEGER_SENSORS,
    MONTHLY_ENERGY_SENSORS,
)
from .coordinator import EcoforestCoordinator

_LOGGER = logging.getLogger(__name__)

# Mapping van eenheid-string naar HA unit constanten
_UNIT_MAP = {
    "°C": UnitOfTemperature.CELSIUS,
    "bar": UnitOfPressure.BAR,
    "kW": UnitOfPower.KILO_WATT,
    "kWh": UnitOfEnergy.KILO_WATT_HOUR,
    "%": "%",
    "rpm": "rpm",
    None: None,
}

_DEVICE_CLASS_MAP = {
    "temperature": SensorDeviceClass.TEMPERATURE,
    "pressure": SensorDeviceClass.PRESSURE,
    "power": SensorDeviceClass.POWER,
    "energy": SensorDeviceClass.ENERGY,
    None: None,
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: EcoforestCoordinator = hass.data[DOMAIN][entry.entry_id]
    name = entry.data.get("name", DEFAULT_NAME)
    entities: list[EcoforestSensor] = []

    # Analog sensoren (read-only)
    for addr, (friendly, unit, dev_class, icon) in ANALOG_SENSORS.items():
        entities.append(
            EcoforestAnalogSensor(coordinator, entry, addr, friendly, unit, dev_class, icon, name)
        )

    # Analog setpoints ook als sensor (zodat huidige waarde zichtbaar is)
    for addr, (friendly, min_v, max_v, step, unit) in ANALOG_SETPOINTS.items():
        entities.append(
            EcoforestAnalogSensor(
                coordinator, entry, addr, f"{friendly} (huidig)", unit,
                "temperature", "mdi:target", name
            )
        )

    # Integer sensoren
    for addr, (friendly, unit, dev_class, icon) in INTEGER_SENSORS.items():
        entities.append(
            EcoforestIntegerSensor(coordinator, entry, addr, friendly, unit, dev_class, icon, name)
        )

    # Maandelijkse energietellers
    for addr, (friendly, unit, dev_class, icon) in MONTHLY_ENERGY_SENSORS.items():
        entities.append(
            EcoforestIntegerSensor(coordinator, entry, addr, friendly, unit, dev_class, icon, name)
        )

    async_add_entities(entities)


class EcoforestBaseSensor(CoordinatorEntity, SensorEntity):
    """Basisklasse voor Ecoforest sensoren."""

    def __init__(
        self,
        coordinator: EcoforestCoordinator,
        entry: ConfigEntry,
        address: int,
        friendly_name: str,
        unit: str | None,
        dev_class: str | None,
        icon: str,
        device_name: str,
    ) -> None:
        super().__init__(coordinator)
        self._address = address
        self._attr_name = f"{device_name} {friendly_name}"
        self._attr_unique_id = f"{entry.entry_id}_sensor_{address}"
        self._attr_icon = icon
        self._attr_native_unit_of_measurement = _UNIT_MAP.get(unit, unit)
        self._attr_device_class = _DEVICE_CLASS_MAP.get(dev_class)
        self._attr_state_class = (
            SensorStateClass.TOTAL_INCREASING
            if dev_class == "energy"
            else SensorStateClass.MEASUREMENT
        )
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=device_name,
            manufacturer="Ecoforest",
            model="ecoAIR",
        )


class EcoforestAnalogSensor(EcoforestBaseSensor):
    """Sensor voor analog registers (waarde / 10)."""

    @property
    def native_value(self) -> float | None:
        return self.coordinator.get_analog(self._address)


class EcoforestIntegerSensor(EcoforestBaseSensor):
    """Sensor voor integer registers (raw waarde)."""

    @property
    def native_value(self) -> int | None:
        return self.coordinator.get_integer(self._address)
