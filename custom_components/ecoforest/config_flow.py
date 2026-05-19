"""Config Flow voor de Ecoforest warmtepomp integratie."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from pymodbus.client import AsyncModbusTcpClient
from pymodbus.exceptions import ModbusException

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import (
    DOMAIN,
    DEFAULT_NAME,
    DEFAULT_PORT,
    DEFAULT_SLAVE,
    DEFAULT_SCAN_INTERVAL,
    CONF_SLAVE,
    CONF_SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_PORT, default=DEFAULT_PORT): vol.All(int, vol.Range(min=1, max=65535)),
        vol.Required(CONF_SLAVE, default=DEFAULT_SLAVE): vol.All(int, vol.Range(min=1, max=247)),
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
    }
)

OPTIONS_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(
            int, vol.Range(min=10, max=300)
        ),
    }
)


async def _test_connection(host: str, port: int, slave: int) -> str | None:
    """Test Modbus TCP verbinding. Retourneert foutmelding of None bij succes."""
    client = AsyncModbusTcpClient(host=host, port=port)
    try:
        await client.connect()
        if not client.connected:
            return "cannot_connect"
        # Lees één register om te bevestigen dat slave reageert
        result = await client.read_holding_registers(address=0, count=1, slave=slave)
        if result.isError():
            return "slave_not_responding"
        return None
    except ModbusException:
        return "cannot_connect"
    except Exception:  # noqa: BLE001
        return "unknown"
    finally:
        client.close()


class EcoforestConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow voor Ecoforest integratie."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            port = user_input[CONF_PORT]
            slave = user_input[CONF_SLAVE]

            # Unieke ID zodat je niet twee keer dezelfde pomp toevoegt
            await self.async_set_unique_id(f"{host}:{port}:{slave}")
            self._abort_if_unique_id_configured()

            error = await _test_connection(host, port, slave)
            if error:
                errors["base"] = error
            else:
                return self.async_create_entry(
                    title=user_input.get(CONF_NAME, DEFAULT_NAME),
                    data={
                        CONF_HOST: host,
                        CONF_PORT: port,
                        CONF_SLAVE: slave,
                        CONF_NAME: user_input.get(CONF_NAME, DEFAULT_NAME),
                    },
                    options={CONF_SCAN_INTERVAL: DEFAULT_SCAN_INTERVAL},
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_SCHEMA,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        return EcoforestOptionsFlow(config_entry)


class EcoforestOptionsFlow(config_entries.OptionsFlow):
    """Opties flow: poll-interval aanpassen zonder opnieuw toevoegen."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self._config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_interval = self._config_entry.options.get(
            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
        )
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_SCAN_INTERVAL, default=current_interval): vol.All(
                        int, vol.Range(min=10, max=300)
                    )
                }
            ),
        )
