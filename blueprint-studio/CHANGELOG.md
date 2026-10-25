# Changelog

## 3.0.12

- Fix Ingress service worker registration and WebSocket unknown command handling:
  - Guarded PWA Service Worker registration in `panel_custom.html` to skip when running inside Home Assistant Ingress, eliminating the 404 script failure for `/blueprint_studio/service-worker.js`.
  - Fixed `_subscribeToUpdates` in `api.js` to gracefully fall back to background polling immediately when Home Assistant Core returns `unknown_command` for `blueprint_studio/subscribe_updates` (as expected in Supervisor Add-on mode), removing the 5 retry warnings and unhandled promise rejection.

## 3.0.11

- Fix terminal library loading and dynamic assets path under Home Assistant Ingress:
  - Added `ASSETS_BASE` constant adapting dynamic vendor asset paths (`xterm`, `xterm-addon-fit`, `diff_match_patch`, `codemirror/merge`, `acorn`, `prettier`, `pdfjs`) to Ingress route `${_ingress}/assets`.
  - Fixed xterm CSS and JavaScript resource paths in `terminal.js` which were previously hardcoded to `/blueprint_studio/assets/...`, causing 404 errors and `Failed to load terminal libraries: undefined`.
  - Fixed `loadScript` in `utils.js` to reject with an informative `Error` instance (`Failed to load script: <url>`) rather than a raw DOM `Event` with undefined message.
  - Added mock `hass.auth.async_get_user` adapter to `HomeAssistant` class in `core.py` preventing ticket user lookup errors.
  - Added Ingress proxy `X-Forwarded-Proto`, `X-Forwarded-Host`, and `X-Ingress-Path` origin tolerance to `api_terminal.py`.
  - Converted `material-icons.woff2` CSS font urls to relative paths.

## 3.0.10

- Fix file loading and JSON response parsing in Home Assistant Ingress:
  - Fixed `fetchWithAuth` in `api.js` to properly await and parse `.json()` responses when running inside Ingress. Previously, an early return handed back raw `Response` objects causing `result.folders` to be undefined.
  - Added defensive guards across `FileCoordinator.js` and `file-tree.js` (`Array.isArray(result?.folders)`, `Array.isArray(result?.files)`) to prevent `TypeError: Cannot read properties of undefined (reading 'forEach')`.
  - Added safe error and status code verification (`result?.error || result?.success === false`) for directory and file listing requests.

## 3.0.9

- Comprehensive Home Assistant Core integration and Supervisor compatibility fixes:
  - Added `hassio_api: true` and `hassio_role: "manager"` permissions in `config.yaml` to unlock Supervisor system API endpoints.
  - Added native Configuration Check via Supervisor Core Check (`/core/api/config/core/check_config` and `/core/check`) replacing broken CLI checks.
  - Added live Home Assistant Core version detection dynamically from `/core/info`.
  - Added installed add-ons retrieval from Supervisor API (`/addons`).
  - Added Home Assistant restart support via Supervisor API (`/core/restart`).
  - Added shims for `homeassistant.components.device_automation`, `conversation`, and `hassio`.
  - Added `self.loop`, `add_job`, `async_add_job`, and `async_create_task` to `HomeAssistant` class to prevent unhandled loop/scheduling attribute errors.
  - Fixed `device_registry` identifiers/connections attributes so device listings never crash with `AttributeError`.
  - Fixed `entity_registry` `domain`, `original_name`, and `unique_id` attributes.
  - Added full selector definitions to `selector.py` matching Home Assistant standard selectors.
  - Expanded YAML reloading to support `homeassistant.reload_core_config` and `homeassistant.reload_all`.
  - Added frontend live sync for `floors`, `labels`, `services`, and WebSocket device triggers/actions.

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
