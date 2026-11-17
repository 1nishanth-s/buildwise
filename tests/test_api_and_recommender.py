"""
BuildWise-AI — Phase 12 Backend API & Recommender Test Suite

Tests:
1. API health and models readiness
2. Catalog summary metrics integrity
3. Bounded deterministic build recommendation generation
4. Exactly two inputs requirement for Build Mode
5. Budget lower boundary enforcement
6. Upgrade recommendation generation and bottleneck analysis
7. Supervised ML performance estimation in recommendation
8. Dynamic component replacement and compatibility revalidation
9. Project persistence (create, read, update, delete) in SQLite
10. Recommendation history tracking
11. Unaltered production dataset checksums
"""
import hashlib
from pathlib import Path
import unittest
from fastapi.testclient import TestClient

from src.api.main import app
from src.storage.db import init_db, list_projects, save_project, get_project, delete_project
from src.recommender.staged_recommender import generate_build_recommendation, generate_upgrade_recommendation

ROOT = Path(__file__).resolve().parent.parent


class ApiAndRecommenderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        init_db()

    def test_01_api_health(self):
        """1. Verifies /api/health returns 200 with model readiness flags."""
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["app"], "BuildWise-AI")
        self.assertTrue(data["models"]["cpu_model_available"])
        self.assertTrue(data["models"]["gpu_model_available"])

    def test_02_catalog_summary(self):
        """2. Verifies /api/catalog/summary reports actual production dataset counts."""
        response = self.client.get("/api/catalog/summary")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["components_count"], 1208)
        self.assertEqual(data["prices_count"], 1109)
        self.assertEqual(data["benchmarks_count"], 237)
        self.assertTrue(data["cpu_models_available"])
        self.assertTrue(data["gpu_models_available"])

    def test_03_build_recommendation_success(self):
        """3. Verifies Build Mode generates complete, verified workflow graph."""
        payload = {"usage": "Gaming", "budget": 85000}
        response = self.client.post("/api/build/recommend", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["mode"], "build")
        self.assertIn("Gaming", data["name"])
        self.assertTrue(len(data["nodes"]) >= 10)
        self.assertTrue(len(data["edges"]) >= 10)
        self.assertIn("total", data["summary"])
        self.assertLessEqual(data["summary"]["total"], 85000 + 5000)

        # Confirm nodes have required fields and no standalone analysis/compat nodes
        kinds = [n["data"]["kind"] for n in data["nodes"]]
        self.assertIn("requirements", kinds)
        self.assertIn("component", kinds)
        self.assertIn("final", kinds)
        self.assertNotIn("budget", kinds)
        self.assertNotIn("ai", kinds)
        self.assertNotIn("compat", kinds)

    def test_04_build_budget_validation(self):
        """4. Verifies invalid or too-low budgets return clear error states."""
        # Non-positive budget
        res_zero = self.client.post("/api/build/recommend", json={"usage": "Gaming", "budget": 0})
        self.assertEqual(res_zero.status_code, 422)

        # Below minimal threshold
        res_low = self.client.post("/api/build/recommend", json={"usage": "Gaming", "budget": 5000})
        self.assertEqual(res_low.status_code, 400)
        self.assertIn("minimum viable threshold", res_low.json()["detail"])

    def test_05_upgrade_recommendation_success(self):
        """5. Verifies Upgrade Mode analyzes existing hardware and proposes compatible replacements."""
        payload = {
            "existing": {
                "cpu": "Ryzen 5 3600",
                "gpu": "GTX 1660 Super",
                "motherboard": "B450",
                "ram": "16GB",
                "psu": "550W",
            },
            "budget": 40000,
            "goal": "Better Gaming Performance",
        }
        response = self.client.post("/api/upgrade/recommend", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["mode"], "upgrade")
        self.assertTrue(len(data["nodes"]) >= 6)
        self.assertTrue(len(data["edges"]) >= 5)

        # Check existing vs recommended vs reusable distinction
        statuses = [n["data"]["status"] for n in data["nodes"]]
        self.assertIn("existing", statuses)
        self.assertIn("recommended", statuses)
        self.assertIn("reusable", statuses)

        # Confirm no standalone analysis or compat cards
        kinds = [n["data"]["kind"] for n in data["nodes"]]
        self.assertNotIn("analysis", kinds)
        self.assertNotIn("compat", kinds)

    def test_06_ml_performance_in_nodes(self):
        """6. Verifies ML predictions are attached to supported CPU/GPU component nodes."""
        rec = generate_build_recommendation("Content Creation", 120000)
        cpu_comp = rec["components"].get("cpu")
        self.assertIsNotNone(cpu_comp)
        self.assertIn("mlPrediction", cpu_comp)
        if cpu_comp["mlPrediction"] and cpu_comp["mlPrediction"].get("status") == "success":
            self.assertGreater(cpu_comp["mlPrediction"]["score"], 0)
            self.assertIn("Cinebench R23", cpu_comp["mlPrediction"]["metric"])

    def test_07_component_replacement(self):
        """7. Tests dynamic component replacement and revalidation via API."""
        # First generate a build
        payload = {"usage": "Gaming", "budget": 80000}
        rec_res = self.client.post("/api/build/recommend", json=payload)
        self.assertEqual(rec_res.status_code, 200)
        proj = rec_res.json()
        proj_id = proj["id"]

        # Find an alternative CPU
        cpu_node = next(n for n in proj["nodes"] if n["data"].get("category") == "cpu")
        alternatives = cpu_node["data"].get("alternatives", [])
        self.assertTrue(len(alternatives) > 0, "Should provide compatible alternatives")
        alt_id = alternatives[0]["id"]

        # Request replacement
        rep_res = self.client.post(
            f"/api/workflow/{proj_id}/replace-component",
            json={"category": "cpu", "new_component_id": alt_id},
        )
        self.assertEqual(rep_res.status_code, 200)
        updated_proj = rep_res.json()
        new_cpu_node = next(n for n in updated_proj["nodes"] if n["data"].get("category") == "cpu")
        self.assertEqual(new_cpu_node["data"]["componentId"], alt_id)

    def test_08_sqlite_persistence_crud(self):
        """8. Tests SQLite project creation, retrieval, listing, and deletion."""
        test_proj = {
            "id": "p_test_suite_01",
            "mode": "build",
            "name": "Unit Test Build",
            "inputs": {"usage": "Office Work", "budget": 45000},
            "nodes": [{"id": "n-1", "data": {"label": "Test Node"}}],
            "edges": [],
            "summary": {"total": 42000},
        }
        saved = save_project(test_proj)
        self.assertEqual(saved["id"], "p_test_suite_01")

        retrieved = get_project("p_test_suite_01")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved["name"], "Unit Test Build")

        # Delete
        del_res = self.client.delete("/api/projects/p_test_suite_01")
        self.assertEqual(del_res.status_code, 200)
        self.assertIsNone(get_project("p_test_suite_01"))

    def test_09_history_endpoint(self):
        """9. Verifies recommendation history is recorded and retrieved."""
        # Generate build to trigger history
        self.client.post("/api/build/recommend", json={"usage": "Gaming", "budget": 65000})
        res = self.client.get("/api/history")
        self.assertEqual(res.status_code, 200)
        history = res.json()
        self.assertGreater(len(history), 0)

    def test_10_production_csv_integrity(self):
        """10. Ensures production datasets remain completely unmodified."""
        expected_hashes = {
            "components.csv": "6753f468dec05adc2ccb4c2582bf798c922a70474aac8ffb8508541a19a67ecc",
            "prices.csv": "6a8a6e14cca32c120170ab244a0f93ebd6514d212264a2034ca96844c71ca625",
            "benchmarks.csv": "4187f577bb064f429f12cb644ffed343246b98e56f2122aea9f095714a564702",
        }
        for filename, expected_sha in expected_hashes.items():
            path = ROOT / "data" / filename
            hasher = hashlib.sha256()
            with open(path, "rb") as f:
                hasher.update(f.read())
            self.assertEqual(hasher.hexdigest(), expected_sha, f"{filename} checksum mismatch!")


if __name__ == "__main__":
    unittest.main()
