# Changelog

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
