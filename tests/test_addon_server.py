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
