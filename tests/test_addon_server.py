"""Tests for Blueprint Studio Supervisor Add-on standalone server."""
import pytest
from pathlib import Path
from aiohttp import web
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop

import sys
APP_DIR = Path(__file__).resolve().parents[1] / "blueprint-studio" / "app"
sys.path.insert(0, str(APP_DIR))

from server import init_app, IngressUser, VERSION


class TestAddonServer(AioHTTPTestCase):
    async def get_application(self):
        self.tmp_config = Path("/tmp/bs_addon_test_config").resolve()
        self.tmp_config.mkdir(parents=True, exist_ok=True)
        self.tmp_data = Path("/tmp/bs_addon_test_data").resolve()
        self.tmp_data.mkdir(parents=True, exist_ok=True)
        return await init_app(self.tmp_config, self.tmp_data)

    async def tearDownAsync(self):
        import shutil
        shutil.rmtree(self.tmp_config, ignore_errors=True)
        shutil.rmtree(self.tmp_data, ignore_errors=True)

    @unittest_run_loop
    async def test_health_check(self):
        resp = await self.client.get("/health")
        self.assertEqual(resp.status, 200)
        data = await resp.json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["version"], VERSION)
        self.assertTrue(data["ingress"])

    @unittest_run_loop
    async def test_ingress_index_injection(self):
        resp = await self.client.get(
            "/",
            headers={"X-Ingress-Path": "/api/hassio_ingress/TEST_TOKEN"}
        )
        self.assertEqual(resp.status, 200)
        text = await resp.text()
        self.assertIn("window.__BS_INGRESS_PATH__ = '/api/hassio_ingress/TEST_TOKEN';", text)
        self.assertIn(f"window.__BS_VERSION__ = '{VERSION}';", text)
        self.assertIn("/api/hassio_ingress/TEST_TOKEN/assets/", text)

    @unittest_run_loop
    async def test_file_operations_api(self):
        # 1. Write file
        write_resp = await self.client.post(
            "/api",
            json={
                "action": "write_file",
                "path": "test.yaml",
                "content": "key: value\n"
            }
        )
        self.assertEqual(write_resp.status, 200)
        write_data = await write_resp.json()
        self.assertTrue(write_data.get("success"))

        # 2. List files
        list_resp = await self.client.get("/api?action=list_files")
        self.assertEqual(list_resp.status, 200)
        files = await list_resp.json()
        self.assertTrue(any(f["name"] == "test.yaml" for f in files))

        # 3. Read file
        read_resp = await self.client.get("/api?action=read_file&path=test.yaml")
        self.assertEqual(read_resp.status, 200)
        read_data = await read_resp.json()
        self.assertIn("key: value", read_data.get("content", ""))

        # 4. Read file with /config/ prefix
        read_config_resp = await self.client.get("/api?action=read_file&path=/config/test.yaml")
        self.assertEqual(read_config_resp.status, 200)
        self.assertIn("key: value", (await read_config_resp.json()).get("content", ""))

        # 5. Read file with /homeassistant/ prefix
        read_ha_resp = await self.client.get("/api?action=read_file&path=/homeassistant/test.yaml")
        self.assertEqual(read_ha_resp.status, 200)
        self.assertIn("key: value", (await read_ha_resp.json()).get("content", ""))

        # 6. Entity metadata test via storage
        storage_dir = self.tmp_config / ".storage"
        storage_dir.mkdir(parents=True, exist_ok=True)
        (storage_dir / "core.entity_registry").write_text(
            '{"data": {"entities": [{"entity_id": "sensor.living_room_temperature", "name": "Living Room Temp", "device_class": "temperature"}]}}'
        )
        meta_resp = await self.client.get("/api?action=get_metadata")
        self.assertEqual(meta_resp.status, 200)
        meta_data = await meta_resp.json()
        self.assertTrue(any(e["entity_id"] == "sensor.living_room_temperature" for e in meta_data.get("entities", [])))

    @unittest_run_loop
    async def test_get_entities_with_attributes_and_restore_state(self):
        storage_dir = self.tmp_config / ".storage"
        storage_dir.mkdir(parents=True, exist_ok=True)
        # 1. Populate restore_state with live attributes
        (storage_dir / "core.restore_state").write_text(
            '{"data": [{"state": {"entity_id": "sensor.kitchen_temperature", "state": "23.5", "attributes": {"friendly_name": "Kitchen Temperature", "device_class": "temperature", "unit_of_measurement": "°C"}}}]}'
        )
        # 2. Populate entity_registry
        (storage_dir / "core.entity_registry").write_text(
            '{"data": {"entities": [{"entity_id": "sensor.kitchen_temperature", "name": "Kitchen Temperature", "device_class": "temperature"}, {"entity_id": "light.kitchen", "name": "Kitchen Light"}]}}'
        )

        resp = await self.client.post(
            "/api",
            json={"action": "get_entities", "with_attributes": True, "force_refresh": True}
        )
        self.assertEqual(resp.status, 200)
        data = await resp.json()
        entities = data.get("entities", [])
        sensor = next((e for e in entities if e["entity_id"] == "sensor.kitchen_temperature"), None)
        self.assertIsNotNone(sensor)
        self.assertEqual(sensor["state"], "23.5")
        self.assertEqual(sensor["device_class"], "temperature")
        self.assertIn("attributes", sensor)
        self.assertEqual(sensor["attributes"].get("unit_of_measurement"), "°C")

    @unittest_run_loop
    async def test_render_template(self):
        resp = await self.client.post(
            "/api",
            json={"action": "render_template", "template": "Result: {{ 5 + 7 }}"}
        )
        self.assertEqual(resp.status, 200)
        data = await resp.json()
        self.assertTrue(data.get("success"))
        self.assertEqual(data.get("result"), "Result: 12")

    @unittest_run_loop
    async def test_call_service_target_handling(self):
        resp = await self.client.post(
            "/api",
            json={
                "action": "call_service",
                "domain": "light",
                "service": "turn_on",
                "target": {"entity_id": "light.kitchen"},
                "service_data": {"brightness": 255}
            }
        )
        self.assertEqual(resp.status, 200)
        data = await resp.json()
        self.assertTrue(data.get("success"))

    @unittest_run_loop
    async def test_device_registry_and_device_automations(self):
        storage_dir = self.tmp_config / ".storage"
        storage_dir.mkdir(parents=True, exist_ok=True)
        (storage_dir / "core.device_registry").write_text(
            '{"data": {"devices": [{"id": "dev123", "name": "Smart Switch", "identifiers": [["esphome", "aa:bb:cc:dd"]]}]}}'
        )
        resp = await self.client.get("/api?action=get_devices")
        self.assertEqual(resp.status, 200)
        data = await resp.json()
        self.assertTrue(data.get("success"))
        devices = data.get("devices", [])
        self.assertTrue(any(d["id"] == "dev123" and d["integration"] == "esphome" for d in devices))

        # Test get_device_automations
        auto_resp = await self.client.post(
            "/api",
            json={"action": "get_device_automations", "device_id": "dev123"}
        )
        self.assertEqual(auto_resp.status, 200)
        auto_data = await auto_resp.json()
        self.assertTrue(auto_data.get("success"))
        self.assertIn("automations", auto_data)

    @unittest_run_loop
    async def test_reload_yaml_and_config_check(self):
        # 1. Test reload_yaml
        reload_resp = await self.client.post(
            "/api",
            json={"action": "reload_yaml", "domain": "automation"}
        )
        self.assertEqual(reload_resp.status, 200)
        self.assertTrue((await reload_resp.json()).get("success"))

        # 2. Test run_config_check
        check_resp = await self.client.get("/api?action=run_config_check")
        self.assertEqual(check_resp.status, 200)
        check_data = await check_resp.json()
        self.assertTrue(check_data.get("success"))
        self.assertIn("result", check_data)

    @unittest_run_loop
    async def test_xterm_static_assets_and_terminal_ticket(self):
        # 1. Verify xterm static assets are served properly
        js_resp = await self.client.get("/assets/vendor/xterm/xterm.js")
        self.assertEqual(js_resp.status, 200)
        js_text = await js_resp.text()
        self.assertIn("Terminal", js_text)

        css_resp = await self.client.get("/assets/vendor/xterm/xterm.css")
        self.assertEqual(css_resp.status, 200)

        # 2. Verify connection ticket issuance for terminal
        ticket_resp = await self.client.post(
            "/api",
            json={"action": "issue_connection_ticket", "ticket_action": "terminal"}
        )
        self.assertEqual(ticket_resp.status, 200)
        ticket_data = await ticket_resp.json()
        self.assertTrue(ticket_data.get("success"))
        self.assertIn("ticket", ticket_data)
        ticket = ticket_data["ticket"]

        # 3. Verify terminal ws accepts the ticket
        ws = await self.client.ws_connect(
            f"/api/terminal_ws?ticket={ticket}",
            headers={"Origin": f"http://{self.client.host}:{self.client.port}"}
        )
        self.assertFalse(ws.closed)
        await ws.close()
