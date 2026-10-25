"""Standalone Ingress Web Server for Blueprint Studio Supervisor Add-on."""
from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import sys
from pathlib import Path

from aiohttp import web

# Set up paths so app and backend can be imported
APP_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(APP_DIR))

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store
from backend.file_manager import FileManager
from backend.git_manager import GitManager
from backend.ai_manager import AIManager
from backend.sftp_manager import SftpManager
from backend.terminal_manager import TerminalManager
from backend.operation_tracker import OperationTracker
from backend.reliability import OperationCoordinator
from backend.ticket_manager import TicketManager
from backend.ha_metadata import HAMetadataManager
from backend.api import BlueprintStudioApiView, BlueprintStudioStreamView, BlueprintStudioUploadView
from backend.api_terminal import TerminalWebSocketView

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
_LOGGER = logging.getLogger("blueprint_studio_server")


def load_version() -> str:
    manifest_path = APP_DIR / "manifest.json"
    if manifest_path.is_file():
        try:
            return json.loads(manifest_path.read_text(encoding="utf-8")).get("version", "3.0.3")
        except Exception:
            pass
    return "3.0.3"


VERSION = load_version()


class IngressUser:
    id = "ingress_user"
    name = "Home Assistant Admin"
    is_admin = True


async def init_app(config_dir: Path, data_dir: Path) -> web.Application:
    """Initialize the aiohttp application with all Blueprint Studio routes."""
    @web.middleware
    async def cache_control_middleware(request: web.Request, handler):
        response = await handler(request)
        if request.path.startswith(("/assets", "/blueprint_studio/assets", "/api")):
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        return response

    app = web.Application(
        client_max_size=1024 * 1024 * 500,  # 500MB upload limit
        middlewares=[cache_control_middleware],
    )

    hass = HomeAssistant(str(config_dir))
    app["hass"] = hass
    store = Store(hass, 2, "blueprint_studio_data")
    data = await store.async_load() or {}

    file_manager = FileManager(hass, config_dir)
    metadata_manager = HAMetadataManager(hass)
    git_manager = GitManager(hass, config_dir, data, store)
    ai_manager = AIManager(hass, data, file_manager, metadata_manager)
    sftp_manager = SftpManager(config_dir)
    terminal_manager = TerminalManager(hass)
    operations = OperationTracker()
    tickets = TicketManager()
    coordinator = OperationCoordinator()

    api_view = BlueprintStudioApiView(
        config_dir,
        store,
        data,
        git=git_manager,
        ai=ai_manager,
        file=file_manager,
        sftp=sftp_manager,
        terminal=terminal_manager,
        operations=operations,
        tickets=tickets,
        coordinator=coordinator,
        metadata=metadata_manager,
    )
    api_view.activate(
        store, data, git_manager, ai_manager, file_manager, sftp_manager,
        terminal_manager, operations, tickets, coordinator, metadata_manager
    )

    stream_view = BlueprintStudioStreamView(file_manager, sftp_manager, operations, tickets)
    stream_view.activate(file_manager, sftp_manager, operations, tickets)

    upload_view = BlueprintStudioUploadView(file_manager, sftp_manager, operations)
    upload_view.activate(file_manager, sftp_manager, operations)

    terminal_view = TerminalWebSocketView(terminal_manager, tickets)
    terminal_view.activate(terminal_manager, tickets)

    panel_html_path = APP_DIR / "www" / "panels" / "panel_custom.html"
    www_dir = APP_DIR / "www"

    async def serve_index(request: web.Request) -> web.Response:
        """Serve the main Blueprint Studio HTML panel configured for Ingress."""
        ingress_path = request.headers.get("X-Ingress-Path", "").rstrip("/")
        if not panel_html_path.is_file():
            return web.Response(status=404, text="Panel HTML not found")

        content = panel_html_path.read_text(encoding="utf-8")
        content = content.replace("{{VERSION}}", VERSION)

        # Adapt assets path to Ingress
        asset_prefix = f"{ingress_path}/assets" if ingress_path else "/assets"
        content = content.replace("/blueprint_studio/assets", asset_prefix)

        # Inject Ingress configuration script before </head>
        ingress_script = (
            f"<script>\n"
            f"  window.__BS_INGRESS_PATH__ = '{ingress_path}';\n"
            f"  window.__BS_VERSION__ = '{VERSION}';\n"
            f"</script>\n"
        )
        content = content.replace("</head>", f"{ingress_script}</head>")

        return web.Response(
            text=content,
            content_type="text/html",
            headers={
                "Cache-Control": "no-store, max-age=0",
                "Pragma": "no-cache",
                "Expires": "0",
            },
        )

    async def handle_api_post(request: web.Request) -> web.Response:
        if "hass_user" not in request:
            request["hass_user"] = IngressUser()
        return await api_view.post(request)

    async def handle_api_get(request: web.Request) -> web.Response:
        if "hass_user" not in request:
            request["hass_user"] = IngressUser()
        return await api_view.get(request)

    async def handle_stream_get(request: web.Request) -> web.StreamResponse:
        return await stream_view.get(request)

    async def handle_upload_post(request: web.Request) -> web.Response:
        return await upload_view.post(request)

    async def handle_terminal_ws(request: web.Request) -> web.WebSocketResponse:
        return await terminal_view.get(request)

    async def handle_health(request: web.Request) -> web.Response:
        return web.json_response({"status": "ok", "version": VERSION, "ingress": True})

    # Register routes
    app.router.add_get("/", serve_index)
    app.router.add_get("/panel", serve_index)
    app.router.add_get("/index.html", serve_index)
    app.router.add_get("/health", handle_health)

    # API routes (standard and namespaced for compatibility)
    for prefix in ("/api", "/api/blueprint_studio"):
        app.router.add_post(prefix, handle_api_post)
        app.router.add_get(prefix, handle_api_get)
        app.router.add_get(f"{prefix}/stream", handle_stream_get)
        app.router.add_post(f"{prefix}/upload", handle_upload_post)
        app.router.add_get(f"{prefix}/terminal_ws", handle_terminal_ws)

    # Static assets routes
    app.router.add_static("/assets", str(www_dir))
    app.router.add_static("/blueprint_studio/assets", str(www_dir))

    return app


