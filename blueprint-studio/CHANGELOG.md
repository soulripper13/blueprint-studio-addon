# Changelog

## 3.0.8

- Fix entity states and attributes in Developer Tools:
  - Added live state update before `get_entities` queries (`hass.states.async_update_states`).
  - Added S6 container environment token loader (`/run/s6/container_environment/SUPERVISOR_TOKEN`) to guarantee authenticated access to Supervisor Core API.
  - Added dual fallback reading `.storage/core.restore_state` and `.storage/core.entity_registry` so entities always retain their last known states and attributes even when offline.
  - Added live frontend state and attribute merging with parent Home Assistant UI (`window.parent.document.querySelector("home-assistant").hass.states`).
  - Fixed Developer Tools template rendering with Jinja2 engine and Supervisor `/api/template` proxy.
  - Fixed action/service runner keyword argument handling (`target`, `blocking`, `return_response`).

## 3.0.7

- Fix Home Assistant entity and action autocomplete in Add-on:
  - Added live entity state retrieval and service discovery via Supervisor Core API (`SUPERVISOR_TOKEN`).
  - Added full entity registry, device registry, area registry, floor registry, and label registry storage fallbacks.
  - Added frontend live state bridge to synchronize with parent Home Assistant iframe.

## 3.0.6

- Fix Ingress authentication bypass: bypass standalone PWA login prompt when loaded through Home Assistant Ingress so users enter directly into the workspace without a redundant login prompt.

## 3.0.5

- Add support for user-configurable workspace directory (`home_dir`) in the add-on Configuration tab (`/homeassistant`, `/share`, `/media`, `/ssl`, or any custom project subfolder).
- Add new wide banner logo (`logo.png`) tailored for the Home Assistant Add-on information page.
- Add rich `README.md` to the add-on directory for the Home Assistant Add-on information page overview.
- Add English translation (`translations/en.yaml`) for clean configuration UI labels.
- Map `/media:rw` in `config.yaml` to allow managing media files.

## 3.0.4

- Fix Home Assistant configuration directory mapping: correctly prioritize `/homeassistant` mapped by Supervisor `homeassistant_config:rw` with backwards-compatible `/config` symlink.
- Normalize path resolution so `/config`, `/homeassistant`, and relative paths all resolve safely to the managed Home Assistant configuration directory.
- Set terminal environment `HOME` and initial working directory to `/homeassistant`.

## 3.0.3

- Initial release of Blueprint Studio as an official Home Assistant Supervisor Add-on.
- Full Ingress integration with Home Assistant sidebar support.
- Mounted `/config` workspace with live YAML editing and Blueprint creation.
- Built-in Git version control, SFTP file management, and interactive terminal.
- AI Copilot with multi-provider support.
