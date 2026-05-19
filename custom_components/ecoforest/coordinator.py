"""DataUpdateCoordinator voor de Ecoforest warmtepomp integratie."""
from __future__ import annotations

import asyncio
import logging
from datetime import timedelta
from typing import Any

from pymodbus.client import AsyncModbusTcpClient
from pymodbus.exceptions import ModbusException

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    ANALOG_SENSORS,
    ANALOG_SETPOINTS,
    INTEGER_SENSORS,
    INTEGER_SETPOINTS,
    COIL_SENSORS,
    MONTHLY_ENERGY_SENSORS,
)

_LOGGER = logging.getLogger(__name__)

# Groepeer adressen in blokken om het aantal Modbus-requests te minimaliseren
# pymodbus leest max 125 registers per FC3-request
_MAX_REGS = 100


def _build_read_blocks(addresses: list[int]) -> list[tuple[int, int]]:
    """Maak aaneengesloten leesblokken van een gesorteerde adressenlijst.

    Retourneert lijst van (start_adres, count) tuples.
    Gaten van <=5 registers worden overgeslagen (minder requests, kleine overhead).
    """
    if not addresses:
        return []
    addresses = sorted(set(addresses))
    blocks: list[tuple[int, int]] = []
    start = addresses[0]
    end = addresses[0]
    for addr in addresses[1:]:
        if addr - end <= 5 and (end - start + 1) < _MAX_REGS:
            end = addr
        else:
            blocks.append((start, end - start + 1))
            start = addr
            end = addr
    blocks.append((start, end - start + 1))
    return blocks


class EcoforestCoordinator(DataUpdateCoordinator):
    """Beheert alle Modbus-communicatie met de Ecoforest warmtepomp."""

    def __init__(
        self,
        hass: HomeAssistant,
        host: str,
        port: int,
        slave: int,
        scan_interval: int,
    ) -> None:
        self.host = host
        self.port = port
        self.slave = slave
        self._client: AsyncModbusTcpClient | None = None
        self._lock = asyncio.Lock()

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )

    # ------------------------------------------------------------------
    # Verbindingsbeheer
    # ------------------------------------------------------------------

    async def _get_client(self) -> AsyncModbusTcpClient:
        if self._client is None or not self._client.connected:
            self._client = AsyncModbusTcpClient(host=self.host, port=self.port)
            await self._client.connect()
            if not self._client.connected:
                raise UpdateFailed(
                    f"Kan geen verbinding maken met Ecoforest op {self.host}:{self.port}"
                )
        return self._client

    async def async_close(self) -> None:
        """Sluit de Modbus-verbinding netjes."""
        if self._client and self._client.connected:
            self._client.close()

    # ------------------------------------------------------------------
    # Data ophalen
    # ------------------------------------------------------------------

    async def _async_update_data(self) -> dict[str, Any]:
        """Haal alle register-waarden op. Wordt door HA periodiek aangeroepen."""
        async with self._lock:
            try:
                client = await self._get_client()
                data: dict[str, Any] = {}

                # 1) Holding registers: Analog + Integer + maandelijkse energie
                holding_addrs = (
                    list(ANALOG_SENSORS.keys())
                    + list(ANALOG_SETPOINTS.keys())
                    + list(INTEGER_SENSORS.keys())
                    + list(INTEGER_SETPOINTS.keys())
                    + list(MONTHLY_ENERGY_SENSORS.keys())
                )
                for start, count in _build_read_blocks(holding_addrs):
                    result = await client.read_holding_registers(
                        address=start - 1,  # Ecoforest gebruikt 1-based adressen
                        count=count,
                        slave=self.slave,
                    )
                    if result.isError():
                        _LOGGER.warning(
                            "Modbus fout bij lezen registers %d-%d: %s",
                            start, start + count - 1, result,
                        )
                        continue
                    for offset, val in enumerate(result.registers):
                        data[f"hr_{start + offset}"] = val

                # 2) Coils
                coil_addrs = sorted(COIL_SENSORS.keys())
                for start, count in _build_read_blocks(coil_addrs):
                    result = await client.read_coils(
                        address=start - 1,
                        count=count,
                        slave=self.slave,
                    )
                    if result.isError():
                        _LOGGER.warning(
                            "Modbus fout bij lezen coils %d-%d: %s",
                            start, start + count - 1, result,
                        )
                        continue
                    for offset, val in enumerate(result.bits[:count]):
                        data[f"coil_{start + offset}"] = bool(val)

                return data

            except ModbusException as err:
                # Gooi verbinding weg zodat volgende poll opnieuw verbindt
                if self._client:
                    self._client.close()
                    self._client = None
                raise UpdateFailed(f"Modbus communicatiefout: {err}") from err

    # ------------------------------------------------------------------
    # Schrijfoperaties (aangeroepen door switch/number entities)
    # ------------------------------------------------------------------

    async def async_write_coil(self, address: int, value: bool) -> None:
        """Schrijf een enkele coil (FC5). Adres is 1-based (Ecoforest spec)."""
        async with self._lock:
            try:
                client = await self._get_client()
                result = await client.write_coil(
                    address=address - 1, value=value, slave=self.slave
                )
                if result.isError():
                    raise ModbusException(f"Schrijffout coil {address}: {result}")
                # Update lokale cache direct zodat UI niet hoeft te wachten op poll
                if self.data is not None:
                    self.data[f"coil_{address}"] = value
            except ModbusException as err:
                raise RuntimeError(f"Kan coil {address} niet schrijven: {err}") from err

    async def async_write_register(self, address: int, value: int) -> None:
        """Schrijf een enkel holding register (FC6). Adres is 1-based."""
        async with self._lock:
            try:
                client = await self._get_client()
                result = await client.write_register(
                    address=address - 1, value=value, slave=self.slave
                )
                if result.isError():
                    raise ModbusException(f"Schrijffout register {address}: {result}")
                if self.data is not None:
                    self.data[f"hr_{address}"] = value
            except ModbusException as err:
                raise RuntimeError(
                    f"Kan register {address} niet schrijven: {err}"
                ) from err

    # ------------------------------------------------------------------
    # Helper: waarden uit gecachede data ophalen
    # ------------------------------------------------------------------

    def get_analog(self, address: int) -> float | None:
        """Geeft analog waarde (register / 10)."""
        if self.data is None:
            return None
        raw = self.data.get(f"hr_{address}")
        if raw is None:
            return None
        # Ondertekend 16-bit (bijv. negatieve buitentemperatuur)
        if raw > 32767:
            raw -= 65536
        return round(raw / 10, 1)

    def get_integer(self, address: int) -> int | None:
        """Geeft integer registerwaarde."""
        if self.data is None:
            return None
        return self.data.get(f"hr_{address}")

    def get_coil(self, address: int) -> bool | None:
        """Geeft coil waarde."""
        if self.data is None:
            return None
        return self.data.get(f"coil_{address}")
