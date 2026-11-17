"""
BuildWise-AI — Phase 11C: Machine Learning Performance Prediction Service

Provides a unified, resilient service layer that interfaces the trained CPU and GPU
regression pipelines with the Streamlit application.
Handles feature extraction, unit validation, missing specification detection,
Streamlit caching, and model failure containment.
"""
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import joblib
import numpy as np
import pandas as pd

from experiments.performance_prediction import config

logger = logging.getLogger("performance_service")

# Model and metadata file paths
CPU_MODEL_PATH = config.CURRENT_DIR / "models" / "best_cpu_pipeline.joblib"
GPU_MODEL_PATH = config.CURRENT_DIR / "models" / "best_gpu_pipeline.joblib"
CPU_METADATA_PATH = config.CURRENT_DIR / "models" / "cpu_model_metadata.json"
GPU_METADATA_PATH = config.CURRENT_DIR / "models" / "gpu_model_metadata.json"

# Hardware enrichment paths
GPU_ENRICHMENT_CSV = config.GPU_ENRICHMENT_CSV
GPU_FAMILY_GROUPS_CSV = config.GPU_FAMILY_GROUPS_CSV


def parse_specs_safely(raw_specs: Any) -> Dict[str, Any]:
    """Safely parses specs_json into a dictionary."""
    if isinstance(raw_specs, dict):
        return raw_specs
    if not raw_specs or pd.isna(raw_specs):
        return {}
    try:
        return json.loads(str(raw_specs))
    except (json.JSONDecodeError, TypeError):
        return {}


