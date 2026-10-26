import csv
import json
from pathlib import Path
import unittest

from src.compatibility import (
    check_cpu_motherboard,
    check_cpu_motherboard_ram,
    check_gpu_case,
    check_motherboard_case,
    check_motherboard_ram_capacity,
    check_psu,
    check_storage_motherboard,
    check_cooler_socket,
    check_cooler_case,
    check_cooler,
    check_ram_speed_qvl,
)


class CompatibilityTests(unittest.TestCase):
    def setUp(self):
        self.cpu = {
            "socket": "AM5",
            "supported_chipsets": ["B650", "B850"],
            "ram_type": "DDR5",
            "minimum_bios_version": "1.20",
        }
        self.motherboard = {
            "socket": "AM5",
            "chipset": "B650",
            "form_factor": "ATX",
            "ram_type": "DDR5",
            "bios_version": "1.20",
        }
        self.ram = {"ram_type": "DDR5"}
        self.case = {
            "supports_form_factors": ["ATX", "mATX"],
            "max_gpu_length_mm": 340,
            "max_cpu_cooler_mm": 170,
        }
        self.cooler = {
            "socket_support": ["AM5", "AM4", "LGA1700"],
            "height_mm": 155,
        }
        self.gpu = {
            "length_mm": 320,
            "recommended_system_psu_w": 750,
            "required_power_connectors": {"16-pin": 1},
        }
        self.psu = {
            "wattage_w": 750,
            "power_connectors": {"16-pin": 1},
        }

    def test_cpu_motherboard_matching_socket_chipset_and_bios(self):
        result = check_cpu_motherboard(self.cpu, self.motherboard)
        self.assertEqual(result.status, "compatible")
        self.assertIn("socket match", result.reason)
        self.assertIn("chipset B650", result.reason)
        self.assertIn("BIOS 1.20", result.reason)

    def test_cpu_motherboard_socket_mismatch(self):
        wrong_socket = dict(self.motherboard, socket="LGA1700")
        self.assertEqual(check_cpu_motherboard(self.cpu, wrong_socket).status, "incompatible")

    def test_cpu_motherboard_genuine_chipset_mismatch(self):
        unsupported_chipset = dict(self.motherboard, chipset="Z890")
        self.assertEqual(check_cpu_motherboard(self.cpu, unsupported_chipset).status, "incompatible")

    def test_cpu_motherboard_vendor_prefix_chipset_match(self):
        cpu = dict(self.cpu, supported_chipsets=["B850"])
        motherboard = dict(self.motherboard, chipset="AMD B850")

        result = check_cpu_motherboard(cpu, motherboard)

        self.assertEqual(result.status, "compatible")
        self.assertIn("chipset AMD B850 as supported", result.reason)

    def test_cpu_motherboard_missing_chipset_is_unknown(self):
        motherboard = dict(self.motherboard, chipset="")

        result = check_cpu_motherboard(self.cpu, motherboard)

        self.assertEqual(result.status, "unknown")
        self.assertIn("motherboard chipset specification is missing", result.reason)

    def test_cpu_motherboard_missing_specs_or_bios_is_unknown(self):
        missing_socket = dict(self.motherboard, socket="")
        self.assertEqual(check_cpu_motherboard(self.cpu, missing_socket).status, "unknown")

        without_bios = dict(self.motherboard)
        without_bios.pop("bios_version")
        result = check_cpu_motherboard(self.cpu, without_bios)
        self.assertEqual(result.status, "unknown")
        self.assertIn("BIOS version is not documented", result.reason)

        no_minimum = dict(self.cpu)
        no_minimum.pop("minimum_bios_version")
        self.assertEqual(check_cpu_motherboard(no_minimum, self.motherboard).status, "unknown")

    def test_blank_or_empty_supported_specs_are_unknown(self):
        blank_socket = dict(self.motherboard, socket="  ")
        result = check_cpu_motherboard(self.cpu, blank_socket)
        self.assertEqual(result.status, "unknown")
        self.assertIn("socket specification is missing", result.reason)

        no_chipset_data = dict(self.cpu, supported_chipsets=[])
        result = check_cpu_motherboard(no_chipset_data, self.motherboard)
        self.assertEqual(result.status, "unknown")
        self.assertIn("list is empty", result.reason)

        no_case_support_data = dict(self.case, supports_form_factors=[])
        result = check_motherboard_case(self.motherboard, no_case_support_data)
        self.assertEqual(result.status, "unknown")
        self.assertIn("list is empty", result.reason)

    def test_non_finite_dimensions_and_capacity_are_unknown(self):
        invalid_gpu = dict(self.gpu, length_mm=float("nan"))
        self.assertEqual(check_gpu_case(invalid_gpu, self.case).status, "unknown")

        infinite_clearance = dict(self.case, max_gpu_length_mm=float("inf"))
        self.assertEqual(check_gpu_case(self.gpu, infinite_clearance).status, "unknown")

        infinite_capacity = dict(self.psu, wattage_w=float("inf"))
        self.assertEqual(
            check_psu(infinite_capacity, self.cpu, self.gpu).status,
            "unknown",
        )

    def test_cpu_motherboard_outdated_bios_is_incompatible(self):
        old_bios = dict(self.motherboard, bios_version="1.10")
        result = check_cpu_motherboard(self.cpu, old_bios)
        self.assertEqual(result.status, "incompatible")
        self.assertIn("older than", result.reason)

    def test_ram_type_match_mismatch_and_missing(self):
        self.assertEqual(
            check_cpu_motherboard_ram(self.cpu, self.motherboard, self.ram).status,
            "compatible",
        )
        mismatched = check_cpu_motherboard_ram(
            self.cpu, self.motherboard, {"ram_type": "DDR4"}
        )
        self.assertEqual(mismatched.status, "incompatible")
        self.assertIn("DDR4", mismatched.reason)
        missing = check_cpu_motherboard_ram(self.cpu, self.motherboard, {})
        self.assertEqual(missing.status, "unknown")

    def test_motherboard_case_form_factor_match_mismatch_and_missing(self):
        self.assertEqual(check_motherboard_case(self.motherboard, self.case).status, "compatible")
        unsupported_case = dict(self.case, supports_form_factors=["ITX"])
        self.assertEqual(
            check_motherboard_case(self.motherboard, unsupported_case).status,
            "incompatible",
        )
        self.assertEqual(check_motherboard_case({}, self.case).status, "unknown")

    def test_motherboard_case_recognizes_documented_form_factor_aliases(self):
        micro_atx_board = dict(self.motherboard, form_factor="Micro-ATX")
        matx_case = dict(self.case, supports_form_factors=["mATX"])
        self.assertEqual(
            check_motherboard_case(micro_atx_board, matx_case).status,
            "compatible",
        )

        mini_itx_board = dict(self.motherboard, form_factor="Mini-ITX")
        itx_case = dict(self.case, supports_form_factors=["ITX"])
        self.assertEqual(
            check_motherboard_case(mini_itx_board, itx_case).status,
            "compatible",
        )
        ambiguous_board = dict(self.motherboard, form_factor="XL-ATX")
        self.assertEqual(
            check_motherboard_case(ambiguous_board, self.case).status,
            "unknown",
        )

    def test_catalogued_micro_atx_board_fits_case_listing_matx(self):
        components_path = Path(__file__).resolve().parents[1] / "data" / "components.csv"
        with components_path.open(encoding="utf-8-sig", newline="") as components_file:
            components = {
                row["component_id"]: json.loads(row["specs_json"])
                for row in csv.DictReader(components_file)
                if row["component_id"] in {
                    "mb-asrock-a620am-x",
                    "case-pop-air-mini",
                }
            }

        result = check_motherboard_case(
            components["mb-asrock-a620am-x"],
            components["case-pop-air-mini"],
        )

        self.assertEqual(result.status, "compatible")

    def test_motherboard_ram_capacity_match_mismatch_and_missing(self):
        motherboard = dict(self.motherboard, ram_max_gb=64)
        ram = {"capacity_gb": 32}
        self.assertEqual(
            check_motherboard_ram_capacity(motherboard, ram).status,
            "compatible",
        )

        oversized_ram = {"capacity_gb": 128}
        result = check_motherboard_ram_capacity(motherboard, oversized_ram)
        self.assertEqual(result.status, "incompatible")
        self.assertIn("exceeds the motherboard maximum", result.reason)

        self.assertEqual(
            check_motherboard_ram_capacity(motherboard, {}).status,
            "unknown",
        )
        self.assertEqual(
            check_motherboard_ram_capacity({}, ram).status,
            "unknown",
        )

    def test_storage_motherboard_explicit_interface_and_form_factor_checks(self):
        storage = {
            "interface": "NVMe Gen5 x4",
            "form_factor": "M.2 2280",
        }
        motherboard = {
            "supported_storage_interfaces": ["NVMe"],
            "supported_m2_form_factors": ["M.2 2280"],
        }
        result = check_storage_motherboard(storage, motherboard)
        self.assertEqual(result.status, "compatible")
        self.assertIn("storage interface NVME as supported", result.reason)
        self.assertIn("documents support for M.2 form factor M.2 2280", result.reason)

        unsupported = dict(
            motherboard,
            supported_storage_interfaces=["SATA"],
            supported_m2_form_factors=["M.2 2242"],
            supported_m2_form_factors_complete=True,
        )
        result = check_storage_motherboard(storage, unsupported)
        self.assertEqual(result.status, "incompatible")
        self.assertIn("does not list the storage interface NVME", result.reason)
        self.assertIn("does not support M.2 form factor M.2 2280", result.reason)

    def test_catalogued_asus_b850_supports_samsung_990_pro_1tb(self):
        components_path = Path(__file__).resolve().parents[1] / "data" / "components.csv"
        with components_path.open(encoding="utf-8-sig", newline="") as components_file:
            components = {
                row["component_id"]: json.loads(row["specs_json"])
                for row in csv.DictReader(components_file)
                if row["component_id"] in {
                    "mb-asus-tuf-gaming-b850-plus-wifi",
                    "samsung-990-pro-1tb",
                }
            }

        motherboard = components["mb-asus-tuf-gaming-b850-plus-wifi"]
        result = check_storage_motherboard(
            components["samsung-990-pro-1tb"],
            motherboard,
        )

        self.assertEqual(result.status, "compatible")
        self.assertTrue(motherboard["supported_m2_form_factors_complete"])
        self.assertIn("dlcdnets.asus.com", motherboard["storage_spec_source"])
        self.assertEqual(motherboard["storage_spec_verified_at"], "2026-10-23")

    def test_storage_motherboard_missing_or_ambiguous_evidence_is_unknown(self):
        storage = {"interface": "PCIe storage", "form_factor": "M.2 2280"}
        motherboard = {
            "supported_storage_interfaces": ["PCIe"],
            "supported_m2_form_factors": ["M.2 2280"],
        }
        result = check_storage_motherboard(storage, motherboard)
        self.assertEqual(result.status, "unknown")
        self.assertIn("unrecognized format", result.reason)

        result = check_storage_motherboard(
            {"interface": "NVMe Gen4 x4", "form_factor": "M.2 2280"},
            {},
        )
        self.assertEqual(result.status, "unknown")
        self.assertIn("not documented", result.reason)

    def test_storage_size_is_not_compared_to_motherboard_when_not_m2(self):
        result = check_storage_motherboard(
            {"interface": "SATA III 6Gb/s", "form_factor": "2.5-inch"},
            {"supported_storage_interfaces": ["SATA"]},
        )

        self.assertEqual(result.status, "compatible")
        self.assertNotIn("form factor", result.reason)

    def test_gpu_case_clearance_match_mismatch_and_missing(self):
        self.assertEqual(check_gpu_case(self.gpu, self.case).status, "compatible")
        too_long = dict(self.gpu, length_mm=350)
        result = check_gpu_case(too_long, self.case)
        self.assertEqual(result.status, "incompatible")
        self.assertIn("exceeds case clearance", result.reason)
        self.assertEqual(check_gpu_case({}, self.case).status, "unknown")

    def test_psu_documented_wattage_and_connector_match(self):
        result = check_psu(self.psu, self.cpu, self.gpu)
        self.assertEqual(result.status, "compatible")
        self.assertIn("recommended system PSU capacity of 750 W", result.reason)
        self.assertIn("lists all GPU-required power connectors", result.reason)

    def test_catalogued_asus_gpu_and_corsair_psu_are_compatible(self):
        components_path = Path(__file__).resolve().parents[1] / "data" / "components.csv"
        with components_path.open(encoding="utf-8-sig", newline="") as components_file:
            components = {
                row["component_id"]: json.loads(row["specs_json"])
                for row in csv.DictReader(components_file)
                if row["component_id"] in {
                    "gpu-nvidia-asus-prime-rtx5070-o12g",
                    "psu-750w-gold",
                }
            }

        result = check_psu(
            components["psu-750w-gold"],
            {},
            components["gpu-nvidia-asus-prime-rtx5070-o12g"],
        )
        self.assertEqual(result.status, "compatible")
        self.assertIn("recommended system PSU capacity of 750 W", result.reason)

    def test_catalogued_9600x_and_asus_b850_have_documented_bios_support(self):
        components_path = Path(__file__).resolve().parents[1] / "data" / "components.csv"
        with components_path.open(encoding="utf-8-sig", newline="") as components_file:
            components = {
                row["component_id"]: json.loads(row["specs_json"])
                for row in csv.DictReader(components_file)
                if row["component_id"] in {
                    "cpu-r5-9600x",
                    "mb-asus-tuf-gaming-b850-plus-wifi",
                }
            }

        result = check_cpu_motherboard(
            components["cpu-r5-9600x"],
            components["mb-asus-tuf-gaming-b850-plus-wifi"],
            cpu_component_id="cpu-r5-9600x",
        )

        self.assertEqual(result.status, "compatible")
        self.assertIn("socket match (AM5)", result.reason)
        self.assertIn("chipset AMD B850 as supported", result.reason)
        self.assertIn("validates this CPU since all BIOS versions", result.reason)
        self.assertIn("checked 2026-10-23", result.reason)

    def test_other_catalogued_cpu_motherboard_pair_without_bios_evidence_is_unknown(self):
        components_path = Path(__file__).resolve().parents[1] / "data" / "components.csv"
        with components_path.open(encoding="utf-8-sig", newline="") as components_file:
            components = {
                row["component_id"]: json.loads(row["specs_json"])
                for row in csv.DictReader(components_file)
                if row["component_id"] in {
                    "cpu-r5-9600x",
                    "mb-b650-tomahawk",
                }
            }

        result = check_cpu_motherboard(
            components["cpu-r5-9600x"],
            components["mb-b650-tomahawk"],
            cpu_component_id="cpu-r5-9600x",
        )

        self.assertEqual(result.status, "unknown")
        self.assertIn("No minimum BIOS requirement is documented", result.reason)

    def test_psu_insufficient_wattage_is_incompatible(self):
        insufficient_capacity = dict(self.psu, wattage_w=600)
        result = check_psu(insufficient_capacity, self.cpu, self.gpu)
        self.assertEqual(result.status, "incompatible")
        self.assertIn("below the recommended system PSU capacity", result.reason)

    def test_psu_missing_connector_inventory_is_unknown(self):
        missing_connector = dict(self.psu, power_connectors={})
        result = check_psu(missing_connector, self.cpu, self.gpu)
        self.assertEqual(result.status, "unknown")
        self.assertIn("connector compatibility is unknown", result.reason)

    def test_psu_missing_gpu_power_requirement_is_unknown(self):
        no_gpu_power_requirement = dict(self.gpu)
        no_gpu_power_requirement.pop("recommended_system_psu_w")
        no_gpu_power_requirement.pop("required_psu_w", None)
        cpu_only_requirement = dict(self.cpu, required_psu_w=500)
        result = check_psu(self.psu, cpu_only_requirement, no_gpu_power_requirement)
        self.assertEqual(result.status, "unknown")
        self.assertIn("GPU/system PSU requirement is missing", result.reason)

    def test_psu_missing_gpu_connector_requirement_is_unknown(self):
        no_required_connectors = dict(self.gpu)
        no_required_connectors.pop("required_power_connectors")
        result = check_psu(self.psu, self.cpu, no_required_connectors)
        self.assertEqual(result.status, "unknown")
        self.assertIn("GPU required power connectors are not documented", result.reason)

    def test_psu_missing_wattage_is_unknown(self):
        self.assertEqual(check_psu({}, self.cpu, self.gpu).status, "unknown")

    def test_psu_without_discrete_gpu_requirement_is_unknown(self):
        result = check_psu(self.psu, self.cpu, {})

        self.assertEqual(result.status, "unknown")
        self.assertIn("documented GPU/system PSU requirement is missing", result.reason)
        self.assertIn("GPU required power connectors are not documented", result.reason)

    def test_availability_metadata_does_not_change_compatibility(self):
        checks = (
            (
                check_cpu_motherboard,
                (self.cpu, self.motherboard),
                (self.cpu, dict(self.motherboard, availability="unavailable")),
            ),
            (
                check_cpu_motherboard_ram,
                (self.cpu, self.motherboard, self.ram),
                (
                    self.cpu,
                    self.motherboard,
                    dict(self.ram, availability="unknown"),
                ),
            ),
            (
                check_motherboard_case,
                (self.motherboard, self.case),
                (
                    self.motherboard,
                    dict(self.case, availability="unavailable"),
                ),
            ),
            (
                check_gpu_case,
                (self.gpu, self.case),
                (
                    self.gpu,
                    dict(self.case, availability="unknown"),
                ),
            ),
            (
                check_psu,
                (self.psu, self.cpu, self.gpu),
                (
                    dict(self.psu, availability="unavailable"),
                    self.cpu,
                    self.gpu,
                ),
            ),
        )
        for check, baseline_specs, metadata_specs in checks:
            with self.subTest(check=check.__name__):
                self.assertEqual(
                    check(*metadata_specs),
                    check(*baseline_specs),
                )


    def test_ak400_black_cooler_socket_and_height_clearance_pass(self):
        # 1. DeepCool AK400 Black with an AM5 CPU and a case supporting 170 mm coolers
        socket_result = check_cooler_socket(self.cooler, self.cpu, self.motherboard)
        self.assertEqual(socket_result.status, "compatible")
        self.assertIn("support for socket AM5", socket_result.reason)

        height_result = check_cooler_case(self.cooler, self.case)
        self.assertEqual(height_result.status, "compatible")
        self.assertIn("155 mm is within case clearance of 170 mm", height_result.reason)
        self.assertIn("15 mm clearance", height_result.reason)

        combined = check_cooler(self.cooler, self.cpu, self.case, self.motherboard)
        self.assertEqual(combined.status, "compatible")

    def test_cooler_socket_mismatch_is_incompatible(self):
        # 2. Cooler socket mismatch: incompatible
        intel_only_cooler = {
            "socket_support": ["LGA1700", "LGA1200"],
            "height_mm": 155,
        }
        result = check_cooler_socket(intel_only_cooler, self.cpu)
        self.assertEqual(result.status, "incompatible")
        self.assertIn("does not list support for socket AM5", result.reason)

    def test_cooler_taller_than_case_limit_is_incompatible(self):
        # 3. Cooler taller than the case limit: incompatible
        tall_cooler = {"height_mm": 175}
        result = check_cooler_case(tall_cooler, self.case)
        self.assertEqual(result.status, "incompatible")
        self.assertIn("exceeds case clearance of 170 mm (by 5 mm)", result.reason)

    def test_missing_cooler_socket_information_is_unknown(self):
        # 4. Missing cooler socket information: unknown
        result_no_sockets = check_cooler_socket({}, self.cpu)
        self.assertEqual(result_no_sockets.status, "unknown")
        self.assertIn("supported socket specification is missing", result_no_sockets.reason)

        result_no_cpu_socket = check_cooler_socket(self.cooler, {})
        self.assertEqual(result_no_cpu_socket.status, "unknown")
        self.assertIn("socket specifications are missing", result_no_cpu_socket.reason)

    def test_missing_cooler_height_or_case_clearance_is_unknown(self):
        # 5. Missing cooler height or case clearance: unknown
        result_no_height = check_cooler_case({}, self.case)
        self.assertEqual(result_no_height.status, "unknown")
        self.assertIn("Cooler height or case maximum CPU cooler clearance is missing", result_no_height.reason)

        result_no_clearance = check_cooler_case(self.cooler, {})
        self.assertEqual(result_no_clearance.status, "unknown")
        self.assertIn("Cooler height or case maximum CPU cooler clearance is missing", result_no_clearance.reason)

    def test_exact_zero_clearance_fits_geometrically_and_reports_zero_clearance(self):
        # 6. Exact zero clearance: fits geometrically, but report 0 mm clearance
        exact_fit_cooler = {"height_mm": 170}
        result = check_cooler_case(exact_fit_cooler, self.case)
        self.assertEqual(result.status, "compatible")
        self.assertIn("0 mm clearance", result.reason)
        self.assertIn("170 mm is within case clearance of 170 mm", result.reason)

    def test_ram_speed_qvl_expo_profile_unlisted_is_unknown(self):
        ram_expo = {"ram_type": "DDR5", "speed_mtps": 6000}
        board_no_qvl = {"socket": "AM5", "chipset": "B850"}
        result = check_ram_speed_qvl(ram_expo, board_no_qvl, "gskill-flare-x5-ddr5-6000-cl36-32gb")
        self.assertEqual(result.status, "unknown")
        self.assertIn("unlisted on the motherboard memory QVL", result.reason)

        board_with_qvl = {
            "socket": "AM5",
            "chipset": "B850",
            "memory_qvl": ["gskill-flare-x5-ddr5-6000-cl36-32gb"],
        }
        result_ok = check_ram_speed_qvl(ram_expo, board_with_qvl, "gskill-flare-x5-ddr5-6000-cl36-32gb")
        self.assertEqual(result_ok.status, "compatible")
        self.assertIn("validated on the motherboard memory QVL", result_ok.reason)

        ram_jedec = {"ram_type": "DDR5", "speed_mtps": 4800}
        result_jedec = check_ram_speed_qvl(ram_jedec, board_no_qvl)
        self.assertEqual(result_jedec.status, "compatible")
        self.assertIn("standard JEDEC baseline", result_jedec.reason)

    def test_ddr5_5600_not_automatically_classified_as_expo_xmp(self):
        """Clarifies that DDR5-5600 test uses an unlisted kit (operating within standard JEDEC
        baseline specifications without being listed on the motherboard QVL).
        Verifies:
        1. An unlisted DDR5-5600 kit is not falsely assumed to be an EXPO/XMP overclock profile.
        2. Its status is compatible under standard baseline operation, but its reason states baseline
           operation and does NOT claim full motherboard QVL validation.
        3. Contrasted with an officially QVL-listed DDR5-5600 kit, which explicitly reports QVL validation.
        """
        # Unlisted board (no memory_qvl documentation)
        board_unlisted = {"socket": "AM5", "chipset": "B850"}

        # 1. Unlisted kit with explicit JEDEC profile DDR5-5600:
        # Passes as compatible under standard JEDEC baseline without claiming QVL validation.
        ram_jedec = {"ram_type": "DDR5", "speed_mtps": 5600, "profile": "JEDEC"}
        result_jedec = check_ram_speed_qvl(ram_jedec, board_unlisted, "crucial-ddr5-5600-unlisted")
        self.assertEqual(result_jedec.status, "compatible")
        self.assertNotIn("EXPO", result_jedec.reason)
        self.assertNotIn("overclock", result_jedec.reason.casefold())
        self.assertNotIn("validated on the motherboard", result_jedec.reason)
        self.assertIn("standard JEDEC profile", result_jedec.reason)

        # 2. Unlisted kit with unspecified profile DDR5-5600:
        # Should not be assumed EXPO/XMP solely because it exceeds 5200 MT/s.
        # Operates within standard baseline specifications without claiming QVL validation.
        ram_unspecified = {"ram_type": "DDR5", "speed_mtps": 5600}
        result_unspecified = check_ram_speed_qvl(ram_unspecified, board_unlisted, "generic-ddr5-5600-unlisted")
        self.assertEqual(result_unspecified.status, "compatible")
        self.assertIn("not classified as EXPO/XMP", result_unspecified.reason)
        self.assertNotIn("validated on the motherboard", result_unspecified.reason)
        self.assertIn("within standard JEDEC baseline specifications", result_unspecified.reason)

        # 3. Contrasting QVL-listed DDR5-5600 kit:
        # Officially listed on motherboard QVL reports exact QVL validation.
        board_with_qvl = {
            "socket": "AM5",
            "chipset": "B850",
            "memory_qvl": ["crucial-ddr5-5600-ct16g56c46u5"],
        }
        result_qvl = check_ram_speed_qvl(
            ram_jedec,
            board_with_qvl,
            ram_component_id="crucial-ddr5-5600-ct16g56c46u5",
        )
        self.assertEqual(result_qvl.status, "compatible")
        self.assertIn("validated on the motherboard memory QVL", result_qvl.reason)

    def test_explicit_expo_profile_evaluated_separately_from_ddr_generation(self):
        board = {"socket": "AM5", "chipset": "B850", "ram_type": "DDR5"}
        cpu = {"socket": "AM5", "ram_type": "DDR5"}
        ram = {"ram_type": "DDR5", "speed_mtps": 6000, "profile": "EXPO"}

        # Basic generation check passes
        gen_result = check_cpu_motherboard_ram(cpu, board, ram)
        self.assertEqual(gen_result.status, "compatible")

        # Explicit EXPO profile evaluated separately against board QVL
        qvl_result = check_ram_speed_qvl(ram, board)
        self.assertEqual(qvl_result.status, "unknown")
        self.assertIn("EXPO", qvl_result.reason)
        self.assertIn("unlisted on the motherboard memory QVL", qvl_result.reason)

    def test_ram_missing_from_motherboard_qvl_remains_unverified_not_incompatible(self):
        board_with_other_qvl = {
            "socket": "AM5",
            "chipset": "B850",
            "memory_qvl": ["corsair-vengeance-32gb"],
            "memory_qvl_complete": True,
        }
        ram_expo = {
            "ram_type": "DDR5",
            "speed_mtps": 6000,
            "profile": "EXPO",
            "part_number": "F5-6000J3636F16GX2-FX5",
        }
        result = check_ram_speed_qvl(ram_expo, board_with_other_qvl, "gskill-flare-x5")
        self.assertEqual(result.status, "unknown")
        self.assertNotEqual(result.status, "incompatible")
        self.assertIn("unlisted on the motherboard memory QVL", result.reason)

    def test_missing_memory_profile_information_returns_honest_unknown(self):
        board = {"socket": "AM5", "chipset": "B850"}
        # High speed kit with no profile (no JEDEC, EXPO, or XMP documented)
        ram_high_speed_no_profile = {"ram_type": "DDR5", "speed_mtps": 6000}
        result = check_ram_speed_qvl(ram_high_speed_no_profile, board)
        self.assertEqual(result.status, "unknown")
        self.assertIn("memory profile information (JEDEC vs EXPO/XMP) is unverified", result.reason)

    def test_cpu_specific_dimm_configuration_limits_respected(self):
        board = {"socket": "AM5", "chipset": "B850"}
        cpu_dimm_limits = {
            "socket": "AM5",
            "ram_type": "DDR5",
            "memory_support_by_dimm_config": {"2_dimm": 5600, "4_dimm": 3600},
        }

        # 2-DIMM kit at 5600 MT/s is within CPU limit
        ram_2dimm = {"ram_type": "DDR5", "speed_mtps": 5600, "kit": "2x16GB"}
        res_2dimm = check_ram_speed_qvl(ram_2dimm, board, cpu_specs=cpu_dimm_limits)
        self.assertEqual(res_2dimm.status, "compatible")
        self.assertIn("within the CPU's documented limit", res_2dimm.reason)

        # 4-DIMM kit at 5600 MT/s exceeds CPU limit of 3600 MT/s
        ram_4dimm = {"ram_type": "DDR5", "speed_mtps": 5600, "kit": "4x16GB"}
        res_4dimm = check_ram_speed_qvl(ram_4dimm, board, cpu_specs=cpu_dimm_limits)
        self.assertEqual(res_4dimm.status, "unknown")
        self.assertIn("exceeds the CPU's documented limit of 3600 MT/s for 4-DIMM", res_4dimm.reason)


if __name__ == "__main__":
    unittest.main()
