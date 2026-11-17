"""
BuildWise-AI — FastAPI Backend Service

Exposes recommendation, compatibility, pricing, and project persistence APIs
for the React Flow frontend while preserving existing Python intelligence.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel, Field

from src.export import (
    generate_build_csv,
    generate_upgrade_csv,
    generate_build_pdf,
    generate_upgrade_pdf,
)

from src.performance_service import get_performance_service
from src.recommender.catalog_data import CatalogService
from src.recommender.staged_recommender import (
    generate_build_recommendation,
    generate_upgrade_recommendation,
    replace_component_in_workflow,
)
from src.storage.db import (
    add_history,
    delete_project,
    get_project,
    init_db,
    list_history,
    list_projects,
    save_project,
)

logger = logging.getLogger("buildwise_api")

# Initialize FastAPI application
app = FastAPI(
    title="BuildWise-AI API",
    description="Interactive AI-Powered PC Recommendation Platform API",
    version="1.0.0",
)

# Enable CORS for Vite frontend development server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
def on_startup():
    init_db()
    CatalogService.get_instance()
    logger.info("BuildWise-AI API started and catalog initialized.")


# =============================================================================
# Request / Response Pydantic Models
# =============================================================================

class BuildRequest(BaseModel):
    usage: str = Field(..., description="Primary usage (e.g. Gaming, Programming, Content Creation, Office Work)")
    budget: int = Field(..., gt=0, description="Total budget in Indian Rupees (INR)")


class UpgradeRequest(BaseModel):
    existing: Dict[str, Any] = Field(default_factory=dict, description="Existing PC components dictionary")
    budget: int = Field(..., gt=0, description="Upgrade budget in Indian Rupees (INR)")
    goal: str = Field(..., description="Primary upgrade goal (e.g. Better Gaming Performance, Faster Productivity)")


class ReplaceComponentRequest(BaseModel):
    category: str = Field(..., description="Component category to replace")
    new_component_id: str = Field(..., description="ID of the new replacement component from catalog")


class SaveProjectRequest(BaseModel):
    id: Optional[str] = None
    mode: str = Field(default="build")
    name: str
    createdAt: Optional[str] = None
    inputs: Dict[str, Any] = Field(default_factory=dict)
    recommendationSnapshot: Optional[Dict[str, Any]] = None
    nodes: List[Dict[str, Any]] = Field(default_factory=list)
    edges: List[Dict[str, Any]] = Field(default_factory=list)
    summary: Dict[str, Any] = Field(default_factory=dict)


# =============================================================================
# Health & Catalog Endpoints
# =============================================================================

@app.get("/api/health")
def health_check():
    """Health check endpoint for service status verification."""
    perf_svc = get_performance_service()
    return {
        "status": "ok",
        "app": "BuildWise-AI",
        "version": "1.0.0",
        "models": {
            "cpu_model_available": perf_svc.is_cpu_model_available(),
            "gpu_model_available": perf_svc.is_gpu_model_available(),
        },
    }


@app.get("/api/catalog/summary")
def get_catalog_summary():
    """Returns actual real-time dataset counts and model statuses."""
    catalog = CatalogService.get_instance()
    perf_svc = get_performance_service()
    
    # Calculate category counts
    cat_counts = catalog.df_components["category"].value_counts().to_dict()

    return {
        "components_count": len(catalog.df_components),
        "prices_count": len(catalog.df_prices),
        "benchmarks_count": len(catalog.df_benchmarks),
        "priced_components_count": len(catalog.prices_lookup),
        "cpu_models_available": perf_svc.is_cpu_model_available(),
        "gpu_models_available": perf_svc.is_gpu_model_available(),
        "categories": cat_counts,
    }


@app.get("/api/catalog/components")
def list_components(
    category: Optional[str] = Query(None, description="Optional category filter"),
    query: Optional[str] = Query(None, description="Search term for brand or model"),
    limit: int = Query(50, ge=1, le=200),
):
    """Searches and lists components from the production catalog with their prices."""
    catalog = CatalogService.get_instance()
    df = catalog.df_components

    if category:
        df = df[df["category"].str.casefold() == category.casefold()]

    if query:
        q = str(query).strip().casefold()
        df = df[
            df["brand"].str.casefold().str.contains(q, na=False) |
            df["model"].str.casefold().str.contains(q, na=False) |
            df["component_id"].str.casefold().str.contains(q, na=False)
        ]

    results = []
    for _, row in df.head(limit).iterrows():
        cid = row["component_id"]
        best_p = catalog.prices_lookup.get(cid)
        price_val = best_p[0]["price_inr"] if best_p else None
        results.append({
            "component_id": cid,
            "category": row["category"],
            "brand": row["brand"],
            "model": row["model"],
            "name": f"{row['brand']} {row['model']}".strip(),
            "price": price_val,
        })
    return results


# =============================================================================
# Recommendation Endpoints
# =============================================================================

@app.post("/api/build/recommend")
def build_recommendation(payload: BuildRequest):
    """
    Build Mode: Accepts EXACTLY two inputs (Primary Usage and Total Budget)
    and produces an interactive React Flow recommendation graph.
    """
    if payload.budget <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Budget must be a positive INR value.",
        )

    try:
        rec = generate_build_recommendation(payload.usage, payload.budget)
        if rec.get("error"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=rec["message"],
            )

        project_id = f"p_{int(rec['summary']['budget'])}_{int(rec['summary']['total'])}_{len(rec['nodes'])}"
        project_name = f"{payload.usage} Build · ₹{payload.budget:,}"

        # Persist project snapshot
        project_data = {
            "id": project_id,
            "mode": "build",
            "name": project_name,
            "inputs": {"usage": payload.usage, "budget": payload.budget},
            "recommendationSnapshot": rec,
            "nodes": rec["nodes"],
            "edges": rec["edges"],
            "summary": rec["summary"],
        }
        saved = save_project(project_data)
        add_history(project_id, "build", {"usage": payload.usage, "budget": payload.budget}, rec["summary"])

        return saved
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to generate build recommendation: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Recommendation failed: {str(exc)}",
        )


@app.post("/api/upgrade/recommend")
def upgrade_recommendation(payload: UpgradeRequest):
    """
    Upgrade Mode: Accepts existing hardware, budget, and upgrade goal,
    analyzing bottlenecks and recommending compatible component replacements.
    """
    if payload.budget <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Budget must be a positive INR value.",
        )

    try:
        rec = generate_upgrade_recommendation(payload.existing, payload.budget, payload.goal)
        project_id = f"p_up_{int(payload.budget)}_{len(rec['nodes'])}"
        project_name = f"Upgrade · {payload.goal} (₹{payload.budget:,})"

        project_data = {
            "id": project_id,
            "mode": "upgrade",
            "name": project_name,
            "inputs": {"existing": payload.existing, "budget": payload.budget, "goal": payload.goal},
            "recommendationSnapshot": rec,
            "nodes": rec["nodes"],
            "edges": rec["edges"],
            "summary": rec["summary"],
        }
        saved = save_project(project_data)
        add_history(project_id, "upgrade", {"goal": payload.goal, "budget": payload.budget}, rec["summary"])

        return saved
    except Exception as exc:
        logger.exception("Failed to generate upgrade recommendation: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upgrade recommendation failed: {str(exc)}",
        )


@app.post("/api/workflow/{project_id}/replace-component")
def replace_component(project_id: str, payload: ReplaceComponentRequest):
    """
    Dynamic Component Replacement:
    Swaps a component on the workflow canvas, re-evaluates deterministic compatibility,
    recalculates budget and ML scores, and updates workflow nodes/edges.
    """
    project = get_project(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID '{project_id}' not found.",
        )

    try:
        workflow_state = {
            "mode": project["mode"],
            "inputs": project["inputs"],
            "components": project["recommendationSnapshot"].get("components") or project["recommendationSnapshot"].get("proposed") or {},
            "existing": project["recommendationSnapshot"].get("existing") or {},
            "summary": project["summary"],
            "deltas": project["recommendationSnapshot"].get("deltas") or {},
        }
        updated_wf = replace_component_in_workflow(
            workflow_state,
            category=payload.category,
            new_component_id=payload.new_component_id,
        )

        project["nodes"] = updated_wf["nodes"]
        project["edges"] = updated_wf["edges"]
        project["summary"] = updated_wf["summary"]
        project["recommendationSnapshot"]["nodes"] = updated_wf["nodes"]
        project["recommendationSnapshot"]["edges"] = updated_wf["edges"]
        project["recommendationSnapshot"]["summary"] = updated_wf["summary"]
        project["recommendationSnapshot"]["components"] = updated_wf["components"]
        project["recommendationSnapshot"]["validation"] = updated_wf["validation"]

        saved = save_project(project)
        return saved
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as exc:
        logger.exception("Failed to replace component: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Component replacement failed: {str(exc)}",
        )


# =============================================================================
# Project Persistence & History Endpoints
# =============================================================================

@app.get("/api/projects")
def list_saved_projects(mode: Optional[str] = Query(None, description="Optional filter by mode")):
    """Lists saved projects."""
    return list_projects(mode=mode)


@app.get("/api/projects/{project_id}")
def get_saved_project(project_id: str):
    """Retrieves a single saved project by ID."""
    proj = get_project(project_id)
    if not proj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found.",
        )
    return proj


@app.post("/api/projects/save")
def persist_project(payload: SaveProjectRequest):
    """Updates or saves project state (e.g. repositioned nodes or edits)."""
    saved = save_project(payload.dict())
    return saved


@app.delete("/api/projects/{project_id}")
def delete_saved_project(project_id: str):
    """Deletes a saved project upon explicit user request."""
    success = delete_project(project_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found.",
        )
    return {"status": "deleted", "id": project_id}


@app.get("/api/history")
def get_recommendation_history(limit: int = Query(50, ge=1, le=100)):
    """Retrieves recommendation generation history."""
    return list_history(limit=limit)


# =============================================================================
# PDF & CSV Export Endpoints
# =============================================================================

@app.get("/api/export/{project_id}/pdf")
def export_project_pdf(project_id: str):
    """
    Exports a completed PC recommendation or upgrade plan as a publication-ready PDF report.
    """
    project = get_project(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID '{project_id}' not found.",
        )

    try:
        mode = str(project.get("mode", "build")).casefold()
        if mode == "upgrade":
            pdf_bytes = generate_upgrade_pdf(project)
        else:
            pdf_bytes = generate_build_pdf(project)

        safe_name = "".join(
            c for c in project.get("name", project_id) if c.isalnum() or c in ("-", "_", " ")
        ).strip().replace(" ", "_")
        filename = f"{safe_name or project_id}.pdf"

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Cache-Control": "no-cache",
            },
        )
    except Exception as exc:
        logger.exception("Failed to generate PDF export: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate PDF report: {str(exc)}",
        )


@app.get("/api/export/{project_id}/csv")
def export_project_csv(project_id: str):
    """
    Exports a completed PC recommendation or upgrade plan as an Excel-compatible CSV file.
    Uses UTF-8 with BOM (utf-8-sig) to preserve Rupee symbols and characters cleanly in Excel.
    """
    project = get_project(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID '{project_id}' not found.",
        )

    try:
        mode = str(project.get("mode", "build")).casefold()
        if mode == "upgrade":
            csv_text = generate_upgrade_csv(project)
        else:
            csv_text = generate_build_csv(project)

        csv_bytes = csv_text.encode("utf-8-sig")

        safe_name = "".join(
            c for c in project.get("name", project_id) if c.isalnum() or c in ("-", "_", " ")
        ).strip().replace(" ", "_")
        filename = f"{safe_name or project_id}.csv"

        return Response(
            content=csv_bytes,
            media_type="text/csv; charset=utf-8-sig",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Cache-Control": "no-cache",
            },
        )
    except Exception as exc:
        logger.exception("Failed to generate CSV export: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate CSV report: {str(exc)}",
        )


# =============================================================================
# Serve Built React Frontend Static Assets (Production Mode)
# =============================================================================

from pathlib import Path
FRONTEND_DIST = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"

if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST / "assets")), name="assets")

    @app.get("/{full_path:path}")
    def serve_frontend(full_path: str):
        if full_path.startswith("api"):
            raise HTTPException(status_code=404, detail="API route not found")
        index_file = FRONTEND_DIST / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
        raise HTTPException(status_code=404, detail="Frontend index.html not found.")
