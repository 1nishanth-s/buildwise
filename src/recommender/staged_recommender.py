"""
BuildWise-AI — Staged Bounded Deterministic Recommender Engine

Generates intelligent PC build and upgrade recommendations using:
- Real catalog components from data/components.csv
- Real Indian INR prices from data/prices.csv
- Empirical benchmarks from data/benchmarks.csv
- Supervised ML performance predictions from best_cpu_pipeline & best_gpu_pipeline
- Deterministic compatibility validation from src.compatibility
- React Flow workflow graph construction (nodes & edges)
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

from src.performance_service import get_performance_service
from src.recommender.catalog_data import CatalogService, choose_best_price, parse_specs
from src.recommender.evaluator import evaluate_component_compatibility, validate_full_build

logger = logging.getLogger("staged_recommender")

USAGE_PROFILES = {
    "gaming": {
        "label": "Gaming",
        "description": "High frame rates, fast GPU rendering, responsive gaming performance",
        "weights": {
            "gpu": 0.38,
            "cpu": 0.20,
            "motherboard": 0.12,
            "ram": 0.08,
            "storage": 0.07,
            "psu": 0.07,
            "case": 0.05,
            "cooler": 0.03,
        },
        "requires_gpu": True,
    },
    "programming": {
        "label": "Programming / Workstation",
        "description": "Fast compilation, multi-core CPU capacity, ample memory for containers and VMs",
        "weights": {
            "cpu": 0.32,
            "ram": 0.16,
            "motherboard": 0.13,
            "gpu": 0.18,
            "storage": 0.09,
            "psu": 0.06,
            "case": 0.04,
            "cooler": 0.02,
        },
        "requires_gpu": False,
    },
    "video editing": {
        "label": "Video Editing / Content Creation",
        "description": "4K/8K timeline playback, hardware encoding, multi-threaded CPU and high VRAM GPU",
        "weights": {
            "cpu": 0.28,
            "gpu": 0.28,
            "ram": 0.14,
            "motherboard": 0.11,
            "storage": 0.08,
            "psu": 0.06,
            "case": 0.05,
        },
        "requires_gpu": True,
    },
    "3d rendering": {
        "label": "3D Rendering / Animation",
        "description": "Blender, Maya, Cinema4D rendering with maximum GPU compute and CPU rendering capability",
        "weights": {
            "gpu": 0.35,
            "cpu": 0.25,
            "ram": 0.14,
            "motherboard": 0.11,
            "storage": 0.07,
            "psu": 0.05,
            "case": 0.03,
        },
        "requires_gpu": True,
    },
    "machine learning": {
        "label": "Machine Learning",
        "description": "CUDA tensor acceleration, high VRAM GPU capacity, and high-memory workstation layout",
        "weights": {
            "gpu": 0.40,
            "cpu": 0.20,
            "ram": 0.15,
            "motherboard": 0.11,
            "storage": 0.06,
            "psu": 0.05,
            "case": 0.03,
        },
        "requires_gpu": True,
    },
    "office work": {
        "label": "Office Work / Productivity",
        "description": "Snappy everyday multitasking, energy efficiency, quiet operation, budget conscious",
        "weights": {
            "cpu": 0.32,
            "motherboard": 0.20,
            "ram": 0.14,
            "storage": 0.14,
            "psu": 0.10,
            "case": 0.10,
        },
        "requires_gpu": False,
    },
    "general purpose": {
        "label": "General Purpose",
        "description": "Balanced everyday computing, multimedia, browsing, and light gaming",
        "weights": {
            "cpu": 0.28,
            "motherboard": 0.18,
            "ram": 0.14,
            "gpu": 0.18,
            "storage": 0.10,
            "psu": 0.06,
            "case": 0.06,
        },
        "requires_gpu": False,
    },
}


def _normalize_usage(usage_input: str) -> str:
    key = str(usage_input).strip().casefold()
    for k in USAGE_PROFILES:
        if k in key or key in k:
            return k
    if "game" in key:
        return "gaming"
    if "code" in key or "program" in key or "dev" in key or "workstation" in key:
        return "programming"
    if "video" in key or "edit" in key or "content" in key:
        return "video editing"
    if "3d" in key or "render" in key:
        return "3d rendering"
    if "ml" in key or "ai" in key or "learning" in key:
        return "machine learning"
    if "office" in key or "study" in key:
        return "office work"
    return "general purpose"


def _get_priced_catalog(catalog: CatalogService, category: str) -> List[Dict[str, Any]]:
    items = catalog.get_components_by_category(category)
    priced = []
    for it in items:
        cid = it["component_id"]
        best_p = choose_best_price(cid, catalog.prices_lookup, prefer_available=True)
        if best_p:
            specs = parse_specs(it.get("specs_json", {}))
            display_name = it.get("name") or f"{it.get('brand', '')} {it.get('model', '')}".strip()
            priced.append({
                **it,
                "name": display_name,
                "specs": specs,
                "price": best_p["price_inr"],
                "price_entry": best_p,
            })
    # Sort primarily by price
    priced.sort(key=lambda x: x["price"])
    return priced


def _enrich_component_metadata(
    comp: Dict[str, Any], catalog: CatalogService, perf_service: Any
) -> Dict[str, Any]:
    """Enriches a selected component with price details, empirical benchmarks, and ML estimates."""
    cid = comp.get("component_id", "")
    cat = comp.get("category", "").casefold()
    specs = parse_specs(comp.get("specs_json", comp.get("specs", {})))

    best_p = choose_best_price(cid, catalog.prices_lookup, prefer_available=True)
    price_val = best_p["price_inr"] if best_p else None

    # Empirical benchmark lookup
    emp_bm = catalog.benchmarks_lookup.get(cid)
    empirical_info = None
    if emp_bm:
        if cat == "cpu" and emp_bm.get("cinebench_r23_multi"):
            empirical_info = {
                "metric": "Cinebench R23 Multi-Core",
                "score": float(emp_bm["cinebench_r23_multi"]),
                "source": emp_bm.get("benchmark_source", "Recorded empirical observation"),
                "recorded_at": emp_bm.get("recorded_at"),
            }
        elif cat == "gpu" and emp_bm.get("timespy_graphics"):
            empirical_info = {
                "metric": "3DMark Time Spy Graphics",
                "score": float(emp_bm["timespy_graphics"]),
                "source": emp_bm.get("benchmark_source", "Recorded empirical observation"),
                "recorded_at": emp_bm.get("recorded_at"),
            }

    # Supervised ML Performance Prediction
    ml_info = None
    if cat == "cpu":
        pred_res = perf_service.predict_cpu(comp)
        if pred_res.get("status") == "available" and pred_res.get("score") is not None:
            ml_info = {
                "metric": "Predicted Cinebench R23 Multi-Core",
                "score": round(pred_res["score"], 1),
                "model": pred_res.get("model_name", "Ridge Regression (alpha=10.0)"),
                "status": "success",
            }
        else:
            ml_info = {
                "metric": "Cinebench R23 Multi-Core",
                "status": pred_res.get("status", "unavailable"),
                "reason": pred_res.get("message", "Prediction unavailable for this CPU"),
            }
    elif cat == "gpu":
        pred_res = perf_service.predict_gpu(comp)
        if pred_res.get("status") == "available" and pred_res.get("score") is not None:
            ml_info = {
                "metric": "Predicted 3DMark Time Spy Graphics",
                "score": round(pred_res["score"], 1),
                "model": pred_res.get("model_name", "Ridge Regression (alpha=1.0)"),
                "status": "success",
            }
        else:
            ml_info = {
                "metric": "3DMark Time Spy Graphics",
                "status": pred_res.get("status", "unavailable"),
                "reason": pred_res.get("message", "Prediction unavailable for this GPU"),
            }

    display_name = comp.get("name") or f"{comp.get('brand', '')} {comp.get('model', '')}".strip()
    return {
        "component_id": cid,
        "category": cat,
        "name": display_name,
        "brand": comp.get("brand", ""),
        "model": comp.get("model", ""),
        "specs": specs,
        "price": price_val,
        "seller": best_p.get("seller") if best_p else "Unknown",
        "sourceUrl": best_p.get("source_url") if best_p else None,
        "availability": best_p.get("availability") if best_p else "unknown",
        "priceBasis": best_p.get("price_basis") if best_p else "None",
        "empiricalBenchmark": empirical_info,
        "mlPrediction": ml_info,
    }


def _find_alternatives(
    category: str,
    selected_comp: Dict[str, Any],
    all_selected: Dict[str, Dict[str, Any]],
    catalog: CatalogService,
    limit: int = 4,
) -> List[Dict[str, Any]]:
    """Finds top compatible alternative components for the properties panel replacement drawer."""
    candidates = _get_priced_catalog(catalog, category)
    sel_id = selected_comp.get("component_id")
    compatible_alts = []

    # Temporary build dictionary for testing candidate compatibility
    test_build = dict(all_selected)

    for cand in candidates:
        if cand["component_id"] == sel_id:
            continue
        test_build[category] = cand
        compat = evaluate_component_compatibility(cand, test_build)
        if compat["status"] != "incompatible":
            best_p = choose_best_price(cand["component_id"], catalog.prices_lookup, prefer_available=True)
            compatible_alts.append({
                "id": cand["component_id"],
                "name": cand["name"],
                "brand": cand.get("brand", ""),
                "price": best_p["price_inr"] if best_p else cand["price"],
                "specs": cand["specs"],
            })
            if len(compatible_alts) >= limit:
                break

    return compatible_alts


def _find_compatible_dependency_candidate(
    cat: str,
    proposed_components: Dict[str, Dict[str, Any]],
    catalog: CatalogService,
) -> Optional[Dict[str, Any]]:
    """
    Finds the most cost-effective candidate component in the priced catalog
    that is strictly compatible with the current proposed configuration.
    Supports multi-hop chained dependencies (e.g., Motherboard relaxing retained RAM
    so that a new socket can be chosen and RAM updated subsequently).
    """
    candidates = _get_priced_catalog(catalog, cat)
    cpu_comp = proposed_components.get("cpu")
    cpu_rt = cpu_comp.get("specs", {}).get("ram_type") if cpu_comp else None

    # Pass 1: strictly compatible with all current components (including retained ones)
    for cand in candidates:
        if cat == "motherboard" and cpu_rt:
            cand_rt = cand.get("specs", {}).get("ram_type")
            if cand_rt and str(cand_rt).upper() != str(cpu_rt).upper():
                continue

        test_build = dict(proposed_components)
        test_build[cat] = cand
        # Verify candidate compatibility against test_build
        res = evaluate_component_compatibility(cand, test_build)
        if res.get("status") == "incompatible":
            continue

        # Also verify reverse checks from every other component against cand
        incompat_detected = False
        for oc, ocomp in test_build.items():
            if oc != cat and ocomp:
                r_check = evaluate_component_compatibility(ocomp, {cat: cand})
                if r_check.get("status") == "incompatible":
                    incompat_detected = True
                    break
        if not incompat_detected:
            return cand

    # Pass 2: if cat == 'motherboard' and retained RAM was the blocker, allow candidates
    # where the motherboard matches CPU, allowing RAM to be resolved in the next pass.
    if cat == "motherboard" and proposed_components.get("ram", {}).get("_reusable"):
        test_without_retained_ram = {k: v for k, v in proposed_components.items() if k != "ram"}
        for cand in candidates:
            if cpu_rt:
                cand_rt = cand.get("specs", {}).get("ram_type")
                if cand_rt and str(cand_rt).upper() != str(cpu_rt).upper():
                    continue

            test_build = dict(test_without_retained_ram)
            test_build[cat] = cand
            res = evaluate_component_compatibility(cand, test_build)
            if res.get("status") == "incompatible":
                continue
            incompat_detected = False
            for oc, ocomp in test_build.items():
                if oc != cat and ocomp:
                    r_check = evaluate_component_compatibility(ocomp, {cat: cand})
                    if r_check.get("status") == "incompatible":
                        incompat_detected = True
                        break
            if not incompat_detected:
                return cand

    return None


def generate_build_recommendation(
    usage_input: str,
    budget_inr: int,
    catalog: Optional[CatalogService] = None,
    perf_service: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Executes staged bounded recommendation for a new PC build.
    Returns:
        {
            "nodes": [...],
            "edges": [...],
            "summary": {...},
            "components": {...},
            "build_valid": bool,
            "notes": [...]
        }
    """
    if catalog is None:
        catalog = CatalogService.get_instance()
    if perf_service is None:
        perf_service = get_performance_service()

    usage_key = _normalize_usage(usage_input)
    profile = USAGE_PROFILES[usage_key]
    weights = profile["weights"]

    # Budget boundary validation
    if budget_inr < 18000:
        return {
            "error": True,
            "message": f"Requested budget ₹{budget_inr:,} is below the minimum viable threshold (₹18,000) for a modern, compatible desktop PC with verified catalog components.",
            "nodes": [],
            "edges": [],
            "summary": {"total": 0, "budget": budget_inr, "status": "insufficient_budget"},
        }

    # Fetch priced candidates per category
    priced_cpus = _get_priced_catalog(catalog, "cpu")
    priced_mobos = _get_priced_catalog(catalog, "motherboard")
    priced_rams = _get_priced_catalog(catalog, "ram")
    priced_gpus = _get_priced_catalog(catalog, "gpu")
    priced_storages = _get_priced_catalog(catalog, "storage")
    priced_psus = _get_priced_catalog(catalog, "psu")
    priced_cases = _get_priced_catalog(catalog, "case")
    priced_coolers = _get_priced_catalog(catalog, "cooler")

    selected: Dict[str, Dict[str, Any]] = {}
    notes: List[str] = []

    # -------------------------------------------------------------------------
    # Stage 1: CPU Selection
    # -------------------------------------------------------------------------
    target_cpu_budget = budget_inr * weights["cpu"]
    best_cpu = None
    scored_cpus = []
    for cpu in priced_cpus:
        if cpu["price"] <= target_cpu_budget * 1.35:
            # Score CPU by cores, boost clock, or ML prediction
            pred = perf_service.predict_cpu(cpu)
            score = pred.get("score") if (pred.get("status") == "available" and pred.get("score")) else 0.0
            if score == 0.0:
                score = float(cpu["specs"].get("cores", 4)) * 1000.0
            scored_cpus.append((score, -abs(cpu["price"] - target_cpu_budget), cpu))

    if scored_cpus:
        scored_cpus.sort(key=lambda x: (x[0], x[1]), reverse=True)
        best_cpu = scored_cpus[0][2]
    else:
        best_cpu = priced_cpus[0]

    selected["cpu"] = best_cpu
    notes.append(f"Selected {best_cpu['name']} based on {profile['label']} computing profile.")

    # -------------------------------------------------------------------------
    # Stage 2: Motherboard Selection (Must match CPU Socket & RAM generation)
    # -------------------------------------------------------------------------
    target_mobo_budget = budget_inr * weights["motherboard"]
    cpu_ram_type = str(best_cpu["specs"].get("ram_type", "")).strip().casefold()
    compatible_mobos = []
    for mb in priced_mobos:
        compat = evaluate_component_compatibility(mb, selected)
        if compat["status"] != "incompatible":
            mb_ram_type = str(mb["specs"].get("ram_type", "")).strip().casefold()
            # If CPU specifies a RAM type, require motherboard to support it
            if cpu_ram_type and mb_ram_type and cpu_ram_type != mb_ram_type:
                continue
            diff = abs(mb["price"] - target_mobo_budget)
            compatible_mobos.append((diff, mb))

    if compatible_mobos:
        compatible_mobos.sort(key=lambda x: x[0])
        best_mobo = compatible_mobos[0][1]
    else:
        # Fallback to first compatible
        best_mobo = next((mb for mb in priced_mobos if evaluate_component_compatibility(mb, selected)["status"] != "incompatible"), priced_mobos[0])

    selected["motherboard"] = best_mobo
    notes.append(f"Selected motherboard {best_mobo['name']} matching socket {best_cpu['specs'].get('socket', '')}.")

    # -------------------------------------------------------------------------
    # Stage 3: RAM Selection (Must match Motherboard & CPU RAM type)
    # -------------------------------------------------------------------------
    target_ram_budget = budget_inr * weights["ram"]
    mb_ram_type = str(best_mobo["specs"].get("ram_type", "")).strip().casefold()
    compatible_rams = []
    for ram in priced_rams:
        compat = evaluate_component_compatibility(ram, selected)
        if compat["status"] != "incompatible":
            r_type = str(ram["specs"].get("ram_type", "")).strip().casefold()
            if mb_ram_type and r_type and mb_ram_type != r_type:
                continue
            cap_gb = float(ram["specs"].get("capacity_gb", 16) or 16)
            # Prefer 32GB if budget >= 85,000, else 16GB
            pref_cap = 32 if budget_inr >= 85000 else 16
            cap_score = 1000 if cap_gb == pref_cap else 500
            diff = -abs(ram["price"] - target_ram_budget)
            compatible_rams.append((cap_score, diff, ram))

    if compatible_rams:
        compatible_rams.sort(key=lambda x: (x[0], x[1]), reverse=True)
        best_ram = compatible_rams[0][2]
    else:
        best_ram = next((r for r in priced_rams if evaluate_component_compatibility(r, selected)["status"] != "incompatible"), priced_rams[0])

    selected["ram"] = best_ram
    notes.append(f"Selected {best_ram['name']} ({best_ram['specs'].get('ram_type', 'DDR4')}) memory kit.")

    # -------------------------------------------------------------------------
    # Stage 4: GPU Selection (Dedicated vs Integrated)
    # -------------------------------------------------------------------------
    needs_gpu = profile["requires_gpu"] or (budget_inr >= 45000)
    best_gpu = None
    if needs_gpu and "gpu" in weights:
        target_gpu_budget = budget_inr * weights["gpu"]
        scored_gpus = []
        for gpu in priced_gpus:
            if gpu["price"] <= target_gpu_budget * 1.30:
                pred = perf_service.predict_gpu(gpu)
                score = pred.get("score") if (pred.get("status") == "available" and pred.get("score")) else 0.0
                if score == 0.0:
                    score = float(gpu["specs"].get("vram_gb", 4) or 4) * 1000.0
                scored_gpus.append((score, -abs(gpu["price"] - target_gpu_budget), gpu))

        if scored_gpus:
            scored_gpus.sort(key=lambda x: (x[0], x[1]), reverse=True)
            best_gpu = scored_gpus[0][2]
        else:
            best_gpu = priced_gpus[0]

        selected["gpu"] = best_gpu
        notes.append(f"Selected {best_gpu['name']} to meet graphical demands for {profile['label']}.")

    # -------------------------------------------------------------------------
    # Stage 5: Storage Selection (NVMe preferred)
    # -------------------------------------------------------------------------
    target_storage_budget = budget_inr * weights["storage"]
    compatible_storages = []
    for st in priced_storages:
        compat = evaluate_component_compatibility(st, selected)
        if compat["status"] == "compatible":
            cap_gb = float(st["specs"].get("capacity_gb", 500) or 500)
            diff = -abs(st["price"] - target_storage_budget)
            compatible_storages.append((cap_gb, diff, st))

    if compatible_storages:
        compatible_storages.sort(key=lambda x: (x[0], x[1]), reverse=True)
        best_storage = compatible_storages[0][2]
    else:
        best_storage = priced_storages[0]

    selected["storage"] = best_storage
    notes.append(f"Selected {best_storage['name']} high-speed storage.")

    # -------------------------------------------------------------------------
    # Stage 6: PSU Selection (Wattage headroom check)
    # -------------------------------------------------------------------------
    target_psu_budget = budget_inr * weights["psu"]
    compatible_psus = []
    for psu in priced_psus:
        compat = evaluate_component_compatibility(psu, selected)
        if compat["status"] == "compatible":
            wattage = float(psu["specs"].get("wattage", 500) or 500)
            diff = -abs(psu["price"] - target_psu_budget)
            compatible_psus.append((wattage, diff, psu))

    if compatible_psus:
        compatible_psus.sort(key=lambda x: (x[0], x[1]), reverse=True)
        best_psu = compatible_psus[0][2]
    else:
        best_psu = priced_psus[0]

    selected["psu"] = best_psu
    notes.append(f"Selected {best_psu['name']} providing clean power headroom.")

    # -------------------------------------------------------------------------
    # Stage 7: Case Selection (Clearance for motherboard & GPU)
    # -------------------------------------------------------------------------
    target_case_budget = budget_inr * weights["case"]
    compatible_cases = []
    for cs in priced_cases:
        compat = evaluate_component_compatibility(cs, selected)
        if compat["status"] == "compatible":
            diff = abs(cs["price"] - target_case_budget)
            compatible_cases.append((diff, cs))

    if compatible_cases:
        compatible_cases.sort(key=lambda x: x[0])
        best_case = compatible_cases[0][1]
    else:
        best_case = priced_cases[0]

    selected["case"] = best_case
    notes.append(f"Selected chassis {best_case['name']} accommodating motherboard form factor.")

    # -------------------------------------------------------------------------
    # Stage 8: Cooler Selection (Optional / TDP > 65W or budget headroom)
    # -------------------------------------------------------------------------
    cpu_tdp = float(best_cpu["specs"].get("tdp_w", 65) or 65)
    if cpu_tdp > 65 or budget_inr >= 60000:
        compatible_coolers = []
        for clr in priced_coolers:
            compat = evaluate_component_compatibility(clr, selected)
            if compat["status"] == "compatible":
                compatible_coolers.append(clr)
        if compatible_coolers:
            selected["cooler"] = compatible_coolers[0]
            notes.append(f"Selected aftermarket CPU cooler {compatible_coolers[0]['name']}.")

    # -------------------------------------------------------------------------
    # Final Validation & Workflow Assembly
    # -------------------------------------------------------------------------
    enriched_components: Dict[str, Dict[str, Any]] = {}
    total_cost = 0

    for cat, item in selected.items():
        enriched = _enrich_component_metadata(item, catalog, perf_service)
        # Fetch alternatives
        enriched["alternatives"] = _find_alternatives(cat, item, selected, catalog, limit=4)
        enriched_components[cat] = enriched
        if enriched["price"]:
            total_cost += enriched["price"]

    validation_result = validate_full_build(selected)

    # Construct React Flow Graph
    nodes, edges = _build_build_workflow_graph(
        usage=profile["label"],
        budget=budget_inr,
        total_cost=total_cost,
        components=enriched_components,
        validation_result=validation_result,
        notes=notes,
    )

    remaining_budget = budget_inr - total_cost
    summary = {
        "total": total_cost,
        "budget": budget_inr,
        "remaining": remaining_budget,
        "status": "compatible" if validation_result["status"] == "compatible" and remaining_budget >= -5000 else "warning",
        "validationStatus": validation_result["status"],
        "checksCount": len(validation_result["checks"]),
        "notes": notes,
    }

    return {
        "nodes": nodes,
        "edges": edges,
        "summary": summary,
        "components": enriched_components,
        "validation": validation_result,
        "notes": notes,
    }


