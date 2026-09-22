"""Config flow for Ragnar Device Tracker."""

from __future__ import annotations

import voluptuous as vol
from aiohttp import ClientError
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    CONF_IGNORE_MACS,
    CONF_MISSED_SCANS,
    CONF_NAME_FORMAT,
    CONF_SCAN_INTERVAL,
    CONF_URL,
    DEFAULT_MISSED_SCANS,
    DEFAULT_NAME_FORMAT,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_URL,
    DOMAIN,
)


async def _validate_url(hass: HomeAssistant, url: str) -> None:
    """Verify that the endpoint returns a valid scan."""
    session = async_get_clientsession(hass)
    async with session.get(url, ssl=False) as response:
        response.raise_for_status()
        payload = await response.json()
    if not payload.get("success") or not isinstance(payload.get("hosts"), dict):
        raise ValueError("invalid response")


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle integration setup."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial setup form."""
        errors = {}
        if user_input is not None:
            try:
                await _validate_url(self.hass, user_input[CONF_URL])
            except (ClientError, ValueError):
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(title="Ragnar Device Tracker", data=user_input)

        schema = vol.Schema(
            {
                vol.Required(CONF_URL, default=DEFAULT_URL): str,
                vol.Required(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(
                    vol.Coerce(int), vol.Range(min=10)
                ),
                vol.Required(CONF_MISSED_SCANS, default=DEFAULT_MISSED_SCANS): vol.All(
                    vol.Coerce(int), vol.Range(min=1)
                ),
                vol.Optional(CONF_IGNORE_MACS, default=""): str,
                vol.Required(CONF_NAME_FORMAT, default=DEFAULT_NAME_FORMAT): str,
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @staticmethod
    def async_get_options_flow(config_entry):
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Allow settings to be changed after setup."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        values = {**self.config_entry.data, **self.config_entry.options}
        schema = vol.Schema(
            {
                vol.Required(CONF_URL, default=values.get(CONF_URL, DEFAULT_URL)): str,
                vol.Required(CONF_SCAN_INTERVAL, default=values.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)): vol.All(vol.Coerce(int), vol.Range(min=10)),
                vol.Required(CONF_MISSED_SCANS, default=values.get(CONF_MISSED_SCANS, DEFAULT_MISSED_SCANS)): vol.All(vol.Coerce(int), vol.Range(min=1)),
                vol.Optional(CONF_IGNORE_MACS, default=values.get(CONF_IGNORE_MACS, "")): str,
                vol.Required(CONF_NAME_FORMAT, default=values.get(CONF_NAME_FORMAT, DEFAULT_NAME_FORMAT)): str,
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)