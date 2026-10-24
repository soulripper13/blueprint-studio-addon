# Changelog

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
