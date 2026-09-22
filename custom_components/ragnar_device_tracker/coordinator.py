"""Coordinator for Ragnar network scans."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from aiohttp import ClientError
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_IGNORE_MACS,
    CONF_MISSED_SCANS,
    CONF_SCAN_INTERVAL,
    CONF_URL,
    DOMAIN,
    UPDATE_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)


class RagnarDataUpdateCoordinator(DataUpdateCoordinator[dict[str, dict[str, Any]]]):
    """Fetch scan results and track consecutive successful misses."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.entry = entry
        self._known_hosts: dict[str, dict[str, Any]] = {}
        self._missed_scans: dict[str, int] = {}
        self._session = async_get_clientsession(hass)
        interval = entry.options.get(CONF_SCAN_INTERVAL, entry.data.get(CONF_SCAN_INTERVAL))
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL if interval is None else timedelta(seconds=interval),
        )

    async def _async_update_data(self) -> dict[str, dict[str, Any]]:
        """Request one scan and update host availability."""
        url = self.entry.options.get(CONF_URL, self.entry.data[CONF_URL])
        try:
            async with self._session.get(url, ssl=False) as response:
                response.raise_for_status()
                payload = await response.json()
        except (ClientError, ValueError) as err:
            raise UpdateFailed(f"Unable to fetch Ragnar scan: {err}") from err

        if not payload.get("success", False) or not isinstance(payload.get("hosts"), dict):
            raise UpdateFailed("Ragnar returned an unsuccessful or invalid scan")

        ignored_macs = {
            mac.strip().lower()
            for mac in self.entry.options.get(
                CONF_IGNORE_MACS, self.entry.data.get(CONF_IGNORE_MACS, "")
            ).split(",")
            if mac.strip()
        }
        current_hosts = {
            ip: host
            for ip, host in payload["hosts"].items()
            if isinstance(host, dict)
            and str(host.get("mac", "")).strip().lower() not in ignored_macs
        }
        for ip in set(self._known_hosts) - set(current_hosts):
            if ip in payload["hosts"]:
                self._known_hosts.pop(ip)
                self._missed_scans.pop(ip, None)

        for ip, host in current_hosts.items():
            if not isinstance(host, dict):
                continue
            host = {**host, "ip": host.get("ip", ip)}
            self._known_hosts[ip] = host
            self._missed_scans[ip] = 0

        threshold = self.entry.options.get(
            CONF_MISSED_SCANS, self.entry.data.get(CONF_MISSED_SCANS, 2)
        )
        for ip in self._known_hosts:
            if ip not in current_hosts:
                self._missed_scans[ip] = self._missed_scans.get(ip, 0) + 1

        return {
            ip: {**host, "available": self._missed_scans.get(ip, 0) < threshold}
            for ip, host in self._known_hosts.items()
        }