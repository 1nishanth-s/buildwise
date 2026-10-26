"""Conservative hardware compatibility checks based on documented specifications."""
from __future__ import annotations

from dataclasses import dataclass
import math
import re
from typing import Any, Literal, Mapping

CompatibilityStatus = Literal["compatible", "incompatible", "unknown"]


@dataclass(frozen=True)
class CompatibilityResult:
    status: CompatibilityStatus
    reason: str


def _missing(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    return isinstance(value, float) and not math.isfinite(value)


def _value(specs: Mapping[str, Any], key: str) -> Any:
    value = specs.get(key)
    return None if _missing(value) else value


def _normalize(value: Any) -> str:
    return str(value).strip().casefold()


def _normalize_chipset(value: Any) -> str:
    normalized = _normalize(value)
    for vendor_prefix in ("amd ", "intel "):
        if normalized.startswith(vendor_prefix):
            return normalized[len(vendor_prefix):]
    return normalized


def _normalize_form_factor(value: Any) -> str:
    normalized = _normalize(value).replace("_", "-")
    aliases = {
        "micro-atx": "matx",
        "micro atx": "matx",
        "mini-itx": "itx",
        "mini itx": "itx",
    }
    normalized = aliases.get(normalized, normalized)
    return normalized if normalized in {"atx", "matx", "itx"} else ""


def _normalize_storage_interface(value: Any) -> str | None:
    normalized = _normalize(value)
    if re.fullmatch(r"nvme(?: gen\d+(?: x\d+)?)?", normalized):
        return "nvme"
    if normalized in {"sata", "sata iii 6gb/s"}:
        return "sata"
    return None


def _number(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) and number > 0 else None


def _count(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) and number >= 0 else None


def _version_parts(value: Any) -> tuple[int, ...] | None:
    parts = str(value).split(".")
    if not parts or any(not part.isdigit() for part in parts):
        return None
    return tuple(int(part) for part in parts)


def _combine(results: list[CompatibilityResult]) -> CompatibilityResult:
    if any(result.status == "incompatible" for result in results):
        status: CompatibilityStatus = "incompatible"
    elif any(result.status == "unknown" for result in results):
        status = "unknown"
    else:
        status = "compatible"
    return CompatibilityResult(
        status=status,
        reason=" ".join(result.reason for result in results),
    )


def check_cpu_motherboard(
    cpu_specs: Mapping[str, Any],
    motherboard_specs: Mapping[str, Any],
    cpu_component_id: str | None = None,
) -> CompatibilityResult:
    results: list[CompatibilityResult] = []
    cpu_socket = _value(cpu_specs, "socket")
    board_socket = _value(motherboard_specs, "socket")
    if cpu_socket is None or board_socket is None:
        results.append(CompatibilityResult(
            "unknown", "CPU or motherboard socket specification is missing."
        ))
    elif _normalize(cpu_socket) != _normalize(board_socket):
        results.append(CompatibilityResult(
            "incompatible",
            f"CPU socket {cpu_socket} does not match motherboard socket {board_socket}.",
        ))
    else:
        results.append(CompatibilityResult(
            "compatible", f"CPU and motherboard socket match ({cpu_socket})."
        ))

    chipset = _value(motherboard_specs, "chipset")
    supported_chipsets = _value(cpu_specs, "supported_chipsets")
    if chipset is None or not isinstance(supported_chipsets, (list, tuple, set)):
        results.append(CompatibilityResult(
            "unknown",
            "CPU supported-chipset list or motherboard chipset specification is missing.",
        ))
    elif not any(not _missing(item) for item in supported_chipsets):
        results.append(CompatibilityResult(
            "unknown",
            "CPU supported-chipset list is empty or contains no usable values.",
        ))
    elif not any(
        not _missing(item) and _normalize_chipset(item) == _normalize_chipset(chipset)
        for item in supported_chipsets
    ):
        results.append(CompatibilityResult(
            "incompatible",
            f"Motherboard chipset {chipset} is not listed as supported by this CPU.",
        ))
    else:
        results.append(CompatibilityResult(
            "compatible", f"CPU specification lists chipset {chipset} as supported."
        ))

    board_bios = _value(motherboard_specs, "bios_version")
    requirements = _value(cpu_specs, "bios_requirements")
    required_bios = _value(cpu_specs, "minimum_bios_version")
    if isinstance(requirements, Mapping) and chipset is not None:
        required_bios = requirements.get(str(chipset), required_bios)
    pair_bios_support = motherboard_specs.get("cpu_bios_support")
    pair_bios_evidence = (
        pair_bios_support.get(cpu_component_id)
        if cpu_component_id
        and isinstance(pair_bios_support, Mapping)
        else None
    )
    validated_since_bios = (
        pair_bios_evidence.get("validated_since_bios")
        if isinstance(pair_bios_evidence, Mapping)
        else None
    )
    bios_source = (
        pair_bios_evidence.get("source")
        if isinstance(pair_bios_evidence, Mapping)
        else None
    )
    bios_checked_at = (
        pair_bios_evidence.get("checked_at")
        if isinstance(pair_bios_evidence, Mapping)
        else None
    )
    if (
        validated_since_bios == "all"
        and isinstance(bios_source, str)
        and bios_source.startswith(("https://", "http://"))
        and isinstance(bios_checked_at, str)
        and bios_checked_at.strip()
    ):
        results.append(CompatibilityResult(
            "compatible",
            f"Manufacturer support table validates this CPU since all BIOS versions for this motherboard (checked {bios_checked_at}).",
        ))
    elif required_bios is None:
        results.append(CompatibilityResult(
            "unknown",
            "No minimum BIOS requirement is documented for this CPU and motherboard pair.",
        ))
    elif board_bios is None:
        results.append(CompatibilityResult(
            "unknown",
            f"CPU requires BIOS {required_bios}, but the motherboard BIOS version is not documented.",
        ))
    else:
        required_parts = _version_parts(required_bios)
        installed_parts = _version_parts(board_bios)
        if required_parts is None or installed_parts is None:
            results.append(CompatibilityResult(
                "unknown",
                f"BIOS versions {board_bios} and {required_bios} cannot be compared safely.",
            ))
        elif installed_parts + (0,) * max(0, len(required_parts) - len(installed_parts)) < (
            required_parts + (0,) * max(0, len(installed_parts) - len(required_parts))
        ):
            results.append(CompatibilityResult(
                "incompatible",
                f"Motherboard BIOS {board_bios} is older than the CPU's required BIOS {required_bios}.",
            ))
        else:
            results.append(CompatibilityResult(
                "compatible",
                f"Motherboard BIOS {board_bios} meets the CPU's required BIOS {required_bios}.",
            ))
    return _combine(results)


def check_cpu_motherboard_ram(
    cpu_specs: Mapping[str, Any],
    motherboard_specs: Mapping[str, Any],
    ram_specs: Mapping[str, Any],
) -> CompatibilityResult:
    types = {
        "CPU": _value(cpu_specs, "ram_type"),
        "motherboard": _value(motherboard_specs, "ram_type"),
        "RAM": _value(ram_specs, "ram_type"),
    }
    if any(value is None for value in types.values()):
        return CompatibilityResult(
            "unknown",
            "CPU, motherboard, or RAM type specification is missing; memory compatibility cannot be confirmed.",
        )
    distinct_types = {_normalize(value) for value in types.values()}
    if len(distinct_types) > 1:
        details = ", ".join(f"{name} specifies {value}" for name, value in types.items())
        return CompatibilityResult("incompatible", f"Memory types do not match: {details}.")
    return CompatibilityResult(
        "compatible",
        f"CPU, motherboard, and RAM all specify {types['RAM']}.",
    )


def check_motherboard_ram_capacity(
    motherboard_specs: Mapping[str, Any],
    ram_specs: Mapping[str, Any],
) -> CompatibilityResult:
    maximum_capacity = _number(_value(motherboard_specs, "ram_max_gb"))
    ram_capacity = _number(_value(ram_specs, "capacity_gb"))
    if maximum_capacity is None or ram_capacity is None:
        return CompatibilityResult(
            "unknown",
            "Motherboard maximum memory capacity or RAM kit capacity is missing or invalid.",
        )
    if ram_capacity > maximum_capacity:
        return CompatibilityResult(
            "incompatible",
            f"RAM kit capacity {ram_capacity:g} GB exceeds the motherboard maximum of {maximum_capacity:g} GB.",
        )
    return CompatibilityResult(
        "compatible",
        f"RAM kit capacity {ram_capacity:g} GB is within the motherboard maximum of {maximum_capacity:g} GB.",
    )


def check_motherboard_case(
    motherboard_specs: Mapping[str, Any],
    case_specs: Mapping[str, Any],
) -> CompatibilityResult:
    board_form_factor = _value(motherboard_specs, "form_factor")
    supported = _value(case_specs, "supports_form_factors")
    if board_form_factor is None or not isinstance(supported, (list, tuple, set)):
        return CompatibilityResult(
            "unknown",
            "Motherboard form factor or the case's supported form factors are missing.",
        )
    normalized_board_form_factor = _normalize_form_factor(board_form_factor)
    if not normalized_board_form_factor:
        return CompatibilityResult(
            "unknown",
            f"Motherboard form factor {board_form_factor} is not recognized safely.",
        )
    if not any(not _missing(item) for item in supported):
        return CompatibilityResult(
            "unknown",
            "The case's supported form-factor list is empty or contains no usable values.",
        )
    normalized_supported = [
        _normalize_form_factor(item) for item in supported if not _missing(item)
    ]
    if any(not item for item in normalized_supported):
        return CompatibilityResult(
            "unknown",
            "Case supported-form-factor data contains an unrecognized format.",
        )
    if normalized_board_form_factor not in normalized_supported:
        return CompatibilityResult(
            "incompatible",
            f"Case does not list motherboard form factor {board_form_factor} as supported.",
        )
    return CompatibilityResult(
        "compatible",
        f"Case lists motherboard form factor {board_form_factor} as supported.",
    )


def check_storage_motherboard(
    storage_specs: Mapping[str, Any],
    motherboard_specs: Mapping[str, Any],
) -> CompatibilityResult:
    results: list[CompatibilityResult] = []
    storage_interface = _normalize_storage_interface(
        _value(storage_specs, "interface")
    )
    supported_interfaces = _value(motherboard_specs, "supported_storage_interfaces")
    if storage_interface is None:
        results.append(CompatibilityResult(
            "unknown",
            "Storage interface is missing or uses an unrecognized format.",
        ))
    elif not isinstance(supported_interfaces, (list, tuple, set)) or not supported_interfaces:
        results.append(CompatibilityResult(
            "unknown",
            "Motherboard supported storage interfaces are not documented.",
        ))
    else:
        normalized_interfaces = [
            _normalize_storage_interface(item)
            for item in supported_interfaces
            if not _missing(item)
        ]
        if not normalized_interfaces or any(
            item is None for item in normalized_interfaces
        ):
            results.append(CompatibilityResult(
                "unknown",
                "Motherboard storage-interface data contains an unrecognized format.",
            ))
        elif storage_interface not in normalized_interfaces:
            results.append(CompatibilityResult(
                "incompatible",
                f"Motherboard does not list the storage interface {storage_interface.upper()} as supported.",
            ))
        else:
            results.append(CompatibilityResult(
                "compatible",
                f"Motherboard lists the storage interface {storage_interface.upper()} as supported.",
            ))

    storage_form_factor = _value(storage_specs, "form_factor")
    supported_m2_form_factors = _value(
        motherboard_specs, "supported_m2_form_factors"
    )
    if storage_form_factor is not None and _normalize(storage_form_factor).startswith("m.2"):
        if not isinstance(supported_m2_form_factors, (list, tuple, set)) or not supported_m2_form_factors:
            results.append(CompatibilityResult(
                "unknown",
                "Motherboard supported M.2 module sizes are not documented.",
            ))
        else:
            normalized_m2_form_factors = {
                _normalize(item)
                for item in supported_m2_form_factors
                if not _missing(item)
            }
            if _normalize(storage_form_factor) in normalized_m2_form_factors:
                results.append(CompatibilityResult(
                    "compatible",
                    f"Motherboard documents support for M.2 form factor {storage_form_factor}.",
                ))
            elif motherboard_specs.get("supported_m2_form_factors_complete") is True:
                results.append(CompatibilityResult(
                    "incompatible",
                    f"Motherboard does not support M.2 form factor {storage_form_factor}.",
                ))
            else:
                results.append(CompatibilityResult(
                    "unknown",
                    f"Motherboard's documented M.2 sizes do not establish support for {storage_form_factor}.",
                ))
    elif storage_form_factor is None:
        results.append(CompatibilityResult(
            "unknown",
            "Storage form factor is missing.",
        ))
    return _combine(results)


def check_gpu_case(gpu_specs: Mapping[str, Any], case_specs: Mapping[str, Any]) -> CompatibilityResult:
    gpu_length = _number(_value(gpu_specs, "length_mm"))
    clearance = _number(_value(case_specs, "max_gpu_length_mm"))
    if gpu_length is None or clearance is None:
        return CompatibilityResult(
            "unknown",
            "GPU length or case maximum GPU clearance is missing or invalid.",
        )
    if gpu_length > clearance:
        return CompatibilityResult(
            "incompatible",
            f"GPU length {gpu_length:g} mm exceeds case clearance {clearance:g} mm.",
        )
    return CompatibilityResult(
        "compatible",
        f"GPU length {gpu_length:g} mm is within case clearance {clearance:g} mm.",
    )


def check_psu(
    psu_specs: Mapping[str, Any],
    cpu_specs: Mapping[str, Any],
    gpu_specs: Mapping[str, Any],
) -> CompatibilityResult:
    results: list[CompatibilityResult] = []
    wattage = _number(_value(psu_specs, "wattage_w"))
    required_wattage = _number(_value(gpu_specs, "required_psu_w"))
    recommended_system_wattage = _number(
        _value(gpu_specs, "recommended_system_psu_w")
    )
    cpu_requirement = _number(_value(cpu_specs, "required_psu_w"))
    gpu_requirements = [
        value
        for value in (required_wattage, recommended_system_wattage)
        if value is not None
    ]
    requirements = [*gpu_requirements, cpu_requirement]
    requirements = [value for value in requirements if value is not None]
    if wattage is None or not gpu_requirements:
        results.append(CompatibilityResult(
            "unknown",
            "PSU wattage or a documented GPU/system PSU requirement is missing; capacity cannot be confirmed from TDP/TGP alone.",
        ))
    else:
        required = max(requirements)
        requirement_label = (
            "recommended system PSU capacity"
            if recommended_system_wattage is not None
            and required == recommended_system_wattage
            else "documented required PSU capacity"
        )
        if wattage < required:
            results.append(CompatibilityResult(
                "incompatible",
                f"PSU capacity {wattage:g} W is below the {requirement_label} of {required:g} W.",
            ))
        else:
            results.append(CompatibilityResult(
                "compatible",
                f"PSU capacity {wattage:g} W meets the {requirement_label} of {required:g} W.",
            ))

    required_connectors = _value(gpu_specs, "required_power_connectors")
    available_connectors = _value(psu_specs, "power_connectors")
    if not isinstance(required_connectors, Mapping) or not required_connectors:
        results.append(CompatibilityResult(
            "unknown",
            "GPU required power connectors are not documented.",
        ))
    elif not isinstance(available_connectors, Mapping):
        results.append(CompatibilityResult(
            "unknown",
            "PSU connector inventory is not documented.",
        ))
    else:
        missing_inventory = [
            f"{connector} requires {count}, but the PSU inventory does not document it"
            for connector, count in required_connectors.items()
            if connector not in available_connectors
            or _count(count) is None
            or _count(available_connectors.get(connector)) is None
        ]
        insufficient = [
            f"{connector} requires {count}, PSU lists {available_connectors[connector]}"
            for connector, count in required_connectors.items()
            if connector in available_connectors
            and _count(count) is not None
            and _count(available_connectors.get(connector)) is not None
            and float(available_connectors[connector]) < float(count)
        ]
        if insufficient:
            results.append(CompatibilityResult(
                "incompatible", "Power connector mismatch: " + "; ".join(insufficient) + "."
            ))
        elif missing_inventory:
            results.append(CompatibilityResult(
                "unknown", "Power connector compatibility is unknown: " + "; ".join(missing_inventory) + "."
            ))
        else:
            results.append(CompatibilityResult(
                "compatible", "PSU lists all GPU-required power connectors."
            ))
    return _combine(results)
def _normalize_socket(value: Any) -> str:
    normalized = _normalize(value)
    if normalized.startswith("socket "):
        normalized = normalized[len("socket "):].strip()
    return normalized.replace(" ", "").replace("-", "")


def check_cooler_socket(
    cooler_specs: Mapping[str, Any],
    cpu_specs: Mapping[str, Any],
    motherboard_specs: Mapping[str, Any] | None = None,
) -> CompatibilityResult:
    cpu_socket = _value(cpu_specs, "socket")
    board_socket = _value(motherboard_specs, "socket") if motherboard_specs else None

    if cpu_socket is None and board_socket is None:
        return CompatibilityResult(
            "unknown",
            "CPU and motherboard socket specifications are missing; cooler socket compatibility cannot be confirmed.",
        )

    target_socket = cpu_socket if cpu_socket is not None else board_socket

    supported_raw = _value(cooler_specs, "socket_support")
    if supported_raw is None:
        supported_raw = _value(cooler_specs, "supported_sockets")

    if supported_raw is None:
        return CompatibilityResult(
            "unknown",
            "Cooler supported socket specification is missing; socket compatibility cannot be confirmed.",
        )

    if isinstance(supported_raw, (list, tuple, set)):
        supported_list = [str(item).strip() for item in supported_raw if not _missing(item)]
    elif isinstance(supported_raw, str):
        supported_list = [item.strip() for item in supported_raw.split(",") if item.strip()]
    else:
        return CompatibilityResult(
            "unknown",
            "Cooler supported socket data contains an unrecognized format.",
        )

    if not supported_list:
        return CompatibilityResult(
            "unknown",
            "Cooler supported socket list is empty or contains no usable values.",
        )

    normalized_supported = {_normalize_socket(item) for item in supported_list}
    normalized_target = _normalize_socket(target_socket)

    if normalized_target in normalized_supported:
        if board_socket and cpu_socket and _normalize(cpu_socket) == _normalize(board_socket):
            return CompatibilityResult(
                "compatible",
                f"Cooler documents support for socket {target_socket} (matches CPU and motherboard).",
            )
        return CompatibilityResult(
            "compatible",
            f"Cooler documents support for socket {target_socket}.",
        )

    return CompatibilityResult(
        "incompatible",
        f"Cooler does not list support for socket {target_socket}; documented supported sockets: {', '.join(supported_list)}.",
    )


def check_cooler_case(
    cooler_specs: Mapping[str, Any],
    case_specs: Mapping[str, Any],
) -> CompatibilityResult:
    cooler_height = _number(_value(cooler_specs, "height_mm"))
    if cooler_height is None:
        cooler_height = _number(_value(cooler_specs, "cooler_height_mm"))
    if cooler_height is None:
        cooler_height = _number(_value(cooler_specs, "height"))

    case_clearance = _number(_value(case_specs, "max_cpu_cooler_mm"))
    if case_clearance is None:
        case_clearance = _number(_value(case_specs, "max_cooler_height_mm"))
    if case_clearance is None:
        case_clearance = _number(_value(case_specs, "cpu_cooler_clearance_mm"))

    if cooler_height is None or case_clearance is None:
        return CompatibilityResult(
            "unknown",
            "Cooler height or case maximum CPU cooler clearance is missing or invalid.",
        )

    clearance_margin = case_clearance - cooler_height

    if cooler_height > case_clearance:
        return CompatibilityResult(
            "incompatible",
            f"Cooler height {cooler_height:g} mm exceeds case clearance of {case_clearance:g} mm (by {abs(clearance_margin):g} mm).",
        )

    return CompatibilityResult(
        "compatible",
        f"Cooler height {cooler_height:g} mm is within case clearance of {case_clearance:g} mm ({clearance_margin:g} mm clearance).",
    )


def check_cooler(
    cooler_specs: Mapping[str, Any],
    cpu_specs: Mapping[str, Any],
    case_specs: Mapping[str, Any],
    motherboard_specs: Mapping[str, Any] | None = None,
) -> CompatibilityResult:
    return _combine([
        check_cooler_socket(cooler_specs, cpu_specs, motherboard_specs),
        check_cooler_case(cooler_specs, case_specs),
    ])


def _extract_dimm_count(ram_specs: Mapping[str, Any]) -> int | None:
    for key in ("dimm_count", "modules", "sticks", "module_count"):
        val = _count(_value(ram_specs, key))
        if val is not None and val > 0:
            return int(val)
    kit = _value(ram_specs, "kit")
    if isinstance(kit, str):
        match = re.match(r"^(\d+)\s*[xX]", kit.strip())
        if match:
            return int(match.group(1))
    return None


def _extract_memory_profile(ram_specs: Mapping[str, Any]) -> str | None:
    for key in ("profile", "memory_profile", "profile_type"):
        val = ram_specs.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip().casefold()
    profiles = ram_specs.get("profiles")
    if isinstance(profiles, (list, tuple, set)):
        items = [str(p).strip().casefold() for p in profiles if str(p).strip()]
        if items:
            return ", ".join(items)
    notes = str(ram_specs.get("notes") or "").casefold()
    has_expo = "expo" in notes
    has_xmp = "xmp" in notes
    has_jedec = "jedec" in notes
    if has_expo and has_xmp:
        return "expo, xmp"
    if has_expo:
        return "expo"
    if has_xmp:
        return "xmp"
    if has_jedec:
        return "jedec"
    return None


def _extract_cpu_memory_speed_limit(
    cpu_specs: Mapping[str, Any] | None,
    dimm_count: int | None,
) -> float | None:
    if not cpu_specs:
        return None
    for key in (
        "max_memory_speed_by_dimm_config",
        "memory_support_by_dimm_config",
        "max_memory_speed_by_dimms",
    ):
        config_map = cpu_specs.get(key)
        if isinstance(config_map, Mapping) and dimm_count is not None:
            for k, v in config_map.items():
                k_str = str(k).casefold().replace(" ", "")
                if k_str in {str(dimm_count), f"{dimm_count}_dimm", f"{dimm_count}dimm", f"{dimm_count}x"}:
                    num = _number(v)
                    if num is not None:
                        return num
    for key in ("max_memory_speed_mtps", "max_memory_speed", "max_ram_speed_mtps"):
        num = _number(cpu_specs.get(key))
        if num is not None:
            return num
    return None


def check_ram_speed_qvl(
    ram_specs: Mapping[str, Any],
    motherboard_specs: Mapping[str, Any],
    ram_component_id: str | None = None,
    cpu_specs: Mapping[str, Any] | None = None,
) -> CompatibilityResult:
    speed = _number(_value(ram_specs, "speed_mtps"))
    if speed is None:
        speed = _number(_value(ram_specs, "speed"))

    if speed is None:
        return CompatibilityResult(
            "compatible",
            "RAM speed is not documented; baseline operation assumed.",
        )

    ram_type = _normalize(_value(ram_specs, "ram_type") or "")
    dimm_count = _extract_dimm_count(ram_specs)
    profile = _extract_memory_profile(ram_specs)
    cpu_limit = _extract_cpu_memory_speed_limit(cpu_specs, dimm_count)

    # 1. Check official motherboard QVL evidence if available
    memory_qvl = _value(motherboard_specs, "memory_qvl")
    if memory_qvl is None:
        memory_qvl = _value(motherboard_specs, "ram_qvl")

    if memory_qvl is not None and isinstance(memory_qvl, (list, tuple, set)):
        qvl_set = {_normalize(item) for item in memory_qvl if not _missing(item)}
        candidate_ids = {
            _normalize(ram_component_id) if ram_component_id else "",
            _normalize(_value(ram_specs, "part_number") or ""),
        }
        candidate_ids.discard("")
        if any(cid in qvl_set for cid in candidate_ids):
            profile_label = f" {profile.upper()} profile" if profile else ""
            return CompatibilityResult(
                "compatible",
                f"RAM{profile_label} ({speed:g} MT/s) is validated on the motherboard memory QVL.",
            )

    # 2. Evaluate explicitly documented EXPO or XMP profile (not on QVL)
    if profile in {"expo", "xmp", "expo, xmp"}:
        return CompatibilityResult(
            "unknown",
            f"RAM operates with an {profile.upper()} profile ({speed:g} MT/s) unlisted on the motherboard memory QVL; profile stability is unverified and depends on CPU memory controller and board trace routing.",
        )

    # 3. Evaluate explicitly documented JEDEC profile
    if profile == "jedec":
        if cpu_limit is not None and speed > cpu_limit:
            dimm_str = f" for {dimm_count}-DIMM configuration" if dimm_count else ""
            return CompatibilityResult(
                "unknown",
                f"RAM specifies a JEDEC profile at {speed:g} MT/s, which exceeds the CPU's documented official memory limit of {cpu_limit:g} MT/s{dimm_str}; stability is unverified.",
            )
        dimm_info = f" (within documented CPU limit of {cpu_limit:g} MT/s)" if cpu_limit else ""
        return CompatibilityResult(
            "compatible",
            f"RAM operates with a standard JEDEC profile at {speed:g} MT/s{dimm_info}.",
        )

    # 4. Profile is NOT documented (missing profile info)
    if cpu_limit is not None:
        dimm_str = f" for {dimm_count}-DIMM configuration" if dimm_count else ""
        if speed > cpu_limit:
            return CompatibilityResult(
                "unknown",
                f"RAM speed {speed:g} MT/s exceeds the CPU's documented limit of {cpu_limit:g} MT/s{dimm_str}; memory profile information (JEDEC vs EXPO/XMP) is unverified and unlisted on the motherboard memory QVL.",
            )
        return CompatibilityResult(
            "compatible",
            f"RAM speed {speed:g} MT/s is within the CPU's documented limit of {cpu_limit:g} MT/s{dimm_str}; memory profile is not classified as EXPO/XMP.",
        )

    jedec_baseline = 5600 if ram_type == "ddr5" else 3200 if ram_type == "ddr4" else 5600
    if speed <= jedec_baseline:
        return CompatibilityResult(
            "compatible",
            f"RAM speed {speed:g} MT/s is within standard JEDEC baseline specifications (up to {jedec_baseline} MT/s) and is not classified as EXPO/XMP.",
        )

    return CompatibilityResult(
        "unknown",
        f"RAM speed {speed:g} MT/s exceeds standard JEDEC baseline (up to {jedec_baseline} MT/s) and memory profile information (JEDEC vs EXPO/XMP) is unverified and unlisted on the motherboard memory QVL.",
    )