def _build_build_workflow_graph(
    usage: str,
    budget: int,
    total_cost: int,
    components: Dict[str, Dict[str, Any]],
    validation_result: Dict[str, Any],
    notes: List[str],
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Generates horizontal Left-to-Right (LR) workflow graph for Build Mode.
    Visual Hierarchy:
      Level 1 (Left): Build Request
      Level 2 (Next): CPU (primary component)
      Level 3 (Middle): Motherboard, RAM, GPU
      Level 4 (Next): Storage, PSU, Cooler, Case
      Level 5 (Far Right): Final PC Build
    Edges reflect real PC hardware relationships without standalone analysis nodes.
    """
    nodes: List[Dict[str, Any]] = []
    edges: List[Dict[str, Any]] = []

    def add_node(nid: str, data: Dict[str, Any], pos_x: int, pos_y: int):
        nodes.append({
            "id": nid,
            "type": "workflowNode",
            "position": {"x": pos_x, "y": pos_y},
            "data": data,
        })

    def add_edge(
        src: str,
        tgt: str,
        label: str = "",
        color: str = "#94a3b8",
        animated: bool = False,
        dashed: bool = False,
        source_handle: Optional[str] = None,
        target_handle: Optional[str] = None,
        edge_type: str = "default",
    ):
        style = {
            "stroke": color,
            "strokeWidth": 2.5,
        }
        if dashed:
            style["strokeDasharray"] = "5 5"
        edge_data = {
            "id": f"e-{src}-{tgt}",
            "source": src,
            "target": tgt,
            "type": edge_type,
            "animated": animated,
            "style": style,
            "markerEnd": {"type": "arrowclosed", "color": color, "width": 12, "height": 12},
        }
        if source_handle:
            edge_data["sourceHandle"] = source_handle
        if target_handle:
            edge_data["targetHandle"] = target_handle
        if label:
            edge_data["label"] = label
            edge_data["labelStyle"] = {
                "fill": "#e2e8f0",
                "fontSize": 9.5,
                "fontWeight": 500,
                "fontFamily": "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace",
                "letterSpacing": "0.02em",
            }
            edge_data["labelBgStyle"] = {
                "fill": "#0f172a",
                "fillOpacity": 0.95,
                "stroke": "#334155",
                "strokeWidth": 1,
                "rx": 4,
                "ry": 4,
            }
            edge_data["labelBgPadding"] = [5, 2.5]
            edge_data["labelBgBorderRadius"] = 4
        edges.append(edge_data)

    y_mid = 340
    compat_status = "compatible" if validation_result.get("status") == "compatible" else "warning"

    # Level 1 (Left): Build Request
    add_node(
        "n-req",
        {
            "kind": "requirements",
            "label": "Build Request",
            "subtitle": usage,
            "description": f"Target Budget: ₹{budget:,} · Primary Usage: {usage}",
            "status": "selected",
            "budget": budget,
            "usage": usage,
        },
        50,
        y_mid,
    )

    # Level 2 (Next): CPU as the primary component
    cpu_comp = components.get("cpu")
    if cpu_comp:
        add_node(
            "n-cpu",
            {
                "kind": "component",
                "category": "cpu",
                "label": cpu_comp["name"],
                "subtitle": cpu_comp["brand"],
                "status": "recommended",
                "compatStatus": "compatible",
                "price": cpu_comp["price"],
                "specs": cpu_comp["specs"],
                "componentId": cpu_comp["component_id"],
                "seller": cpu_comp.get("seller"),
                "sourceUrl": cpu_comp.get("sourceUrl"),
                "availability": cpu_comp.get("availability"),
                "priceBasis": cpu_comp.get("priceBasis"),
                "empiricalBenchmark": cpu_comp.get("empiricalBenchmark"),
                "mlPrediction": cpu_comp.get("mlPrediction"),
                "alternatives": cpu_comp.get("alternatives", []),
                "reason": cpu_comp.get("reason", f"Primary processor selected for {usage} build."),
            },
            450,
            y_mid,
        )
        # Restrained connection from Build Request to CPU
        add_edge("n-req", "n-cpu", label="Build Target", color="#94a3b8", dashed=True, animated=False)

    # Level 3 (Middle): Motherboard, RAM, GPU
    x_col3 = 850
    col3_cats = {
        "motherboard": 140,
        "ram": 340,
        "gpu": 540,
    }
    for cat, y_pos in col3_cats.items():
        comp = components.get(cat)
        if not comp:
            continue
        add_node(
            f"n-{cat}",
            {
                "kind": "component",
                "category": cat,
                "label": comp["name"],
                "subtitle": comp["brand"],
                "status": "recommended",
                "compatStatus": "compatible",
                "price": comp["price"],
                "specs": comp["specs"],
                "componentId": comp["component_id"],
                "seller": comp.get("seller"),
                "sourceUrl": comp.get("sourceUrl"),
                "availability": comp.get("availability"),
                "priceBasis": comp.get("priceBasis"),
                "empiricalBenchmark": comp.get("empiricalBenchmark"),
                "mlPrediction": comp.get("mlPrediction"),
                "alternatives": comp.get("alternatives", []),
                "reason": comp.get("reason", f"Selected {cat.upper()} for {usage} profile."),
            },
            x_col3,
            y_pos,
        )

    # Level 4 (Next): Storage, PSU, Cooler, Case
    x_col4 = 1250
    col4_cats = {
        "cooler": 40,
        "storage": 240,
        "psu": 440,
        "case": 640,
    }
    for cat, y_pos in col4_cats.items():
        comp = components.get(cat)
        if not comp:
            continue
        add_node(
            f"n-{cat}",
            {
                "kind": "component",
                "category": cat,
                "label": comp["name"],
                "subtitle": comp["brand"],
                "status": "recommended",
                "compatStatus": "compatible",
                "price": comp["price"],
                "specs": comp["specs"],
                "componentId": comp["component_id"],
                "seller": comp.get("seller"),
                "sourceUrl": comp.get("sourceUrl"),
                "availability": comp.get("availability"),
                "priceBasis": comp.get("priceBasis"),
                "empiricalBenchmark": comp.get("empiricalBenchmark"),
                "mlPrediction": comp.get("mlPrediction"),
                "alternatives": comp.get("alternatives", []),
                "reason": comp.get("reason", f"Selected {cat.upper()} for {usage} profile."),
            },
            x_col4,
            y_pos,
        )

    # Level 5 (Far Right): Final PC Build
    add_node(
        "n-final",
        {
            "kind": "final",
            "label": "Final PC Build",
            "subtitle": f"₹{total_cost:,} Total",
            "description": f"Verified compatible build. Remaining budget: ₹{budget - total_cost:,}.",
            "status": compat_status,
            "price": total_cost,
        },
        1650,
        y_mid,
    )

    # Meaningful Hardware Relationship Edges (Clean Non-Crossing Professional Layout):
    # 1. CPU <-> Motherboard: socket compatibility
    if "cpu" in components and "motherboard" in components:
        add_edge("n-cpu", "n-motherboard", label="Socket Match", color="#94a3b8")

    # 2. Motherboard <-> Cooler: mounting and thermal interface
    if "motherboard" in components and "cooler" in components:
        add_edge("n-motherboard", "n-cooler", label="Mounting & Thermal", color="#94a3b8")

    # 3. Motherboard <-> RAM: memory compatibility (Clean vertical bus drop)
    if "motherboard" in components and "ram" in components:
        add_edge(
            "n-motherboard",
            "n-ram",
            label="Memory Bus",
            color="#94a3b8",
            source_handle="source-bottom",
            target_handle="target-top",
        )

    # 4. Motherboard <-> GPU: expansion interface
    if "motherboard" in components and "gpu" in components:
        add_edge("n-motherboard", "n-gpu", label="PCIe Interface", color="#94a3b8")

    # 5. Motherboard <-> Storage: storage interface
    if "motherboard" in components and "storage" in components:
        add_edge("n-motherboard", "n-storage", label="M.2 NVMe / SATA", color="#94a3b8")

    # 6. GPU <-> PSU: dedicated power delivery
    if "gpu" in components and "psu" in components:
        add_edge("n-gpu", "n-psu", label="Power Delivery", color="#94a3b8")

    # 7. GPU <-> Case: GPU physical length clearance
    if "gpu" in components and "case" in components:
        add_edge("n-gpu", "n-case", label="GPU Clearance", color="#94a3b8")

    # 8-11. Clean Symmetrical Convergence into Final Build Summary (Column 4 -> Column 5)
    if "cooler" in components:
        add_edge("n-cooler", "n-final", label="Height Clearance", color="#94a3b8")
    if "storage" in components:
        add_edge("n-storage", "n-final", label="Storage Array", color="#94a3b8")
    if "psu" in components:
        add_edge("n-psu", "n-final", label="Power Delivery", color="#94a3b8")
    if "case" in components:
        add_edge("n-case", "n-final", label="Form Factor Fit", color="#94a3b8")

    return nodes, edges


def generate_upgrade_recommendation(
    existing_hardware: Dict[str, Any],
    budget_inr: int,
    goal: str,
    catalog: Optional[CatalogService] = None,
    perf_service: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Executes intelligent upgrade recommendation comparing existing hardware vs upgrade candidates.
    Distinguishes retained components from proposed replacements with empirical and ML deltas.
    """
    if catalog is None:
        catalog = CatalogService.get_instance()
    if perf_service is None:
        perf_service = get_performance_service()

    # Find matching catalog records for existing hardware if possible
    ALL_UPGRADE_CATEGORIES = ["cpu", "gpu", "motherboard", "ram", "storage", "psu", "cooler", "case"]
    existing_resolved: Dict[str, Dict[str, Any]] = {}
    for cat in ALL_UPGRADE_CATEGORIES:
        val = str(existing_hardware.get(cat, "")).strip()
        if not val:
            continue
        # Search catalog for substring match in brand or model
        subset = catalog.df_components[catalog.df_components["category"].str.casefold() == cat]
        matched_row = None

        preferred_ram = "DDR4" if "ddr4" in val.lower() else ("DDR5" if "ddr5" in val.lower() else None)
        preferred_socket = None
        for s in ["AM5", "AM4", "LGA1700", "LGA1200", "LGA1151"]:
            if s.lower() in val.lower():
                preferred_socket = s
                break

        # Pass 1: exact match with qualifiers
        for _, row in subset.iterrows():
            m_str = (str(row.get("brand", "")) + " " + str(row.get("model", ""))).lower()
            sp = parse_specs(row.get("specs_json", {}))
            if preferred_ram and sp.get("ram_type", "").upper() != preferred_ram:
                continue
            if preferred_socket and sp.get("socket", "").upper() != preferred_socket:
                continue
            if val.lower() in m_str or all(w in m_str for w in val.lower().split()):
                matched_row = row.to_dict()
                break

        # Pass 2: relaxed match
        if not matched_row:
            matches = subset[
                subset["brand"].str.contains(val, case=False, na=False) |
                subset["model"].str.contains(val, case=False, na=False)
            ]
            if not matches.empty:
                # If preferred qualifier exists, try to find matching row among matches
                if preferred_ram or preferred_socket:
                    for _, r in matches.iterrows():
                        sp = parse_specs(r.get("specs_json", {}))
                        if preferred_ram and sp.get("ram_type", "").upper() == preferred_ram:
                            matched_row = r.to_dict()
                            break
                        if preferred_socket and sp.get("socket", "").upper() == preferred_socket:
                            matched_row = r.to_dict()
                            break
                if not matched_row:
                    matched_row = matches.iloc[0].to_dict()

        if matched_row:
            existing_resolved[cat] = _enrich_component_metadata(matched_row, catalog, perf_service)
        else:
            custom_specs: Dict[str, Any] = {}
            import re
            if cat == "psu":
                m = re.search(r'(\d{3,4})\s*[wW]', val)
                if m:
                    custom_specs["wattage_w"] = int(m.group(1))
            elif cat == "ram":
                if preferred_ram:
                    custom_specs["ram_type"] = preferred_ram
            elif cat in ("cpu", "motherboard"):
                if preferred_socket:
                    custom_specs["socket"] = preferred_socket
            existing_resolved[cat] = {
                "component_id": f"custom_{cat}",
                "category": cat,
                "name": val,
                "brand": "User Hardware",
                "model": val,
                "specs": custom_specs,
                "price": 0,
                "availability": "installed",
                "empiricalBenchmark": None,
                "mlPrediction": None,
            }

    # Determine primary upgrade target based on goal
    goal_lower = str(goal).casefold()
    upgrade_targets = ["gpu"]
    if "gam" in goal_lower or "fps" in goal_lower or "gpu" in goal_lower or "graphic" in goal_lower:
        upgrade_targets = ["gpu"]
    elif "render" in goal_lower or "video" in goal_lower:
        upgrade_targets = ["gpu", "ram"]
    elif "product" in goal_lower or "program" in goal_lower or "dev" in goal_lower or "multitask" in goal_lower or "cpu" in goal_lower or "processor" in goal_lower:
        upgrade_targets = ["cpu"]
    elif "storage" in goal_lower or "ssd" in goal_lower:
        upgrade_targets = ["storage"]
    elif "ram" in goal_lower or "memory" in goal_lower:
        upgrade_targets = ["ram"]
    else:
        upgrade_targets = ["gpu"]

    proposed_components: Dict[str, Dict[str, Any]] = {}
    total_upgrade_cost = 0
    deltas: Dict[str, Any] = {}

    # Retain components not being upgraded
    for cat in ALL_UPGRADE_CATEGORIES:
        if cat not in upgrade_targets and cat in existing_resolved:
            ret = dict(existing_resolved[cat])
            ret["_reusable"] = True
            ret["price"] = 0
            ret["upgrade_role"] = "retained"
            ret["dependency_reason"] = None
            proposed_components[cat] = ret

    # Select upgrade replacements within budget
    for target_cat in upgrade_targets:
        target_budget = budget_inr / len(upgrade_targets)
        candidates = _get_priced_catalog(catalog, target_cat)
        best_cand = None

        if target_cat == "gpu":
            scored = []
            for c in candidates:
                if c["price"] <= target_budget * 1.25:
                    pred = perf_service.predict_gpu(c)
                    sc = pred.get("score") if (pred.get("status") == "available" and pred.get("score")) else 0.0
                    scored.append((sc, c))
            if scored:
                scored.sort(key=lambda x: x[0], reverse=True)
                best_cand = scored[0][1]
            elif candidates:
                best_cand = candidates[0]

            if best_cand:
                enr = _enrich_component_metadata(best_cand, catalog, perf_service)
                enr["_reusable"] = False
                enr["upgrade_role"] = "primary"
                enr["dependency_reason"] = None
                enr["alternatives"] = _find_alternatives(target_cat, best_cand, proposed_components, catalog, limit=4)
                proposed_components[target_cat] = enr
                total_upgrade_cost += enr["price"] or 0

                # Compute performance comparison delta
                ex_gpu = existing_resolved.get("gpu")
                if ex_gpu and ex_gpu.get("mlPrediction") and ex_gpu["mlPrediction"].get("status") == "success" and enr.get("mlPrediction") and enr["mlPrediction"].get("status") == "success":
                    ex_score = ex_gpu["mlPrediction"]["score"]
                    up_score = enr["mlPrediction"]["score"]
                    diff = up_score - ex_score
                    pct = (diff / ex_score * 100.0) if ex_score > 0 else 0.0
                    deltas["gpu"] = {
                        "metric": "3DMark Time Spy Graphics",
                        "baselineScore": ex_score,
                        "upgradeScore": up_score,
                        "absoluteDelta": round(diff, 1),
                        "percentageDelta": round(pct, 1),
                    }

        elif target_cat == "cpu":
            mb = proposed_components.get("motherboard") or existing_resolved.get("motherboard")
            scored_same_socket = []
            scored_all = []

            prefer_intel = "intel" in goal_lower
            prefer_amd = "amd" in goal_lower or "ryzen" in goal_lower

            for c in candidates:
                if c["price"] <= target_budget * 1.25:
                    brand_c = str(c.get("brand", "")).casefold()
                    if prefer_intel and "intel" not in brand_c:
                        continue
                    if prefer_amd and "amd" not in brand_c:
                        continue

                    pred = perf_service.predict_cpu(c)
                    sc = pred.get("score") if (pred.get("status") == "available" and pred.get("score")) else 0.0
                    scored_all.append((sc, c))

                    if mb:
                        compat = evaluate_component_compatibility(c, {"motherboard": mb})
                        if compat["status"] != "incompatible":
                            scored_same_socket.append((sc, c))

            scored_all.sort(key=lambda x: x[0], reverse=True)
            scored_same_socket.sort(key=lambda x: x[0], reverse=True)

            mb_socket = str(mb.get("specs", {}).get("socket", "")).upper() if mb else ""
            force_platform_upgrade = (
                (prefer_intel and "AM" in mb_socket) or
                (prefer_amd and "LGA" in mb_socket) or
                ("am5" in goal_lower and "AM5" not in mb_socket) or
                ("lga1700" in goal_lower and "LGA1700" not in mb_socket)
            )

            if scored_same_socket and not force_platform_upgrade:
                best_cand = scored_same_socket[0][1]
            elif scored_all:
                best_cand = scored_all[0][1]
            elif candidates:
                best_cand = candidates[0]

            if best_cand:
                enr = _enrich_component_metadata(best_cand, catalog, perf_service)
                enr["_reusable"] = False
                enr["upgrade_role"] = "primary"
                enr["dependency_reason"] = None
                enr["alternatives"] = _find_alternatives(target_cat, best_cand, proposed_components, catalog, limit=4)
                proposed_components[target_cat] = enr
                total_upgrade_cost += enr["price"] or 0

                # Compute performance comparison delta
                ex_cpu = existing_resolved.get("cpu")
                if ex_cpu and ex_cpu.get("mlPrediction") and ex_cpu["mlPrediction"].get("status") == "success" and enr.get("mlPrediction") and enr["mlPrediction"].get("status") == "success":
                    ex_score = ex_cpu["mlPrediction"]["score"]
                    up_score = enr["mlPrediction"]["score"]
                    diff = up_score - ex_score
                    pct = (diff / ex_score * 100.0) if ex_score > 0 else 0.0
                    deltas["cpu"] = {
                        "metric": "Cinebench R23 Multi-Core",
                        "baselineScore": ex_score,
                        "upgradeScore": up_score,
                        "absoluteDelta": round(diff, 1),
                        "percentageDelta": round(pct, 1),
                    }

        elif target_cat == "ram":
            mb = proposed_components.get("motherboard") or existing_resolved.get("motherboard")
            candidates_ram = []
            for c in candidates:
                if c["price"] <= target_budget * 1.25:
                    if mb:
                        compat = evaluate_component_compatibility(c, {"motherboard": mb})
                        if compat["status"] != "incompatible":
                            candidates_ram.append(c)
                    else:
                        candidates_ram.append(c)
            best_cand = candidates_ram[-1] if candidates_ram else (candidates[0] if candidates else None)
            if best_cand:
                enr = _enrich_component_metadata(best_cand, catalog, perf_service)
                enr["_reusable"] = False
                enr["upgrade_role"] = "primary"
                enr["dependency_reason"] = None
                enr["alternatives"] = _find_alternatives(target_cat, best_cand, proposed_components, catalog, limit=4)
                proposed_components[target_cat] = enr
                total_upgrade_cost += enr["price"] or 0

        elif target_cat == "storage":
            candidates_st = [c for c in candidates if c["price"] <= target_budget * 1.2] or candidates
            best_cand = candidates_st[-1] if candidates_st else None
            if best_cand:
                enr = _enrich_component_metadata(best_cand, catalog, perf_service)
                enr["_reusable"] = False
                enr["upgrade_role"] = "primary"
                enr["dependency_reason"] = None
                enr["alternatives"] = _find_alternatives(target_cat, best_cand, proposed_components, catalog, limit=4)
                proposed_components[target_cat] = enr
                total_upgrade_cost += enr["price"] or 0

    # Bounded Dependency Resolution Loop (Passes 1..3 with cycle detection)
    max_passes = 3
    resolved_dependencies: set = set()
    unresolved_categories: list = []
    notes: list = []

    for pass_num in range(1, max_passes + 1):
        changed_in_pass = False
        retained_cats = [
            cat for cat, comp in proposed_components.items()
            if comp.get("_reusable") is True and cat not in resolved_dependencies
        ]

        for cat in retained_cats:
            comp = proposed_components[cat]
            res_forward = evaluate_component_compatibility(comp, proposed_components)
            incompat_reasons = []
            for chk in res_forward.get("checks", []):
                if chk.get("status") == "incompatible":
                    pair_name = chk.get("pair", "")
                    if cat != "psu" and pair_name.startswith("PSU"):
                        continue
                    incompat_reasons.append(chk.get("reason", "Incompatible pairing"))

            for other_cat, other_comp in proposed_components.items():
                if other_cat != cat and not other_comp.get("_reusable", False):
                    res_back = evaluate_component_compatibility(other_comp, {cat: comp})
                    for chk in res_back.get("checks", []):
                        if chk.get("status") == "incompatible":
                            pair_name = chk.get("pair", "")
                            if cat != "psu" and pair_name.startswith("PSU"):
                                continue
                            if chk.get("reason") not in incompat_reasons:
                                incompat_reasons.append(chk.get("reason", "Incompatible pairing"))

            if incompat_reasons:
                reason_text = "; ".join(incompat_reasons)
                dep_cand = _find_compatible_dependency_candidate(cat, proposed_components, catalog)
                if dep_cand:
                    enr_cand = _enrich_component_metadata(dep_cand, catalog, perf_service)
                    enr_cand["_reusable"] = False
                    enr_cand["upgrade_role"] = "dependency"
                    enr_cand["dependency_reason"] = f"Required replacement: {reason_text}"
                    enr_cand["alternatives"] = _find_alternatives(cat, dep_cand, proposed_components, catalog, limit=4)
                    proposed_components[cat] = enr_cand
                    total_upgrade_cost += enr_cand["price"] or 0
                    resolved_dependencies.add(cat)
                    changed_in_pass = True
                    logger.info("Resolved dependency for %s: %s (Reason: %s)", cat, enr_cand["name"], reason_text)
                else:
                    comp["upgrade_role"] = "unresolved"
                    comp["dependency_reason"] = f"Unresolved incompatibility: {reason_text}"
                    if cat not in unresolved_categories:
                        unresolved_categories.append(cat)
                    logger.warning("No compatible candidate found in catalog for dependent %s: %s", cat, reason_text)

        if not changed_in_pass:
            break

    primary_categories = [cat for cat, c in proposed_components.items() if c.get("upgrade_role") == "primary"]
    dependent_categories = [cat for cat, c in proposed_components.items() if c.get("upgrade_role") == "dependency"]
    retained_categories = [cat for cat, c in proposed_components.items() if c.get("upgrade_role") == "retained"]

    if dependent_categories:
        notes.append(
            f"Added required dependent replacement(s) for {', '.join(c.upper() for c in dependent_categories)} "
            "to satisfy hardware compatibility and system power requirements."
        )

    remaining_budget = budget_inr - total_upgrade_cost
    if remaining_budget < 0:
        notes.append(
            f"Plan exceeds budget by ₹{abs(remaining_budget):,}. All required dependencies were retained "
            "for hardware safety and operational stability."
        )

    if unresolved_categories:
        notes.append(
            f"Hardware incompatibility could not be resolved for {', '.join(c.upper() for c in unresolved_categories)} "
            "due to lack of matching parts in catalog."
        )

    validation = validate_full_build(proposed_components)

    overall_status = "compatible"
    if validation["status"] == "incompatible" or unresolved_categories:
        overall_status = "incompatible"
    elif remaining_budget < 0 or validation["status"] == "warning" or any(c.get("upgrade_role") == "warning" for c in proposed_components.values()):
        overall_status = "warning"

    nodes, edges = _build_upgrade_workflow_graph(
        existing=existing_resolved,
        proposed=proposed_components,
        budget=budget_inr,
        upgrade_cost=total_upgrade_cost,
        goal=goal,
        deltas=deltas,
        validation=validation,
    )

    summary = {
        "total": total_upgrade_cost,
        "budget": budget_inr,
        "remaining": remaining_budget,
        "goal": goal,
        "status": overall_status,
        "upgradedCategories": primary_categories + dependent_categories,
        "primaryCategories": primary_categories,
        "dependentCategories": dependent_categories,
        "retainedCategories": retained_categories,
        "unresolvedCategories": unresolved_categories,
        "upgradeRoles": {cat: c.get("upgrade_role") for cat, c in proposed_components.items()},
        "deltas": deltas,
        "notes": notes,
    }

    return {
        "nodes": nodes,
        "edges": edges,
        "summary": summary,
        "existing": existing_resolved,
        "proposed": proposed_components,
        "deltas": deltas,
        "validation": validation,
    }


def _build_upgrade_workflow_graph(
    existing: Dict[str, Dict[str, Any]],
    proposed: Dict[str, Dict[str, Any]],
    budget: int,
    upgrade_cost: int,
    goal: str,
    deltas: Dict[str, Any],
    validation: Dict[str, Any],
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Generates horizontal Left-to-Right (LR) workflow graph for Upgrade Mode.
    Visual Hierarchy:
      Level 1 (Left): Existing PC Configuration
      Level 2 (Next): CPU (if present)
      Level 3 (Middle): Motherboard, RAM, GPU
      Level 4 (Next): Storage, PSU, Cooler, Case
      Level 5 (Far Right): Final Upgrade Plan
    Distinguishes retained components (reusable) from proposed replacements (recommended).
    Internal analysis operations are removed as large standalone nodes.
    """
    nodes: List[Dict[str, Any]] = []
    edges: List[Dict[str, Any]] = []

    def add_node(nid: str, data: Dict[str, Any], pos_x: int, pos_y: int):
        nodes.append({
            "id": nid,
            "type": "workflowNode",
            "position": {"x": pos_x, "y": pos_y},
            "data": data,
        })

    def add_edge(
        src: str,
        tgt: str,
        label: str = "",
        color: str = "#94a3b8",
        animated: bool = False,
        dashed: bool = False,
        source_handle: Optional[str] = None,
        target_handle: Optional[str] = None,
        edge_type: str = "default",
    ):
        style = {
            "stroke": color,
            "strokeWidth": 2.5,
        }
        if dashed:
            style["strokeDasharray"] = "5 5"
        edge_data = {
            "id": f"e-{src}-{tgt}",
            "source": src,
            "target": tgt,
            "type": edge_type,
            "animated": animated,
            "style": style,
            "markerEnd": {"type": "arrowclosed", "color": color, "width": 12, "height": 12},
        }
        if source_handle:
            edge_data["sourceHandle"] = source_handle
        if target_handle:
            edge_data["targetHandle"] = target_handle
        if label:
            edge_data["label"] = label
            edge_data["labelStyle"] = {
                "fill": "#e2e8f0",
                "fontSize": 9.5,
                "fontWeight": 500,
                "fontFamily": "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace",
                "letterSpacing": "0.02em",
            }
            edge_data["labelBgStyle"] = {
                "fill": "#0f172a",
                "fillOpacity": 0.95,
                "stroke": "#334155",
                "strokeWidth": 1,
                "rx": 4,
                "ry": 4,
            }
            edge_data["labelBgPadding"] = [5, 2.5]
            edge_data["labelBgBorderRadius"] = 4
        edges.append(edge_data)

    y_mid = 340
    compat_status = "compatible" if validation.get("status") == "compatible" else "warning"

    # Level 1 (Left): Existing PC Configuration
    add_node(
        "n-existing",
        {
            "kind": "existing",
            "label": "Existing PC Configuration",
            "subtitle": f"{len(existing)} components entered",
            "description": f"Baseline system configuration. Upgrade Goal: {goal}.",
            "status": "existing",
            "specs": {cat: comp.get("name", "Installed") for cat, comp in existing.items()},
        },
        50,
        y_mid,
    )

    # Component layout positions in horizontal hierarchy
    # Level 2 (Next): CPU
    # Level 3 (Middle): Motherboard, RAM, GPU
    # Level 4 (Next): Cooler, Storage, PSU, Case
    cat_positions = {
        "cpu": (450, y_mid),
        "motherboard": (850, 140),
        "ram": (850, 340),
        "gpu": (850, 540),
        "cooler": (1250, 40),
        "storage": (1250, 240),
        "psu": (1250, 440),
        "case": (1250, 640),
    }

    prop_ids = []
    for cat, pos in cat_positions.items():
        comp = proposed.get(cat)
        if not comp:
            continue
        nid = f"n-{cat}"
        prop_ids.append(nid)
        is_reusable = comp.get("_reusable", False)
        role = comp.get("upgrade_role", "retained" if is_reusable else "primary")
        dep_reason = comp.get("dependency_reason")

        if role == "dependency":
            status_val = "dependency"
            subtitle_val = "Required Dependency"
        elif role == "primary":
            status_val = "recommended"
            subtitle_val = "Primary Upgrade"
        elif role == "unresolved":
            status_val = "warning"
            subtitle_val = "Unresolved Incompatibility"
        else:
            status_val = "reusable"
            subtitle_val = "Retained Component"

        price_val = 0 if is_reusable else (comp.get("price") or 0)
        ex_item = existing.get(cat, {})
        baseline_name = ex_item.get("name") if isinstance(ex_item, dict) else None

        if role == "dependency":
            reason_text = dep_reason or f"Required replacement for {goal} compatibility."
        elif role == "primary":
            reason_text = f"Selected primary upgrade replacement for {goal}."
        elif role == "unresolved":
            reason_text = dep_reason or "Hardware incompatibility could not be resolved."
        else:
            reason_text = "Retained from current configuration."

        add_node(
            nid,
            {
                "kind": "component",
                "category": cat,
                "label": comp.get("name", cat.upper()),
                "subtitle": subtitle_val,
                "status": status_val,
                "compatStatus": "compatible" if role != "unresolved" else "incompatible",
                "upgrade_role": role,
                "dependency_reason": dep_reason,
                "baseline_name": baseline_name,
                "price": price_val,
                "specs": comp.get("specs", {}),
                "componentId": comp.get("component_id"),
                "seller": comp.get("seller"),
                "sourceUrl": comp.get("sourceUrl"),
                "availability": comp.get("availability"),
                "priceBasis": comp.get("priceBasis"),
                "empiricalBenchmark": comp.get("empiricalBenchmark"),
                "mlPrediction": comp.get("mlPrediction"),
                "alternatives": comp.get("alternatives", []),
                "reason": reason_text,
            },
            pos[0],
            pos[1],
        )

    # Level 5 (Far Right): Final Upgrade Plan
    remaining = budget - upgrade_cost
    final_subtitle = f"₹{upgrade_cost:,} Total Cost"
    if remaining < 0:
        final_desc = f"Target: {goal}. Exceeds budget by ₹{abs(remaining):,}. Dependencies retained for safety."
        compat_status = "warning"
    else:
        final_desc = f"Target: {goal}. Remaining budget: ₹{remaining:,}."

    add_node(
        "n-final",
        {
            "kind": "final",
            "label": "Final Upgrade Plan",
            "subtitle": final_subtitle,
            "description": final_desc,
            "status": compat_status,
            "price": upgrade_cost,
        },
        1650,
        y_mid,
    )

    # Edges in Upgrade Mode (Clean Non-Crossing Professional Layout):
    # 1. Contextual edge from Existing Configuration to primary components
    if "cpu" in proposed:
        add_edge("n-existing", "n-cpu", label="Baseline Anchor", color="#94a3b8", dashed=True, animated=False)
    elif "motherboard" in proposed:
        add_edge("n-existing", "n-motherboard", label="Baseline Anchor", color="#94a3b8", dashed=True, animated=False)
    elif "gpu" in proposed:
        add_edge("n-existing", "n-gpu", label="Baseline Anchor", color="#94a3b8", dashed=True, animated=False)

    # 2. Hardware relationships among proposed components
    if "cpu" in proposed and "motherboard" in proposed:
        add_edge("n-cpu", "n-motherboard", label="Socket Match", color="#94a3b8")
    if "motherboard" in proposed and "cooler" in proposed:
        add_edge("n-motherboard", "n-cooler", label="Mounting & Thermal", color="#94a3b8")
    elif "cpu" in proposed and "cooler" in proposed:
        add_edge("n-cpu", "n-cooler", label="Mounting & Thermal", color="#94a3b8")
    if "motherboard" in proposed and "ram" in proposed:
        add_edge(
            "n-motherboard",
            "n-ram",
            label="Memory Bus",
            color="#94a3b8",
            source_handle="source-bottom",
            target_handle="target-top",
        )
    if "motherboard" in proposed and "gpu" in proposed:
        add_edge("n-motherboard", "n-gpu", label="PCIe Interface", color="#94a3b8")
    if "motherboard" in proposed and "storage" in proposed:
        add_edge("n-motherboard", "n-storage", label="M.2 NVMe / SATA", color="#94a3b8")
    if "gpu" in proposed and "psu" in proposed:
        add_edge("n-gpu", "n-psu", label="Power Delivery", color="#94a3b8")
    if "gpu" in proposed and "case" in proposed:
        add_edge("n-gpu", "n-case", label="GPU Clearance", color="#94a3b8")

    # If CPU and GPU exist without motherboard
    if "cpu" in proposed and "gpu" in proposed and "motherboard" not in proposed:
        add_edge("n-cpu", "n-gpu", label="PCIe Interface", color="#94a3b8")

    # 3. Clean Symmetrical Convergence into Final Upgrade Plan (Column 4 -> Column 5)
    connected_to_final = False
    if "cooler" in proposed:
        add_edge("n-cooler", "n-final", label="Height Clearance", color="#94a3b8")
        connected_to_final = True
    if "storage" in proposed:
        add_edge("n-storage", "n-final", label="Storage Array", color="#94a3b8")
        connected_to_final = True
    if "psu" in proposed:
        add_edge("n-psu", "n-final", label="Power Delivery", color="#94a3b8")
        connected_to_final = True
    if "case" in proposed:
        add_edge("n-case", "n-final", label="Form Factor Fit", color="#94a3b8")
        connected_to_final = True

    if not connected_to_final:
        if "gpu" in proposed:
            add_edge("n-gpu", "n-final", label="PCIe Interface", color="#94a3b8")
        elif "ram" in proposed:
            add_edge("n-ram", "n-final", label="Memory Bus", color="#94a3b8")
        elif prop_ids:
            add_edge(prop_ids[-1], "n-final", label="Upgrade Path", color="#94a3b8")

    return nodes, edges


def replace_component_in_workflow(
    workflow_state: Dict[str, Any],
    category: str,
    new_component_id: str,
    catalog: Optional[CatalogService] = None,
    perf_service: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Handles dynamic replacement of a component on the workflow canvas:
    - Replaces component
    - Re-evaluates compatibility across the entire configuration
    - Re-computes budget and ML estimates
    - Updates affected workflow nodes and edges
    """
    if catalog is None:
        catalog = CatalogService.get_instance()
    if perf_service is None:
        perf_service = get_performance_service()

    comp_record = catalog.get_component(new_component_id)
    if not comp_record:
        raise ValueError(f"Component ID '{new_component_id}' not found in catalog.")

    # Reconstitute components dictionary
    components = dict(workflow_state.get("components") or {})
    enriched_new = _enrich_component_metadata(comp_record, catalog, perf_service)

    components[category] = enriched_new

    mode = workflow_state.get("mode", "build")
    if mode == "build":
        # Recalculate total for full build
        total_cost = sum(c.get("price", 0) or 0 for c in components.values())
        budget = workflow_state.get("summary", {}).get("budget", total_cost)
        validation = validate_full_build(components)

        usage = workflow_state.get("inputs", {}).get("usage", "General Purpose")
        nodes, edges = _build_build_workflow_graph(
            usage=usage,
            budget=budget,
            total_cost=total_cost,
            components=components,
            validation_result=validation,
            notes=[f"Updated {category.upper()} to {enriched_new['name']}."],
        )
        summary = {
            "total": total_cost,
            "budget": budget,
            "remaining": budget - total_cost,
            "status": "compatible" if validation["status"] == "compatible" else "incompatible",
            "validationStatus": validation["status"],
            "checksCount": len(validation["checks"]),
            "notes": [f"Swapped {category.upper()} to {enriched_new['name']}."],
        }
    else:
        # Upgrade mode
        existing = workflow_state.get("existing") or {}
        goal = workflow_state.get("inputs", {}).get("goal", "Performance")
        deltas = workflow_state.get("deltas") or {}
        budget = workflow_state.get("summary", {}).get("budget", 0)

        # Swapped component is an active replacement
        components[category]["_reusable"] = False
        if components[category].get("upgrade_role") != "dependency":
            components[category]["upgrade_role"] = "primary"
        components[category]["dependency_reason"] = None

        # Re-run bounded dependency resolution loop on remaining retained components
        resolved_dependencies: set = set()
        for pass_num in range(1, 4):
            changed = False
            recheck_cats = [
                cat for cat, comp in components.items()
                if (comp.get("_reusable") is True or comp.get("upgrade_role") == "dependency")
                and cat != category and cat not in resolved_dependencies
            ]
            for cat in recheck_cats:
                comp = components[cat]
                res_f = evaluate_component_compatibility(comp, components)
                incompat_reasons = []
                for chk in res_f.get("checks", []):
                    if chk.get("status") == "incompatible":
                        pair_name = chk.get("pair", "")
                        if cat != "psu" and pair_name.startswith("PSU"):
                            continue
                        incompat_reasons.append(chk.get("reason", "Incompatible pairing"))
                for oc, ocomp in components.items():
                    if oc != cat and not ocomp.get("_reusable", False):
                        res_b = evaluate_component_compatibility(ocomp, {cat: comp})
                        for chk in res_b.get("checks", []):
                            if chk.get("status") == "incompatible":
                                pair_name = chk.get("pair", "")
                                if cat != "psu" and pair_name.startswith("PSU"):
                                    continue
                                if chk.get("reason") not in incompat_reasons:
                                    incompat_reasons.append(chk.get("reason", "Incompatible pairing"))

                if incompat_reasons:
                    dep_cand = _find_compatible_dependency_candidate(cat, components, catalog)
                    if dep_cand:
                        enr_cand = _enrich_component_metadata(dep_cand, catalog, perf_service)
                        enr_cand["_reusable"] = False
                        enr_cand["upgrade_role"] = "dependency"
                        enr_cand["dependency_reason"] = f"Required replacement: {'; '.join(incompat_reasons)}"
                        enr_cand["alternatives"] = _find_alternatives(cat, dep_cand, components, catalog, limit=4)
                        components[cat] = enr_cand
                        resolved_dependencies.add(cat)
                        changed = True
            if not changed:
                break

        validation = validate_full_build(components)
        total_cost = sum(c.get("price", 0) or 0 for c in components.values() if not c.get("_reusable", False))

        nodes, edges = _build_upgrade_workflow_graph(
            existing=existing,
            proposed=components,
            budget=budget,
            upgrade_cost=total_cost,
            goal=goal,
            deltas=deltas,
            validation=validation,
        )

        primary_cats = [cat for cat, c in components.items() if c.get("upgrade_role") == "primary"]
        dep_cats = [cat for cat, c in components.items() if c.get("upgrade_role") == "dependency"]
        ret_cats = [cat for cat, c in components.items() if c.get("upgrade_role") == "retained"]

        summary = {
            "total": total_cost,
            "budget": budget,
            "remaining": budget - total_cost,
            "status": "compatible" if validation["status"] == "compatible" else "warning",
            "validationStatus": validation["status"],
            "checksCount": len(validation["checks"]),
            "upgradedCategories": primary_cats + dep_cats,
            "primaryCategories": primary_cats,
            "dependentCategories": dep_cats,
            "retainedCategories": ret_cats,
            "upgradeRoles": {cat: c.get("upgrade_role") for cat, c in components.items()},
            "notes": [f"Swapped {category.upper()} to {enriched_new['name']}."],
        }

    return {
        "nodes": nodes,
        "edges": edges,
        "summary": summary,
        "components": components,
        "validation": validation,
    }