class PerformancePredictionService:
    """
    Singleton-style service managing CPU and GPU model loading, hardware feature
    extraction, unit validation, inference, and failure containment.
    """

    def __init__(self):
        self._cpu_pipeline = None
        self._gpu_pipeline = None
        self._cpu_metadata = None
        self._gpu_metadata = None
        self._gpu_enrichment_map = None
        self._gpu_family_map = None
        self._cpu_load_attempted = False
        self._gpu_load_attempted = False

    # -------------------------------------------------------------------------
    # Model Loading & Resource Management
    # -------------------------------------------------------------------------

    def get_cpu_pipeline(self):
        """Loads and caches the trained CPU pipeline."""
        if not self._cpu_load_attempted:
            self._cpu_load_attempted = True
            if CPU_MODEL_PATH.exists():
                try:
                    self._cpu_pipeline = joblib.load(CPU_MODEL_PATH)
                    logger.info("Successfully loaded CPU pipeline from %s", CPU_MODEL_PATH.name)
                except Exception as exc:
                    logger.warning("Failed to load CPU pipeline: %s", exc)
                    self._cpu_pipeline = None
            else:
                logger.warning("CPU model artifact not found at %s", CPU_MODEL_PATH)
                self._cpu_pipeline = None
        return self._cpu_pipeline

    def get_gpu_pipeline(self):
        """Loads and caches the trained GPU pipeline."""
        if not self._gpu_load_attempted:
            self._gpu_load_attempted = True
            if GPU_MODEL_PATH.exists():
                try:
                    self._gpu_pipeline = joblib.load(GPU_MODEL_PATH)
                    logger.info("Successfully loaded GPU pipeline from %s", GPU_MODEL_PATH.name)
                except Exception as exc:
                    logger.warning("Failed to load GPU pipeline: %s", exc)
                    self._gpu_pipeline = None
            else:
                logger.warning("GPU model artifact not found at %s", GPU_MODEL_PATH)
                self._gpu_pipeline = None
        return self._gpu_pipeline

    def is_cpu_model_available(self) -> bool:
        """Returns True if CPU pipeline is loaded and ready for inference."""
        return self.get_cpu_pipeline() is not None

    def is_gpu_model_available(self) -> bool:
        """Returns True if GPU pipeline is loaded and ready for inference."""
        return self.get_gpu_pipeline() is not None

    def get_cpu_metadata(self) -> Dict[str, Any]:
        """Loads CPU model training and validation metadata."""
        if self._cpu_metadata is None and CPU_METADATA_PATH.exists():
            try:
                with open(CPU_METADATA_PATH, "r", encoding="utf-8") as f:
                    self._cpu_metadata = json.load(f)
            except Exception as exc:
                logger.warning("Failed to load CPU metadata: %s", exc)
                self._cpu_metadata = {}
        return self._cpu_metadata or {}

    def get_gpu_metadata(self) -> Dict[str, Any]:
        """Loads GPU model training and validation metadata."""
        if self._gpu_metadata is None and GPU_METADATA_PATH.exists():
            try:
                with open(GPU_METADATA_PATH, "r", encoding="utf-8") as f:
                    self._gpu_metadata = json.load(f)
            except Exception as exc:
                logger.warning("Failed to load GPU metadata: %s", exc)
                self._gpu_metadata = {}
        return self._gpu_metadata or {}

    def _get_gpu_enrichment(self) -> Dict[str, Dict[str, Any]]:
        """Loads and caches GPU hardware feature enrichment lookup."""
        if self._gpu_enrichment_map is None:
            self._gpu_enrichment_map = {}
            if GPU_ENRICHMENT_CSV.exists():
                try:
                    df = pd.read_csv(GPU_ENRICHMENT_CSV)
                    df["val"] = df["verified_value"].combine_first(df["value"])
                    pivot = df.pivot(index="component_id", columns="feature_name", values="val")
                    self._gpu_enrichment_map = {
                        str(idx).strip(): row.dropna().to_dict()
                        for idx, row in pivot.iterrows()
                    }
                except Exception as exc:
                    logger.warning("Could not load GPU enrichment CSV: %s", exc)
        return self._gpu_enrichment_map

    def _get_gpu_family_groups(self) -> Dict[str, Dict[str, Any]]:
        """Loads and caches GPU family groups lookup."""
        if self._gpu_family_map is None:
            self._gpu_family_map = {}
            if GPU_FAMILY_GROUPS_CSV.exists():
                try:
                    df = pd.read_csv(GPU_FAMILY_GROUPS_CSV)
                    self._gpu_family_map = {
                        str(row["component_id"]).strip(): row.to_dict()
                        for _, row in df.iterrows()
                    }
                except Exception as exc:
                    logger.warning("Could not load GPU family groups CSV: %s", exc)
        return self._gpu_family_map

    # -------------------------------------------------------------------------
    # Feature Extraction & Unit Validation
    # -------------------------------------------------------------------------

    def extract_cpu_features(
        self, component_row: Dict[str, Any]
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Extracts and validates CPU predictive features from a component record.
        Validates units and boundary constraints.
        Returns:
            (features_dict, None) on success, or (None, failure_reason_str) on failure.
        """
        if not isinstance(component_row, dict):
            return None, "Invalid component record structure"

        specs = parse_specs_safely(component_row.get("specs_json"))

        # 1. Cores
        cores_raw = specs.get("cores")
        if cores_raw is None or str(cores_raw).strip() == "":
            return None, "Missing CPU cores specification"
        try:
            cores = int(cores_raw)
            if cores <= 0 or cores > 128:
                return None, f"CPU cores ({cores}) outside realistic range [1-128]"
        except (ValueError, TypeError):
            return None, f"Non-numeric CPU cores value: {cores_raw}"

        # 2. Threads
        threads_raw = specs.get("threads")
        if threads_raw is None or str(threads_raw).strip() == "":
            return None, "Missing CPU threads specification"
        try:
            threads = int(threads_raw)
            if threads < cores:
                return None, f"CPU threads ({threads}) cannot be fewer than cores ({cores})"
            if threads > 256:
                return None, f"CPU threads ({threads}) outside realistic range [1-256]"
        except (ValueError, TypeError):
            return None, f"Non-numeric CPU threads value: {threads_raw}"

        # 3. Boost Clock (GHz)
        boost_raw = specs.get("boost_ghz") or specs.get("boost_clock_ghz")
        if boost_raw is None or str(boost_raw).strip() == "":
            return None, "Missing CPU boost clock specification"
        try:
            boost_clock_ghz = float(boost_raw)
            # Handle accidental MHz inputs (e.g., 5000 MHz -> 5.0 GHz)
            if boost_clock_ghz > 100.0:
                boost_clock_ghz = boost_clock_ghz / 1000.0
            if boost_clock_ghz < 1.0 or boost_clock_ghz > 8.5:
                return None, f"CPU boost clock ({boost_clock_ghz:.2f} GHz) outside plausible range [1.0-8.5 GHz]"
        except (ValueError, TypeError):
            return None, f"Non-numeric CPU boost clock: {boost_raw}"

        # 4. Base Clock (GHz) — Optional/nullable, median imputed by model pipeline
        base_raw = specs.get("base_clock_ghz")
        base_clock_ghz: Optional[float] = None
        if base_raw is not None and str(base_raw).strip() != "":
            try:
                b_val = float(base_raw)
                if b_val > 100.0:
                    b_val = b_val / 1000.0
                if 0.5 <= b_val <= 7.0:
                    base_clock_ghz = b_val
            except (ValueError, TypeError):
                base_clock_ghz = None

        # 5. TDP / Base Power (Watts)
        tdp_raw = specs.get("tdp_w") or specs.get("tdp") or specs.get("base_power_w")
        if tdp_raw is None or str(tdp_raw).strip() == "":
            return None, "Missing CPU TDP / Power specification"
        try:
            tdp_w = float(tdp_raw)
            if tdp_w < 10.0 or tdp_w > 1000.0:
                return None, f"CPU TDP ({tdp_w}W) outside plausible range [10-1000W]"
        except (ValueError, TypeError):
            return None, f"Non-numeric CPU TDP value: {tdp_raw}"

        # 6. Brand
        brand = str(component_row.get("brand", "")).strip()
        if not brand:
            return None, "Missing CPU brand"

        # 7. Socket
        socket = str(specs.get("socket", "")).strip()
        if not socket:
            return None, "Missing CPU socket specification"

        # 8. RAM Type
        ram_type = str(specs.get("ram_type", "DDR4")).strip()
        if not ram_type:
            ram_type = "DDR4"

        return {
            "cores": cores,
            "threads": threads,
            "boost_clock_ghz": boost_clock_ghz,
            "base_clock_ghz": base_clock_ghz,
            "tdp_w": tdp_w,
            "brand": brand,
            "socket": socket,
            "ram_type": ram_type,
        }, None

    def extract_gpu_features(
        self, component_row: Dict[str, Any]
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Extracts and validates GPU predictive features from a component record,
        leveraging specs_json and the verified hardware enrichment lookup.
        Returns:
            (features_dict, None) on success, or (None, failure_reason_str) on failure.
        """
        if not isinstance(component_row, dict):
            return None, "Invalid component record structure"

        cid = str(component_row.get("component_id", "")).strip()
        specs = parse_specs_safely(component_row.get("specs_json"))
        enrich = self._get_gpu_enrichment().get(cid, {})
        fam = self._get_gpu_family_groups().get(cid, {})

        # 1. VRAM Capacity (GB)
        vram_raw = specs.get("vram_gb") or enrich.get("vram_gb")
        if vram_raw is None or str(vram_raw).strip() == "":
            return None, "Missing GPU VRAM specification"
        try:
            vram_gb = float(vram_raw)
            if vram_gb < 1.0 or vram_gb > 128.0:
                return None, f"GPU VRAM ({vram_gb} GB) outside realistic range [1-128 GB]"
        except (ValueError, TypeError):
            return None, f"Non-numeric GPU VRAM: {vram_raw}"

        # 2. Memory Bus Width (bits)
        bus_raw = enrich.get("memory_bus_width_bits") or specs.get("memory_bus_bits")
        if bus_raw is None or str(bus_raw).strip() == "":
            return None, "Missing GPU memory bus width specification"
        try:
            memory_bus_width_bits = int(bus_raw)
            if memory_bus_width_bits < 32 or memory_bus_width_bits > 2048:
                return None, f"GPU memory bus ({memory_bus_width_bits} bits) outside realistic range [32-2048 bits]"
        except (ValueError, TypeError):
            return None, f"Non-numeric GPU memory bus: {bus_raw}"

        # 3. Memory Bandwidth (GB/s)
        bw_raw = enrich.get("memory_bandwidth_gbps") or specs.get("memory_bandwidth_gbps")
        if bw_raw is None or str(bw_raw).strip() == "":
            return None, "Missing GPU memory bandwidth specification"
        try:
            memory_bandwidth_gbps = float(bw_raw)
            if memory_bandwidth_gbps < 10.0 or memory_bandwidth_gbps > 5000.0:
                return None, f"GPU memory bandwidth ({memory_bandwidth_gbps} GB/s) outside realistic range [10-5000 GB/s]"
        except (ValueError, TypeError):
            return None, f"Non-numeric GPU memory bandwidth: {bw_raw}"

        # 4. Base Clock (MHz)
        base_raw = enrich.get("base_clock_mhz") or specs.get("core_clock_mhz") or specs.get("base_clock_mhz")
        if base_raw is None or str(base_raw).strip() == "":
            return None, "Missing GPU base clock specification"
        try:
            base_clock_mhz = float(base_raw)
            if base_clock_mhz < 200.0 or base_clock_mhz > 4500.0:
                return None, f"GPU base clock ({base_clock_mhz} MHz) outside realistic range [200-4500 MHz]"
        except (ValueError, TypeError):
            return None, f"Non-numeric GPU base clock: {base_raw}"

        # 5. Boost Clock (MHz)
        boost_raw = enrich.get("boost_clock_mhz") or specs.get("boost_clock_mhz")
        if boost_raw is None or str(boost_raw).strip() == "":
            return None, "Missing GPU boost clock specification"
        try:
            boost_clock_mhz = float(boost_raw)
            if boost_clock_mhz < 200.0 or boost_clock_mhz > 4500.0:
                return None, f"GPU boost clock ({boost_clock_mhz} MHz) outside realistic range [200-4500 MHz]"
        except (ValueError, TypeError):
            return None, f"Non-numeric GPU boost clock: {boost_raw}"

        # 6. Board Power (Watts)
        power_raw = enrich.get("board_power_w") or specs.get("tgp_w") or specs.get("board_power_w")
        if power_raw is None or str(power_raw).strip() == "":
            return None, "Missing GPU board power (TGP) specification"
        try:
            board_power_w = float(power_raw)
            if board_power_w < 15.0 or board_power_w > 1200.0:
                return None, f"GPU board power ({board_power_w}W) outside realistic range [15-1200W]"
        except (ValueError, TypeError):
            return None, f"Non-numeric GPU board power: {power_raw}"

        # 7. Architecture
        architecture = str(
            enrich.get("architecture") or fam.get("architecture") or specs.get("architecture", "")
        ).strip()
        if not architecture:
            return None, "Missing GPU architecture specification"

        # 8. Chipmaker
        chipmaker = str(
            enrich.get("chipmaker")
            or fam.get("brand")
            or specs.get("chipmaker")
            or component_row.get("brand", "")
        ).strip()
        # Normalize chipmaker if AIB brand is listed
        if "nvidia" in chipmaker.lower():
            chipmaker = "NVIDIA"
        elif "amd" in chipmaker.lower() or "radeon" in chipmaker.lower():
            chipmaker = "AMD"
        elif "intel" in chipmaker.lower():
            chipmaker = "Intel"

        if not chipmaker:
            return None, "Missing GPU chipmaker specification"

        # 9. Memory Type
        memory_type = str(
            enrich.get("memory_type") or specs.get("memory_type", "GDDR6")
        ).strip()
        if not memory_type:
            memory_type = "GDDR6"

        return {
            "vram_gb": vram_gb,
            "memory_bus_width_bits": memory_bus_width_bits,
            "memory_bandwidth_gbps": memory_bandwidth_gbps,
            "base_clock_mhz": base_clock_mhz,
            "boost_clock_mhz": boost_clock_mhz,
            "board_power_w": board_power_w,
            "architecture": architecture,
            "chipmaker": chipmaker,
            "memory_type": memory_type,
        }, None

    # -------------------------------------------------------------------------
    # Inference Methods
    # -------------------------------------------------------------------------

    def predict_cpu(self, component_row: Dict[str, Any]) -> Dict[str, Any]:
        """
        Runs CPU performance prediction.
        Returns a structured prediction dictionary.
        """
        pipeline = self.get_cpu_pipeline()
        if pipeline is None:
            return {
                "status": "unavailable",
                "category": "cpu",
                "target_suite": "Cinebench R23",
                "target_metric": "Multi-Core Score",
                "score": None,
                "score_formatted": "Prediction Unavailable",
                "unit": "pts",
                "is_prediction": True,
                "model_name": "Ridge Regression (alpha=10.0)",
                "message": "CPU performance model artifact is not loaded or unavailable.",
                "features_used": None,
            }

        features, error_reason = self.extract_cpu_features(component_row)
        if features is None:
            return {
                "status": "unavailable",
                "category": "cpu",
                "target_suite": "Cinebench R23",
                "target_metric": "Multi-Core Score",
                "score": None,
                "score_formatted": "Prediction Unavailable",
                "unit": "pts",
                "is_prediction": True,
                "model_name": "Ridge Regression (alpha=10.0)",
                "message": f"Insufficient specifications: {error_reason}",
                "features_used": None,
            }

        try:
            df_input = pd.DataFrame([features])
            pred_arr = pipeline.predict(df_input)
            raw_score = float(pred_arr[0])

            if not np.isfinite(raw_score) or raw_score <= 0:
                logger.info("CPU model produced non-positive prediction: %s", raw_score)
                return {
                    "status": "unavailable",
                    "category": "cpu",
                    "target_suite": "Cinebench R23",
                    "target_metric": "Multi-Core Score",
                    "score": None,
                    "score_formatted": "Prediction Unavailable",
                    "unit": "pts",
                    "is_prediction": True,
                    "model_name": "Ridge Regression (alpha=10.0)",
                    "message": "Prediction Unavailable: Physical linear model extrapolation boundary reached for low-spec dual-core hardware.",
                    "features_used": features,
                }

            score = round(raw_score, 1)
            return {
                "status": "available",
                "category": "cpu",
                "target_suite": "Cinebench R23",
                "target_metric": "Multi-Core Score",
                "score": score,
                "score_formatted": f"{int(round(score)):,} pts",
                "unit": "pts",
                "is_prediction": True,
                "model_name": "Ridge Regression (alpha=10.0)",
                "training_context": "Trained on 180 empirical observations across 10 platform families (CV R²=0.917)",
                "message": None,
                "features_used": features,
            }
        except Exception as exc:
            logger.error("Error during CPU inference: %s", exc)
            return {
                "status": "error",
                "category": "cpu",
                "target_suite": "Cinebench R23",
                "target_metric": "Multi-Core Score",
                "score": None,
                "score_formatted": "Prediction Unavailable",
                "unit": "pts",
                "is_prediction": True,
                "model_name": "Ridge Regression (alpha=10.0)",
                "message": f"Inference execution failed: {exc}",
                "features_used": features,
            }

    def predict_gpu(self, component_row: Dict[str, Any]) -> Dict[str, Any]:
        """
        Runs GPU performance prediction.
        Returns a structured prediction dictionary.
        """
        pipeline = self.get_gpu_pipeline()
        if pipeline is None:
            return {
                "status": "unavailable",
                "category": "gpu",
                "target_suite": "3DMark Time Spy",
                "target_metric": "Graphics Score",
                "score": None,
                "score_formatted": "Prediction Unavailable",
                "unit": "pts",
                "is_prediction": True,
                "model_name": "Ridge Regression (alpha=1.0)",
                "message": "GPU performance model artifact is not loaded or unavailable.",
                "features_used": None,
            }

        features, error_reason = self.extract_gpu_features(component_row)
        if features is None:
            return {
                "status": "unavailable",
                "category": "gpu",
                "target_suite": "3DMark Time Spy",
                "target_metric": "Graphics Score",
                "score": None,
                "score_formatted": "Prediction Unavailable",
                "unit": "pts",
                "is_prediction": True,
                "model_name": "Ridge Regression (alpha=1.0)",
                "message": f"Insufficient specifications: {error_reason}",
                "features_used": None,
            }

        try:
            df_input = pd.DataFrame([features])
            pred_arr = pipeline.predict(df_input)
            raw_score = float(pred_arr[0])

            if not np.isfinite(raw_score) or raw_score <= 0:
                logger.info("GPU model produced non-positive prediction: %s", raw_score)
                return {
                    "status": "unavailable",
                    "category": "gpu",
                    "target_suite": "3DMark Time Spy",
                    "target_metric": "Graphics Score",
                    "score": None,
                    "score_formatted": "Prediction Unavailable",
                    "unit": "pts",
                    "is_prediction": True,
                    "model_name": "Ridge Regression (alpha=1.0)",
                    "message": "Prediction Unavailable: Physical linear model extrapolation boundary reached for low-spec hardware.",
                    "features_used": features,
                }

            score = round(raw_score, 1)
            return {
                "status": "available",
                "category": "gpu",
                "target_suite": "3DMark Time Spy",
                "target_metric": "Graphics Score",
                "score": score,
                "score_formatted": f"{int(round(score)):,} pts",
                "unit": "pts",
                "is_prediction": True,
                "model_name": "Ridge Regression (alpha=1.0)",
                "training_context": "Trained on 57 empirical observations across 14 silicon die groups (CV R²=0.902)",
                "message": None,
                "features_used": features,
            }
        except Exception as exc:
            logger.error("Error during GPU inference: %s", exc)
            return {
                "status": "error",
                "category": "gpu",
                "target_suite": "3DMark Time Spy",
                "target_metric": "Graphics Score",
                "score": None,
                "score_formatted": "Prediction Unavailable",
                "unit": "pts",
                "is_prediction": True,
                "model_name": "Ridge Regression (alpha=1.0)",
                "message": f"Inference execution failed: {exc}",
                "features_used": features,
            }

    def predict_component(self, component_row: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dispatches prediction based on component category.
        Strictly returns unsupported for non-CPU/GPU categories.
        """
        if not isinstance(component_row, dict):
            return {
                "status": "unsupported",
                "category": None,
                "score": None,
                "score_formatted": "—",
                "is_prediction": False,
                "message": "Invalid component record",
            }

        cat = str(component_row.get("category", "")).lower().strip()
        if cat == "cpu":
            return self.predict_cpu(component_row)
        elif cat == "gpu":
            return self.predict_gpu(component_row)
        else:
            return {
                "status": "unsupported",
                "category": cat,
                "score": None,
                "score_formatted": "—",
                "is_prediction": False,
                "message": f"ML performance prediction is not available for '{cat}' components. Only CPU and GPU models are trained.",
            }

    # -------------------------------------------------------------------------
    # Upgrade Comparison Utility
    # -------------------------------------------------------------------------

    def compare_predicted_performance(
        self, comp_a_row: Dict[str, Any], comp_b_row: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculates side-by-side model-estimated performance delta between
        two components of the same category (CPU or GPU).
        """
        cat_a = str(comp_a_row.get("category", "")).lower().strip()
        cat_b = str(comp_b_row.get("category", "")).lower().strip()

        if cat_a != cat_b or cat_a not in ("cpu", "gpu"):
            return {
                "status": "unavailable",
                "message": "Both components must belong to the same supported category (CPU or GPU).",
                "is_model_estimated": True,
            }

        pred_a = self.predict_component(comp_a_row)
        pred_b = self.predict_component(comp_b_row)

        if pred_a["status"] != "available" or pred_b["status"] != "available":
            reasons = []
            if pred_a["status"] != "available":
                reasons.append(f"Current hardware: {pred_a.get('message', 'unavailable')}")
            if pred_b["status"] != "available":
                reasons.append(f"Upgrade candidate: {pred_b.get('message', 'unavailable')}")
            return {
                "status": "unavailable",
                "message": " | ".join(reasons),
                "is_model_estimated": True,
            }

        score_a = pred_a["score"]
        score_b = pred_b["score"]
        delta = score_b - score_a
        pct_change = ((score_b - score_a) / score_a * 100.0) if score_a > 0 else 0.0

        return {
            "status": "available",
            "category": cat_a,
            "suite": pred_a["target_suite"],
            "metric": pred_a["target_metric"],
            "score_a": score_a,
            "score_b": score_b,
            "delta": delta,
            "pct_change": pct_change,
            "summary": f"{score_b:,.0f} vs {score_a:,.0f} pts ({pct_change:+.1f}%)",
            "is_model_estimated": True,
            "model_name": pred_a["model_name"],
        }


# Global shared instance
_SERVICE_INSTANCE: Optional[PerformancePredictionService] = None


def get_performance_service() -> PerformancePredictionService:
    """Returns the shared PerformancePredictionService singleton instance."""
    global _SERVICE_INSTANCE
    if _SERVICE_INSTANCE is None:
        _SERVICE_INSTANCE = PerformancePredictionService()
    return _SERVICE_INSTANCE
