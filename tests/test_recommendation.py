import csv
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest


ROOT = Path(__file__).resolve().parents[1]


class RecommendationTests(unittest.TestCase):
    def _run_synthetic_recommendation(
        self,
        budget,
        prefer_available=False,
        available_cpu=False,
        include_availability_alternative=False,
        include_unknown_alternative=False,
        include_estimate_alternative=False,
        include_available_board_alternative=False,
        include_vendor_prefixed_board_alternative=False,
        include_storage_alternative=False,
        include_capacity_alternative=False,
        checked_at="2026-10-21",
        freshness_days=7,
        seller_url="https://example.com/offer",
        seller_name="Test Seller",
    ):
        temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(temporary_directory.cleanup)
        app_root = Path(temporary_directory.name)
        data_dir = app_root / "data"
        data_dir.mkdir()
        shutil.copy2(ROOT / "app.py", app_root / "app.py")

        component_rows = [
            ("cpu-incompatible", "cpu", "Budget CPU", {"socket": "AM4", "supported_chipsets": ["B550"], "ram_type": "DDR4"}),
            ("cpu-compatible", "cpu", "Compatible CPU", {"socket": "AM5", "supported_chipsets": ["B650"], "ram_type": "DDR5"}),
            ("board", "motherboard", "Test Board", {"socket": "AM5", "chipset": "B650", "form_factor": "ATX", "ram_type": "DDR5"}),
            ("memory", "ram", "Test RAM", {"ram_type": "DDR5", "capacity_gb": 32}),
            ("drive", "storage", "Test Storage", {"interface": "NVMe Gen4 x4", "form_factor": "M.2 2280"}),
            ("chassis", "case", "Test Case", {"supports_form_factors": ["ATX"], "max_gpu_length_mm": 300}),
        ]
        if include_storage_alternative:
            component_rows[2] = (
                "board",
                "motherboard",
                "Unsupported Storage Board",
                {
                    "socket": "AM5",
                    "chipset": "B650",
                    "form_factor": "ATX",
                    "ram_type": "DDR5",
                    "supported_storage_interfaces": ["SATA"],
                    "supported_storage_form_factors": ["2.5-inch"],
                },
            )
            component_rows.append((
                "board-storage-compatible",
                "motherboard",
                "Storage-Compatible Board",
                {
                    "socket": "AM5",
                    "chipset": "B650",
                    "form_factor": "ATX",
                    "ram_type": "DDR5",
                    "supported_storage_interfaces": ["NVMe"],
                    "supported_storage_form_factors": ["M.2 2280"],
                },
            ))
        if include_capacity_alternative:
            component_rows[2] = (
                "board",
                "motherboard",
                "Low-Capacity Board",
                {
                    "socket": "AM5",
                    "chipset": "B650",
                    "form_factor": "ATX",
                    "ram_type": "DDR5",
                    "ram_max_gb": 16,
                },
            )
            component_rows[3] = (
                "memory",
                "ram",
                "Oversized RAM Kit",
                {"ram_type": "DDR5", "capacity_gb": 32},
            )
            component_rows.append((
                "memory-compatible-capacity",
                "ram",
                "Within-Capacity RAM Kit",
                {"ram_type": "DDR5", "capacity_gb": 16},
            ))
        if include_available_board_alternative:
            component_rows.append((
                "board-available",
                "motherboard",
                "Available Test Board",
                {"socket": "AM5", "chipset": "B650", "form_factor": "ATX", "ram_type": "DDR5"},
            ))
        if include_vendor_prefixed_board_alternative:
            component_rows[2] = (
                "board",
                "motherboard",
                "Unsupported Test Board",
                {"socket": "AM5", "chipset": "Z890", "form_factor": "ATX", "ram_type": "DDR5"},
            )
            component_rows.append((
                "board-vendor-prefixed",
                "motherboard",
                "Vendor-Prefixed Test Board",
                {"socket": "AM5", "chipset": "AMD B650", "form_factor": "ATX", "ram_type": "DDR5"},
            ))
        with (data_dir / "components.csv").open(
            "w", newline="", encoding="utf-8"
        ) as destination:
            fields = [
                "component_id", "category", "brand", "model", "specs_json",
                "source_name", "source_url", "source_license", "identity_status",
            ]
            writer = csv.DictWriter(destination, fieldnames=fields)
            writer.writeheader()
            for component_id, category, model, specs in component_rows:
                writer.writerow({
                    "component_id": component_id,
                    "category": category,
                    "brand": "Test Brand",
                    "model": model,
                    "specs_json": json.dumps(specs),
                    "source_name": "Test source",
                    "source_url": "https://example.com/component",
                    "source_license": "test",
                    "identity_status": "verified",
                })

        prices = [
            ("cpu-incompatible", 100, "unknown"),
            (
                "cpu-compatible",
                300,
                "available"
                if available_cpu or include_availability_alternative
                else "unknown",
            ),
            ("board", 100, "unknown"),
            ("memory", 50, "unknown"),
            ("drive", 50, "unknown"),
            ("chassis", 50, "unknown"),
        ]
        if include_available_board_alternative:
            prices.append(("board-available", 150, "available"))
        if include_vendor_prefixed_board_alternative:
            prices.append(("board-vendor-prefixed", 150, "unknown"))
        if include_storage_alternative:
            prices.append(("board-storage-compatible", 150, "unknown"))
        if include_capacity_alternative:
            prices.append(("memory-compatible-capacity", 100, "unknown"))
        if include_availability_alternative:
            prices.append(("cpu-compatible", 250, "unavailable"))
        if include_unknown_alternative:
            prices.append(("cpu-compatible", 275, "unknown"))
        if include_estimate_alternative:
            prices.append(("cpu-compatible", 50, "unknown", "planning_estimate"))
        with (data_dir / "prices.csv").open(
            "w", newline="", encoding="utf-8"
        ) as destination:
            fields = [
                "price_id", "component_id", "seller", "price_inr",
                "source_url", "checked_at", "availability", "price_type",
                "provenance",
            ]
            writer = csv.DictWriter(destination, fieldnames=fields)
            writer.writeheader()
            for index, price in enumerate(prices):
                component_id, amount, availability = price[:3]
                is_estimate = len(price) > 3 and price[3] == "planning_estimate"
                writer.writerow({
                    "price_id": f"price-{index}",
                    "component_id": component_id,
                    "seller": "" if is_estimate else seller_name,
                    "price_inr": amount,
                    "source_url": "" if is_estimate else seller_url,
                    "checked_at": "" if is_estimate else checked_at,
                    "availability": availability,
                    "price_type": "planning_estimate" if is_estimate else "seller_observation",
                    "provenance": "Test estimate" if is_estimate else "",
                })

        app = AppTest.from_file(str(app_root / "app.py"), default_timeout=10).run()
        app.number_input[0].set_value(budget)
        app.selectbox[0].set_value("study/office")
        app.button[0].click().run()
        return app

    def test_unavailable_prices_count_toward_budget_without_affecting_compatibility(self):
        app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=10).run()
        app.number_input[0].set_value(250_000)
        app.selectbox[0].set_value("gaming")
        app.button[0].click().run()

        self.assertFalse(app.exception)
        selected = app.dataframe[0].value
        unavailable = selected[selected["availability"] == "unavailable"]
        self.assertGreater(len(unavailable), 0)
        self.assertTrue((unavailable["compatibility"] == "compatible").any())

        recorded_total = int(selected["price_inr"].sum())
        available_total = int(
            selected.loc[selected["availability"] == "available", "price_inr"].sum()
        )
        total_message = next(
            item.value for item in app.markdown
            if item.value.startswith((
                "**Recorded-price total:**",
                "**Budget total (includes planning estimate):**",
            ))
        )
        self.assertIn(f"{recorded_total:,} INR", total_message)
        self.assertGreater(recorded_total, available_total)

    def test_rm750x_estimate_counts_toward_budget_and_is_labeled(self):
        with tempfile.TemporaryDirectory() as directory:
            app_root = Path(directory)
            data_dir = app_root / "data"
            data_dir.mkdir()
            shutil.copy2(ROOT / "app.py", app_root / "app.py")
            shutil.copy2(ROOT / "data" / "components.csv", data_dir / "components.csv")
            with (data_dir / "components.csv").open(
                newline="", encoding="utf-8"
            ) as comp_source:
                comp_reader = csv.DictReader(comp_source)
                competing_psu_ids = {
                    row["component_id"]
                    for row in comp_reader
                    if row["category"].strip().casefold() == "psu"
                    and row["component_id"] != "psu-750w-gold"
                }
            with (ROOT / "data" / "prices.csv").open(
                newline="", encoding="utf-8-sig"
            ) as source:
                reader = csv.DictReader(source)
                rows = [
                    row for row in reader
                    if row["price_id"] != "price-psu-corsair-rm750x-amazon-20261023-120759"
                    and row["component_id"] not in competing_psu_ids
                ]
                fieldnames = reader.fieldnames
            with (data_dir / "prices.csv").open(
                "w", newline="", encoding="utf-8"
            ) as destination:
                writer = csv.DictWriter(destination, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)

            app = AppTest.from_file(str(app_root / "app.py"), default_timeout=10).run()
            app.number_input[0].set_value(200_000)
            app.selectbox[0].set_value("study/office")
            app.button[0].click().run()

            self.assertFalse(app.exception)
            selected = app.dataframe[0].value
            psu = selected[selected["model"] == "RM750x (2024) 750W 80+ Gold"].iloc[0]
            self.assertEqual(psu["price_inr"], 29370)
            self.assertEqual(psu["availability"], "unknown")
            self.assertEqual(psu["price_basis"], "User-provided planning estimate")
            self.assertIn("not an independently verified seller price", psu["provenance"])

            estimate_total = int(selected["price_inr"].sum())
            total_message = next(
                item.value for item in app.markdown
                if item.value.startswith("**Budget total (includes planning estimate):**")
            )
            self.assertIn(f"{estimate_total:,} INR", total_message)
            self.assertTrue(any(
                "user-provided planning estimate" in item.value
                and "not an independently verified seller price" in item.value
                for item in app.warning
            ))

    def test_equal_price_seller_observation_is_preferred_over_estimate(self):
        with tempfile.TemporaryDirectory() as directory:
            app_root = Path(directory)
            data_dir = app_root / "data"
            data_dir.mkdir()
            shutil.copy2(ROOT / "app.py", app_root / "app.py")
            shutil.copy2(ROOT / "data" / "components.csv", data_dir / "components.csv")
            with (data_dir / "components.csv").open(
                newline="", encoding="utf-8"
            ) as comp_source:
                comp_reader = csv.DictReader(comp_source)
                competing_psu_ids = {
                    row["component_id"]
                    for row in comp_reader
                    if row["category"].strip().casefold() == "psu"
                    and row["component_id"] != "psu-750w-gold"
                }
            with (ROOT / "data" / "prices.csv").open(
                newline="", encoding="utf-8-sig"
            ) as source:
                reader = csv.DictReader(source)
                rows = [
                    row for row in reader
                    if row["component_id"] not in competing_psu_ids
                ]
                fieldnames = reader.fieldnames
            with (data_dir / "prices.csv").open(
                "w", newline="", encoding="utf-8"
            ) as destination:
                writer = csv.DictWriter(destination, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)

            app = AppTest.from_file(str(app_root / "app.py"), default_timeout=10).run()
            app.number_input[0].set_value(200_000)
            app.selectbox[0].set_value("study/office")
            app.button[0].click().run()

            self.assertFalse(app.exception)
            selected = app.dataframe[0].value
            psu = selected[selected["model"] == "RM750x (2024) 750W 80+ Gold"].iloc[0]
            self.assertEqual(psu["price_inr"], 29370)
            self.assertEqual(psu["availability"], "available")
            self.assertEqual(psu["price_basis"], "Recorded seller observation")
            self.assertEqual(psu["seller"], "Global Klamp")
            self.assertTrue(any(
                item.value.startswith("**Recorded-price total:**")
                for item in app.markdown
            ))

    def test_simplified_interface_has_no_available_first_controls(self):
        app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=10).run()
        # Form has only 1 checkbox (peripherals), and no select_slider
        self.assertEqual(len(app.checkbox), 1)
        self.assertEqual(len(app.select_slider), 0)
        app.number_input[0].set_value(250_000)
        app.selectbox[0].set_value("study/office")
        app.button[0].click().run()
        self.assertFalse(app.exception)
        self.assertTrue(any(
            "Selection uses the lowest recorded price per component" in item.value
            for item in app.caption
        ))

    def test_recommender_keeps_vendor_prefixed_supported_chipset_candidate(self):
        app = self._run_synthetic_recommendation(
            700,
            include_vendor_prefixed_board_alternative=True,
        )

        self.assertFalse(app.exception)
        selected = app.dataframe[0].value
        motherboard = selected[
            selected["category"].str.casefold() == "motherboard"
        ].iloc[0]
        self.assertEqual(motherboard["model"], "Vendor-Prefixed Test Board")
        self.assertEqual(motherboard["compatibility"], "unknown")
        self.assertIn("chipset AMD B650 as supported", motherboard["compatibility_reason"])
        self.assertIn("No minimum BIOS requirement is documented", motherboard["compatibility_reason"])

    def test_recommender_prefers_documented_storage_compatible_motherboard(self):
        app = self._run_synthetic_recommendation(
            700,
            include_storage_alternative=True,
        )

        self.assertFalse(app.exception)
        selected = app.dataframe[0].value
        motherboard = selected[
            selected["category"].str.casefold() == "motherboard"
        ].iloc[0]
        self.assertEqual(motherboard["model"], "Storage-Compatible Board")
        self.assertNotIn(
            "does not list the storage interface",
            motherboard["compatibility_reason"],
        )
        self.assertIn(
            "Motherboard lists the storage interface NVME as supported",
            motherboard["compatibility_reason"],
        )

    def test_recommender_avoids_ram_capacity_exceeding_documented_board_limit(self):
        app = self._run_synthetic_recommendation(
            700,
            include_capacity_alternative=True,
        )

        self.assertFalse(app.exception)
        selected = app.dataframe[0].value
        ram = selected[selected["category"].str.casefold() == "ram"].iloc[0]
        self.assertEqual(ram["model"], "Within-Capacity RAM Kit")
        self.assertIn(
            "within the motherboard maximum of 16 GB",
            ram["compatibility_reason"],
        )

    def test_complete_build_reports_unknown_overall_compatibility(self):
        app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=10).run()
        app.number_input[0].set_value(250_000)
        app.selectbox[0].set_value("study/office")
        app.button[0].click().run()

        self.assertFalse(app.exception)
        self.assertTrue(any(
            "Recommendation status:" in item.value
            and "Complete PC build" in item.value
            for item in app.markdown
        ))
        self.assertTrue(any(
            "Overall compatibility:" in item.value
            and "Unknown" in item.value
            for item in app.markdown
        ))
        self.assertFalse(any(
            "Overall compatibility:** Compatible" in item.value
            for item in app.markdown
        ))

    def test_storage_evidence_changes_catalog_motherboard_selection(self):
        app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=10).run()
        app.number_input[0].set_value(250_000)
        app.selectbox[0].set_value("study/office")
        app.button[0].click().run()

        self.assertFalse(app.exception)
        selected = app.dataframe[0].value
        motherboard = selected[
            selected["category"].str.casefold() == "motherboard"
        ].iloc[0]
        self.assertEqual(motherboard["model"], "TUF Gaming B850-PLUS WiFi")
        self.assertIn(
            "validates this CPU since all BIOS versions",
            motherboard["compatibility_reason"],
        )
        self.assertIn(
            "Motherboard lists the storage interface NVME as supported",
            motherboard["compatibility_reason"],
        )
        self.assertIn("storage", selected["category"].str.casefold().tolist())

    def test_recommendation_uses_exact_pair_bios_support_evidence(self):
        app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=10).run()
        app.number_input[0].set_value(250_000)
        app.selectbox[0].set_value("study/office")
        app.button[0].click().run()

        self.assertFalse(app.exception)
        selected = app.dataframe[0].value
        motherboard = selected[
            selected["category"].str.casefold() == "motherboard"
        ].iloc[0]
        self.assertEqual(motherboard["model"], "TUF Gaming B850-PLUS WiFi")
        self.assertEqual(motherboard["compatibility"], "compatible")
        self.assertIn(
            "validates this CPU since all BIOS versions",
            motherboard["compatibility_reason"],
        )

    def test_office_build_reports_psu_unknown_without_discrete_gpu(self):
        app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=10).run()
        app.number_input[0].set_value(250_000)
        app.selectbox[0].set_value("study/office")
        app.button[0].click().run()

        self.assertFalse(app.exception)
        selected = app.dataframe[0].value
        self.assertNotIn("gpu", selected["category"].str.casefold().tolist())
        psu = selected[selected["category"].str.casefold() == "psu"].iloc[0]
        self.assertEqual(psu["compatibility"], "unknown")
        self.assertIn(
            "documented GPU/system PSU requirement is missing",
            psu["compatibility_reason"],
        )
        self.assertTrue(any(
            "PSU/system compatibility unknown" in item.value
            and "documented GPU/system PSU requirement is missing" in item.value
            for item in app.warning
        ))

    def test_missing_required_category_is_reported_as_partial_not_zero_cost(self):
        with tempfile.TemporaryDirectory() as directory:
            app_root = Path(directory)
            data_dir = app_root / "data"
            data_dir.mkdir()
            shutil.copy2(ROOT / "app.py", app_root / "app.py")
            shutil.copy2(ROOT / "data" / "components.csv", data_dir / "components.csv")
            with (data_dir / "components.csv").open(
                newline="", encoding="utf-8"
            ) as comp_source:
                comp_reader = csv.DictReader(comp_source)
                psu_ids = {
                    row["component_id"]
                    for row in comp_reader
                    if row["category"].strip().casefold() == "psu"
                }
            with (ROOT / "data" / "prices.csv").open(
                newline="", encoding="utf-8"
            ) as source:
                reader = csv.DictReader(source)
                rows = [
                    row for row in reader
                    if row["component_id"] not in psu_ids
                ]
                fieldnames = reader.fieldnames
            with (data_dir / "prices.csv").open(
                "w", newline="", encoding="utf-8"
            ) as destination:
                writer = csv.DictWriter(destination, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)

            app = AppTest.from_file(str(app_root / "app.py"), default_timeout=10).run()
            app.number_input[0].set_value(250_000)
            app.selectbox[0].set_value("study/office")
            app.button[0].click().run()

            self.assertFalse(app.exception)
            selected = app.dataframe[0].value
            self.assertNotIn("psu", selected["category"].str.casefold().tolist())
            recorded_total = int(selected["price_inr"].sum())
            self.assertGreater(recorded_total, 0)
            self.assertLessEqual(recorded_total, 250_000)
            self.assertTrue(any(
                "Partial PC build" in item.value and "psu" in item.value
                for item in app.markdown
            ))
            self.assertTrue(any(
                "prices were not treated as zero" in item.value
                for item in app.warning
            ))

    def test_gaming_partial_recommendation_names_missing_gpu(self):
        with tempfile.TemporaryDirectory() as directory:
            app_root = Path(directory)
            data_dir = app_root / "data"
            data_dir.mkdir()
            shutil.copy2(ROOT / "app.py", app_root / "app.py")
            shutil.copy2(ROOT / "data" / "components.csv", data_dir / "components.csv")
            with (data_dir / "components.csv").open(
                newline="", encoding="utf-8"
            ) as comp_source:
                comp_reader = csv.DictReader(comp_source)
                gpu_ids = {
                    row["component_id"]
                    for row in comp_reader
                    if row["category"].strip().casefold() == "gpu"
                }
            with (ROOT / "data" / "prices.csv").open(
                newline="", encoding="utf-8"
            ) as source:
                reader = csv.DictReader(source)
                rows = [
                    row for row in reader
                    if row["component_id"] not in gpu_ids
                ]
                fieldnames = reader.fieldnames
            with (data_dir / "prices.csv").open(
                "w", newline="", encoding="utf-8"
            ) as destination:
                writer = csv.DictWriter(destination, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)

            app = AppTest.from_file(str(app_root / "app.py"), default_timeout=10).run()
            app.number_input[0].set_value(250_000)
            app.selectbox[0].set_value("gaming")
            app.button[0].click().run()

            self.assertFalse(app.exception)
            selected = app.dataframe[0].value
            self.assertNotIn("gpu", selected["category"].str.casefold().tolist())
            self.assertTrue(any(
                "Partial PC build" in item.value and "gpu" in item.value
                for item in app.markdown
            ))

    def test_gaming_recommendation_does_not_omit_unpriced_cpu_cooler(self):
        with tempfile.TemporaryDirectory() as directory:
            app_root = Path(directory)
            data_dir = app_root / "data"
            data_dir.mkdir()
            shutil.copy2(ROOT / "app.py", app_root / "app.py")
            shutil.copy2(ROOT / "data" / "components.csv", data_dir / "components.csv")
            with (ROOT / "data" / "prices.csv").open(
                newline="", encoding="utf-8"
            ) as source:
                reader = csv.DictReader(source)
                rows = [
                    row for row in reader
                    if not row["component_id"].startswith("cooler-")
                ]
                fieldnames = reader.fieldnames
            with (data_dir / "prices.csv").open(
                "w", newline="", encoding="utf-8"
            ) as destination:
                writer = csv.DictWriter(destination, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)

            app = AppTest.from_file(str(app_root / "app.py"), default_timeout=10).run()
            app.number_input[0].set_value(300_000)
            app.selectbox[0].set_value("gaming")
            app.button[0].click().run()

            self.assertFalse(app.exception)
            selected = app.dataframe[0].value
            self.assertNotIn("cooler", selected["category"].str.casefold().tolist())
            self.assertTrue(any(
                "Partial PC build" in item.value and "cooler" in item.value
                for item in app.markdown
            ))
            self.assertTrue(any(
                "No priced cooler records are available" in item.value
                for item in app.warning
            ))

    def test_gaming_recommendation_includes_priced_cpu_cooler(self):
        app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=10).run()
        app.number_input[0].set_value(300_000)
        app.selectbox[0].set_value("gaming")
        app.button[0].click().run()

        self.assertFalse(app.exception)
        selected = app.dataframe[0].value
        self.assertIn("cooler", selected["category"].str.casefold().tolist())
        cooler_row = selected[selected["category"].str.casefold() == "cooler"].iloc[0]
        self.assertEqual(cooler_row["model"], "AK400 Black (R-AK400-BKNNMN-G-1)")
        self.assertEqual(cooler_row["price_inr"], 2290)
        self.assertEqual(cooler_row["availability"], "available")
        self.assertEqual(cooler_row["seller"], "Computech Store")
        self.assertEqual(len(selected), 8)

    def test_gaming_recommendation_cooler_is_compatible_and_overall_build_is_unknown(self):
        app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=10).run()
        app.number_input[0].set_value(300_000)
        app.selectbox[0].set_value("gaming")
        app.button[0].click().run()

        self.assertFalse(app.exception)
        selected = app.dataframe[0].value
        cooler_row = selected[selected["category"].str.casefold() == "cooler"].iloc[0]
        self.assertEqual(cooler_row["compatibility"], "compatible")
        self.assertIn("support for socket AM5", cooler_row["compatibility_reason"])
        self.assertIn("15 mm clearance", cooler_row["compatibility_reason"])

        ram_row = selected[selected["category"].str.casefold() == "ram"].iloc[0]
        self.assertEqual(ram_row["compatibility"], "unknown")
        self.assertIn("unlisted on the motherboard memory QVL", ram_row["compatibility_reason"])

        self.assertTrue(any(
            "Overall compatibility:" in item.value and "Unknown" in item.value
            for item in app.markdown
        ))
        self.assertFalse(any(
            "Overall compatibility:** Compatible" in item.value
            for item in app.markdown
        ))

    def test_upgrade_can_select_a_subset_and_existing_build_stays_unknown(self):
        app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=10).run()
        app.radio[0].set_value("Upgrade (selected categories only)")
        app.multiselect[0].set_value(["gpu"])
        app.number_input[0].set_value(100_000)
        app.selectbox[0].set_value("gaming")
        app.button[0].click().run()

        self.assertFalse(app.exception)
        selected = app.dataframe[0].value
        self.assertEqual(selected["category"].str.casefold().tolist(), ["gpu"])
        self.assertTrue(any(
            "Upgrade options for selected categories only" in item.value
            for item in app.markdown
        ))
        self.assertTrue(any(
            "Overall compatibility:** Unknown" in item.value
            for item in app.markdown
        ))
        self.assertTrue(any(
            "Compatibility with your existing components is unknown" in item.value
            for item in app.warning
        ))

    def test_missing_availability_is_unknown_metadata_not_incompatibility(self):
        with tempfile.TemporaryDirectory() as directory:
            app_root = Path(directory)
            data_dir = app_root / "data"
            data_dir.mkdir()
            shutil.copy2(ROOT / "app.py", app_root / "app.py")
            shutil.copy2(ROOT / "data" / "components.csv", data_dir / "components.csv")

            with (ROOT / "data" / "prices.csv").open(
                newline="", encoding="utf-8-sig"
            ) as source:
                reader = csv.DictReader(source)
                rows = list(reader)
                fieldnames = reader.fieldnames
            for row in rows:
                if row["component_id"] == "gpu-nvidia-asus-prime-rtx5070-o12g":
                    row["availability"] = ""
                    break
            else:
                self.fail("Expected GPU price observation was not found.")

            with (data_dir / "prices.csv").open(
                "w", newline="", encoding="utf-8"
            ) as destination:
                writer = csv.DictWriter(destination, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)

            app = AppTest.from_file(str(app_root / "app.py"), default_timeout=10).run()
            app.number_input[0].set_value(250_000)
            app.selectbox[0].set_value("gaming")
            app.button[0].click().run()

            self.assertFalse(app.exception)
            selected = app.dataframe[0].value
            gpu = selected[selected["category"] == "gpu"].iloc[0]
            self.assertEqual(gpu["availability"], "unknown")
            self.assertEqual(gpu["compatibility"], "compatible")
            self.assertTrue(any(
                "availability for gpu" in item.value.casefold()
                for item in app.warning
            ))

    def test_selects_a_more_compatible_alternative_within_budget(self):
        app = self._run_synthetic_recommendation(600)

        self.assertFalse(app.exception)
        selected = app.dataframe[0].value
        cpu = selected[selected["category"].str.casefold() == "cpu"].iloc[0]
        total_message = next(
            item.value for item in app.markdown
            if item.value.startswith("**Recorded-price total:**")
        )
        total = int(total_message.split("**")[-1].split()[0].replace(",", ""))
        self.assertEqual(cpu["model"], "Compatible CPU")
        self.assertEqual(cpu["compatibility"], "unknown")
        self.assertIn("BIOS", cpu["compatibility_reason"])
        self.assertLessEqual(total, 600)

    def test_indian_market_presence_verified_for_indian_retailer(self):
        app = self._run_synthetic_recommendation(
            600,
            seller_url="https://www.primeabgb.com/online-price-reviews-india/test-part/",
            seller_name="Prime ABGB",
        )

        self.assertFalse(app.exception)
        selected = app.dataframe[0].value
        cpu = selected[selected["category"].str.casefold() == "cpu"].iloc[0]
        self.assertEqual(cpu["indian_market_presence"], "Verified Indian listing")

    def test_indian_market_presence_warns_when_no_verified_indian_listing(self):
        app = self._run_synthetic_recommendation(
            600,
            seller_url="https://example.com/offer",
            seller_name="Test Seller",
        )

        self.assertFalse(app.exception)
        selected = app.dataframe[0].value
        cpu = selected[selected["category"].str.casefold() == "cpu"].iloc[0]
        self.assertEqual(cpu["indian_market_presence"], "No verified Indian listing")
        self.assertTrue(any(
            "no verified indian retailer listing was found for cpu" in item.value.casefold()
            for item in app.warning
        ))

    def test_stale_availability_is_flagged_as_historical_not_current_stock(self):
        app = self._run_synthetic_recommendation(
            600,
            available_cpu=True,
            checked_at="2026-10-01",
        )

        self.assertFalse(app.exception)
        selected = app.dataframe[0].value
        cpu = selected[selected["category"].str.casefold() == "cpu"].iloc[0]
        self.assertEqual(cpu["availability"], "available")
        self.assertEqual(cpu["availability_freshness"], "Potentially stale")
        self.assertTrue(any(
            "older than the 7-day freshness window" in item.value
            and "historical" in item.value
            for item in app.warning
        ))
        self.assertTrue(any(
            "not a live stock or delivery confirmation" in item.value
            for item in app.warning
        ))

    def test_gaming_recommendation_all_eight_components_have_verified_indian_listings(self):
        app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=10).run()
        app.number_input[0].set_value(300_000)
        app.selectbox[0].set_value("gaming")
        app.button[0].click().run()

        self.assertFalse(app.exception)
        selected = app.dataframe[0].value
        self.assertEqual(len(selected), 8)
        self.assertTrue(
            (selected["indian_market_presence"] == "Verified Indian listing").all(),
            "Expected all 8 gaming components to have verified Indian retailer listings",
        )
        self.assertFalse(any(
            "No verified Indian retailer listing was found" in item.value
            for item in app.warning
        ))
        self.assertTrue(any(
            "Indian retailer listings confirm documented local-market presence" in item.value
            for item in app.warning
        ))

    def test_planning_estimate_reports_no_verified_indian_listing(self):
        with tempfile.TemporaryDirectory() as directory:
            app_root = Path(directory)
            data_dir = app_root / "data"
            data_dir.mkdir()
            shutil.copy2(ROOT / "app.py", app_root / "app.py")
            shutil.copy2(ROOT / "data" / "components.csv", data_dir / "components.csv")
            with (data_dir / "components.csv").open(
                newline="", encoding="utf-8"
            ) as comp_source:
                comp_reader = csv.DictReader(comp_source)
                competing_psu_ids = {
                    row["component_id"]
                    for row in comp_reader
                    if row["category"].strip().casefold() == "psu"
                    and row["component_id"] != "psu-750w-gold"
                }
            with (ROOT / "data" / "prices.csv").open(
                newline="", encoding="utf-8-sig"
            ) as source:
                reader = csv.DictReader(source)
                rows = [
                    row for row in reader
                    if row["price_id"] != "price-psu-corsair-rm750x-amazon-20261023-120759"
                    and row["component_id"] not in competing_psu_ids
                ]
                fieldnames = reader.fieldnames
            with (data_dir / "prices.csv").open(
                "w", newline="", encoding="utf-8"
            ) as destination:
                writer = csv.DictWriter(destination, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)

            app = AppTest.from_file(str(app_root / "app.py"), default_timeout=10).run()
            app.number_input[0].set_value(200_000)
            app.selectbox[0].set_value("study/office")
            app.button[0].click().run()

            self.assertFalse(app.exception)
            selected = app.dataframe[0].value
            psu = selected[selected["model"] == "RM750x (2024) 750W 80+ Gold"].iloc[0]
            self.assertEqual(psu["indian_market_presence"], "No verified Indian listing")
            self.assertTrue(any(
                "no verified indian retailer listing was found for psu" in item.value.casefold()
                for item in app.warning
            ))

    def test_future_check_date_does_not_claim_available_offer_is_stale(self):
        app = self._run_synthetic_recommendation(
            600,
            available_cpu=True,
            checked_at="2099-01-01",
        )

        self.assertFalse(app.exception)
        selected = app.dataframe[0].value
        cpu = selected[selected["category"].str.casefold() == "cpu"].iloc[0]
        self.assertEqual(cpu["availability"], "available")
        self.assertEqual(cpu["availability_freshness"], "Check date unavailable")
        self.assertTrue(any(
            "freshness could not be determined from the recorded check date" in item.value
            and "not a live stock or delivery confirmation" in item.value
            for item in app.warning
        ))
        self.assertFalse(any(
            "outside the 7-day freshness window" in item.value
            for item in app.warning
        ))

    def test_default_price_selection_keeps_lowest_recorded_offer(self):
        app = self._run_synthetic_recommendation(
            600,
            prefer_available=False,
            include_availability_alternative=True,
        )

        self.assertFalse(app.exception)
        selected = app.dataframe[0].value
        cpu = selected[selected["category"].str.casefold() == "cpu"].iloc[0]
        self.assertEqual(cpu["price_inr"], 250)
        self.assertEqual(cpu["availability"], "unavailable")

    def test_does_not_return_a_build_over_budget(self):
        app = self._run_synthetic_recommendation(300)

        self.assertFalse(app.exception)
        self.assertFalse(app.dataframe)
        self.assertTrue(any(
            "No combination of recorded prices fits" in item.value
            for item in app.warning
        ))


if __name__ == "__main__":
    unittest.main()