def main() -> None:
    parser = argparse.ArgumentParser(description="Blueprint Studio Standalone Server")
    parser.add_argument("--port", type=int, default=8099, help="Port to listen on")
    parser.add_argument(
        "--config-dir",
        type=str,
        default=None,
        help="Home Assistant config directory",
    )
    parser.add_argument("--data-dir", type=str, default="/data", help="Add-on persisted data directory")
    args = parser.parse_args()

    data_path = Path(args.data_dir).resolve()

    # Determine config directory
    config_dir_str = args.config_dir
    if not config_dir_str:
        options_file = data_path / "options.json"
        if options_file.is_file():
            try:
                with open(options_file, encoding="utf-8") as f:
                    opt = json.load(f)
                    user_dir = opt.get("home_dir") or opt.get("config_dir")
                    if user_dir and os.path.isdir(user_dir):
                        config_dir_str = user_dir
                        _LOGGER.info("Using configured home_dir from options.json: %s", user_dir)
            except Exception as err:
                _LOGGER.warning("Could not read options.json: %s", err)

    def _has_ha_config(d: str) -> bool:
        return os.path.isfile(os.path.join(d, "configuration.yaml"))

    def _dir_has_files(d: str) -> bool:
        try:
            return os.path.isdir(d) and len(os.listdir(d)) > 0
        except OSError:
            return False

    # Auto-detect Home Assistant configuration directory if default or not set
    if not config_dir_str or config_dir_str in ("/homeassistant", "/config"):
        if _has_ha_config("/homeassistant"):
            config_dir_str = "/homeassistant"
        elif _has_ha_config("/config"):
            config_dir_str = "/config"
        elif _dir_has_files("/homeassistant"):
            config_dir_str = "/homeassistant"
        elif _dir_has_files("/config"):
            config_dir_str = "/config"
        else:
            config_dir_str = "/homeassistant" if os.path.isdir("/homeassistant") else "/config"

    config_path = Path(config_dir_str).resolve()

    if not config_path.is_dir():
        _LOGGER.warning("Config directory %s does not exist, creating it", config_path)
        config_path.mkdir(parents=True, exist_ok=True)

    os.environ["HOME"] = str(config_path)

    _LOGGER.info("Starting Blueprint Studio Add-on v%s on port %d", VERSION, args.port)
    _LOGGER.info("Configuration directory: %s", config_path)
    _LOGGER.info("Data directory: %s", data_path)

    app = asyncio.run(init_app(config_path, data_path))
    web.run_app(app, port=args.port, host="0.0.0.0")


if __name__ == "__main__":
    main()
