"""
Unit and integration tests for BuildWise-AI PDF and CSV report exporters.
"""
import io
import unittest
from fastapi.testclient import TestClient

from src.api.main import app
from src.export import (
    generate_build_csv,
    generate_upgrade_csv,
    generate_build_pdf,
    generate_upgrade_pdf,
)
from src.storage.db import get_project, init_db, save_project


class TestExportReports(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = TestClient(app)

        # Create a sample Build Mode project
        cls.build_project = {
            "id": "p_test_export_build_01",
            "mode": "build",
            "name": "Export Test Build · Rs 75,000",
            "inputs": {"usage": "Gaming", "budget": 75000},
            "summary": {
                "total": 42740,
                "budget": 75000,
                "remaining": 32260,
                "status": "compatible",
                "notes": ["Selected Core i7-14700K for gaming.", "Verified DDR5-5200."],
            },
            "recommendationSnapshot": {
                "components": {
                    "cpu": {
                        "component_id": "DS3_CPU_012",
                        "category": "cpu",
                        "brand": "Intel",
                        "model": "Core i7-14700K",
                        "name": "Intel Core i7-14700K",
                        "specs": {"cores": 20, "threads": 28, "boost_ghz": 5.6, "tdp_w": 253, "socket": "LGA1700"},
                        "price": 4370,
                        "seller": "Computech Store",
                        "availability": "available",
                        "priceBasis": "Verified retailer observation",
                        "empiricalBenchmark": None,
                        "mlPrediction": {
                            "metric": "Predicted Cinebench R23 Multi-Core",
                            "score": 35560.8,
                            "model": "Ridge Regression (alpha=10.0)",
                            "status": "success",
                        },
                    },
                    "gpu": {
                        "component_id": "DS3_GPU_001",
                        "category": "gpu",
                        "brand": "NVIDIA",
                        "model": "GeForce RTX 4070 SUPER",
                        "name": "NVIDIA GeForce RTX 4070 SUPER",
                        "specs": {"chipset": "RTX 4070 Super", "vram_gb": 12, "boost_clock_mhz": 2475, "tgp_w": 220},
                        "price": 58990,
                        "seller": "PrimeABGB",
                        "availability": "available",
                        "empiricalBenchmark": {
                            "suite": "3DMark",
                            "metric": "Time Spy Graphics",
                            "score": 21000,
                            "source": "Recorded empirical observation",
                        },
                        "mlPrediction": {
                            "metric": "Predicted Time Spy Graphics",
                            "score": 20850.5,
                            "model": "Ridge Regression (alpha=1.0)",
                            "status": "success",
                        },
                    },
                    "motherboard": {
                        "component_id": "DS3_MB_005",
                        "category": "motherboard",
                        "brand": "ASRock",
                        "model": "B760 Pro RS",
                        "name": "ASRock B760 Pro RS",
                        "specs": {"socket": "LGA1700", "chipset": "B760", "form_factor": "ATX", "ram_type": "DDR5"},
                        "price": 13990,
                        "seller": "MDComputers",
                        "availability": "available",
                    },
                },
                "validation": {"compatible": True, "warnings": []},
                "summary": {"total": 42740, "budget": 75000, "remaining": 32260},
                "notes": ["Selected Core i7-14700K for gaming."],
            },
            "nodes": [],
            "edges": [],
        }
        save_project(cls.build_project)

        # Create a sample Upgrade Mode project
        cls.upgrade_project = {
            "id": "p_test_export_upgrade_01",
            "mode": "upgrade",
            "name": "Export Test Upgrade · Better Gaming",
            "inputs": {
                "existing": {
                    "cpu": {"name": "AMD Ryzen 5 3600", "specs": {"socket": "AM4", "cores": 6}},
                    "gpu": {"name": "GTX 1060 6GB", "specs": {"vram_gb": 6}},
                },
                "budget": 50000,
                "goal": "Better Gaming Performance",
            },
            "summary": {
                "total": 35000,
                "budget": 50000,
                "remaining": 15000,
                "status": "compatible",
                "upgradedCategories": ["gpu"],
            },
            "recommendationSnapshot": {
                "existing": {
                    "cpu": {"name": "AMD Ryzen 5 3600", "specs": {"socket": "AM4", "cores": 6}},
                    "gpu": {"name": "GTX 1060 6GB", "specs": {"vram_gb": 6}},
                },
                "proposed": {
                    "cpu": {"name": "AMD Ryzen 5 3600", "price": 0, "specs": {"socket": "AM4", "cores": 6}},
                    "gpu": {
                        "name": "ASUS RTX 4060 Ti 8GB",
                        "brand": "ASUS",
                        "model": "Dual RTX 4060 Ti",
                        "price": 35000,
                        "seller": "MDComputers",
                        "availability": "available",
                        "specs": {"vram_gb": 8, "tgp_w": 160},
                        "mlPrediction": {"metric": "Predicted Time Spy Graphics", "score": 13450.0},
                    },
                },
                "deltas": {
                    "gpu": {
                        "metric": "Time Spy Graphics Score",
                        "baseline": 4150.0,
                        "upgraded": 13450.0,
                        "delta": 9300.0,
                        "pct_gain": 224.1,
                    }
                },
                "summary": {"total": 35000, "budget": 50000, "remaining": 15000},
            },
            "nodes": [],
            "edges": [],
        }
        save_project(cls.upgrade_project)

    # -------------------------------------------------------------------------
    # CSV Tests
    # -------------------------------------------------------------------------

    def test_generate_build_csv(self):
        csv_text = generate_build_csv(self.build_project)
        self.assertIsInstance(csv_text, str)
        self.assertIn("# BuildWise-AI PC Build Recommendation Specification", csv_text)
        self.assertIn("Project ID,p_test_export_build_01", csv_text)
        self.assertIn("Gaming", csv_text)
        self.assertIn("Intel Core i7-14700K", csv_text)
        self.assertIn("Predicted Cinebench R23 Multi-Core", csv_text)
        self.assertIn("Ridge Regression (alpha=10.0)", csv_text)
        self.assertIn("3DMark", csv_text)
        self.assertIn("Time Spy Graphics", csv_text)
        self.assertIn("Computech Store", csv_text)
        self.assertIn("Disclaimer", csv_text)

    def test_generate_upgrade_csv(self):
        csv_text = generate_upgrade_csv(self.upgrade_project)
        self.assertIsInstance(csv_text, str)
        self.assertIn("# BuildWise-AI PC Upgrade Recommendation Report", csv_text)
        self.assertIn("Better Gaming Performance", csv_text)
        self.assertIn("AMD Ryzen 5 3600", csv_text)
        self.assertIn("ASUS RTX 4060 Ti 8GB", csv_text)
        self.assertIn("REPLACED", csv_text)
        self.assertIn("RETAINED", csv_text)
        self.assertIn("+9,300 pts (+224.1%)", csv_text)
        self.assertIn("Disclaimer", csv_text)

    # -------------------------------------------------------------------------
    # PDF Tests
    # -------------------------------------------------------------------------

    def test_generate_build_pdf(self):
        pdf_bytes = generate_build_pdf(self.build_project)
        self.assertIsInstance(pdf_bytes, bytes)
        self.assertTrue(pdf_bytes.startswith(b"%PDF-"))
        self.assertGreater(len(pdf_bytes), 10000)

    def test_generate_upgrade_pdf(self):
        pdf_bytes = generate_upgrade_pdf(self.upgrade_project)
        self.assertIsInstance(pdf_bytes, bytes)
        self.assertTrue(pdf_bytes.startswith(b"%PDF-"))
        self.assertGreater(len(pdf_bytes), 10000)

    # -------------------------------------------------------------------------
    # Edge Cases Tests (Missing Prices, Missing Predictions, Empty Structs)
    # -------------------------------------------------------------------------

    def test_export_edge_cases(self):
        sparse_proj = {
            "id": "p_sparse_test",
            "mode": "build",
            "name": "Sparse Test",
            "inputs": {},
            "summary": {},
            "recommendationSnapshot": {
                "components": {
                    "cpu": {
                        "category": "cpu",
                        "brand": "Unknown",
                        "model": "Generic CPU",
                        "price": None,
                        "empiricalBenchmark": None,
                        "mlPrediction": None,
                    }
                }
            },
            "nodes": [],
        }
        csv_sparse = generate_build_csv(sparse_proj)
        self.assertIn("Generic CPU", csv_sparse)
        self.assertIn("Unpriced", csv_sparse)

        pdf_sparse = generate_build_pdf(sparse_proj)
        self.assertTrue(pdf_sparse.startswith(b"%PDF-"))

    # -------------------------------------------------------------------------
    # FastAPI HTTP Endpoints Tests
    # -------------------------------------------------------------------------

    def test_api_export_build_pdf(self):
        resp = self.client.get("/api/export/p_test_export_build_01/pdf")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.headers.get("content-type"), "application/pdf")
        self.assertIn("attachment; filename=", resp.headers.get("content-disposition", ""))
        self.assertTrue(resp.content.startswith(b"%PDF-"))

    def test_api_export_build_csv(self):
        resp = self.client.get("/api/export/p_test_export_build_01/csv")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.headers.get("content-type"), "text/csv; charset=utf-8-sig")
        self.assertIn("attachment; filename=", resp.headers.get("content-disposition", ""))
        # Verify UTF-8 BOM is present at the beginning of content
        self.assertTrue(resp.content.startswith(b"\xef\xbb\xbf"))
        decoded = resp.content.decode("utf-8-sig")
        self.assertIn("Intel Core i7-14700K", decoded)

    def test_api_export_upgrade_pdf(self):
        resp = self.client.get("/api/export/p_test_export_upgrade_01/pdf")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.headers.get("content-type"), "application/pdf")
        self.assertTrue(resp.content.startswith(b"%PDF-"))

    def test_api_export_upgrade_csv(self):
        resp = self.client.get("/api/export/p_test_export_upgrade_01/csv")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.headers.get("content-type"), "text/csv; charset=utf-8-sig")
        self.assertTrue(resp.content.startswith(b"\xef\xbb\xbf"))
        decoded = resp.content.decode("utf-8-sig")
        self.assertIn("ASUS RTX 4060 Ti", decoded)

    def test_api_export_not_found(self):
        resp = self.client.get("/api/export/nonexistent_project_999/pdf")
        self.assertEqual(resp.status_code, 404)

        resp_csv = self.client.get("/api/export/nonexistent_project_999/csv")
        self.assertEqual(resp_csv.status_code, 404)


if __name__ == "__main__":
    unittest.main()
