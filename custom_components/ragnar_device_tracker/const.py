"""Constants for the Ragnar Device Tracker integration."""

from __future__ import annotations

from datetime import timedelta

DOMAIN = "ragnar_device_tracker"
NAME = "Ragnar Device Tracker"
VERSION = "0.1.0"
DEFAULT_URL = ""
DEFAULT_SCAN_INTERVAL = 60
DEFAULT_MISSED_SCANS = 2
DEFAULT_NAME_FORMAT = "{hostname} | {vendor} | {ip} | {mac}"
CONF_URL = "url"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_MISSED_SCANS = "missed_scans"
CONF_NAME_FORMAT = "name_format"
CONF_IGNORE_MACS = "ignore_macs"
UPDATE_INTERVAL = timedelta(seconds=DEFAULT_SCAN_INTERVAL)
PLATFORMS = ["device_tracker"]