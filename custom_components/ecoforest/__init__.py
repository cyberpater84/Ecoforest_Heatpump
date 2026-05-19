"""Ecoforest warmtepomp integratie voor Home Assistant."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, Platform
from homeassistant.core import HomeAssistant

from .const import CONF_SLAVE, CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL, DOMAIN
from .coordinator import EcoforestCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR, Platform.SWITCH, Platform.NUMBER, Platform.BINARY_SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Zet de Ecoforest integratie op vanuit een config entry."""
    scan_interval = entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

    coordinator = EcoforestCoordinator(
        hass=hass,
        host=entry.data[CONF_HOST],
        port=entry.data[CONF_PORT],
        slave=entry.data[CONF_SLAVE],
        scan_interval=scan_interval,
    )

    # Eerste data-ophaal; gooit ConfigEntryNotReady bij verbindingsfout
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Herlaad bij opties-wijziging (bijv. scan interval aangepast)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Verwijder de integratie."""
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        coordinator: EcoforestCoordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.async_close()
    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Herlaad de integratie wanneer opties veranderen."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
