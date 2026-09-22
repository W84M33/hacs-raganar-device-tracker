# Ragnar Device Tracker

Home Assistant custom integration that polls Ragnar's Nmap ping endpoint and exposes each discovered host as a `device_tracker` entity.

## Install with HACS

1. Add this repository as a custom repository in HACS under **Integrations**.
2. Install **Ragnar Device Tracker**.
3. Restart Home Assistant.
4. Add the integration from **Settings > Devices & services**.

## Configuration

The setup form accepts:

- **Endpoint URL**: the URL of the Ragnar Nmap ping endpoint. It can be changed later from the integration's Options screen.
- **Scan interval**: seconds between scans, at least 10.
- **Missed scans before away**: consecutive successful scans where a host is absent. The default is 2.
- **MAC addresses to omit**: optional comma-separated MAC addresses that should not become device trackers. Matching is case-insensitive.
- **Name format**: supports `{hostname}`, `{vendor}`, `{ip}`, and `{mac}`. The default is `{hostname} | {vendor} | {ip} | {mac}`. Empty fields are removed from the displayed name.

Certificate verification is disabled for the endpoint connection to support local HTTPS services with self-signed certificates. Use a trusted network and endpoint.

Each entity exposes the scan fields as extra state attributes. A failed scan does not mark devices away; only successful scans that omit a previously discovered host count toward the away threshold.
