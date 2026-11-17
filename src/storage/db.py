"""
BuildWise-AI — Local SQLite Storage for Projects & Recommendation History

Maintains local SQLite persistence for saved PC builds, upgrade plans, and
workflow snapshots without altering the production catalog datasets.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
import sqlite3
from typing import Any, Dict, List, Optional

DEFAULT_DB_PATH = Path(os.environ.get("BUILDWISE_DB_PATH", Path(__file__).resolve().parent.parent.parent / "data" / "buildwise_projects.db"))


def get_connection(db_path: Optional[Path | str] = None) -> sqlite3.Connection:
    """Returns an SQLite connection configured with Row factory."""
    path = Path(db_path) if db_path else Path(os.environ.get("BUILDWISE_DB_PATH", DEFAULT_DB_PATH))
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Optional[Path | str] = None) -> None:
    """Initializes tables for projects and recommendation history."""
    conn = get_connection(db_path)
    try:
        with conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS projects (
                    id TEXT PRIMARY KEY,
                    mode TEXT NOT NULL,
                    name TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    inputs_json TEXT NOT NULL,
                    recommendation_snapshot_json TEXT NOT NULL,
                    nodes_json TEXT NOT NULL,
                    edges_json TEXT NOT NULL,
                    summary_json TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS history (
                    id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    mode TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    inputs_json TEXT NOT NULL,
                    summary_json TEXT NOT NULL
                )
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_projects_mode ON projects(mode)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_history_created_at ON history(created_at DESC)")
    finally:
        conn.close()


def save_project(project_data: Dict[str, Any], db_path: Optional[Path | str] = None) -> Dict[str, Any]:
    """
    Inserts or updates a project in the SQLite database.
    Does not modify CSV datasets.
    """
    init_db(db_path)
    conn = get_connection(db_path)
    try:
        now_iso = datetime.now(timezone.utc).isoformat()
        pid = str(project_data.get("id") or f"p_{int(datetime.now(timezone.utc).timestamp() * 1000)}")
        mode = str(project_data.get("mode", "build")).casefold()
        name = str(project_data.get("name", f"Untitled {mode.capitalize()}"))
        created_at = str(project_data.get("createdAt") or project_data.get("created_at") or now_iso)
        updated_at = now_iso

        inputs = project_data.get("inputs") or project_data.get("buildDetails") or project_data.get("upgradeDetails") or {}
        snapshot = project_data.get("recommendationSnapshot") or project_data.get("recommendation") or {}
        nodes = project_data.get("nodes", [])
        edges = project_data.get("edges", [])
        summary = project_data.get("summary", {})

        inputs_json = json.dumps(inputs)
        snapshot_json = json.dumps(snapshot)
        nodes_json = json.dumps(nodes)
        edges_json = json.dumps(edges)
        summary_json = json.dumps(summary)

        with conn:
            conn.execute(
                """
                INSERT INTO projects (
                    id, mode, name, created_at, updated_at,
                    inputs_json, recommendation_snapshot_json,
                    nodes_json, edges_json, summary_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    mode = excluded.mode,
                    name = excluded.name,
                    updated_at = excluded.updated_at,
                    inputs_json = excluded.inputs_json,
                    recommendation_snapshot_json = excluded.recommendation_snapshot_json,
                    nodes_json = excluded.nodes_json,
                    edges_json = excluded.edges_json,
                    summary_json = excluded.summary_json
                """,
                (
                    pid, mode, name, created_at, updated_at,
                    inputs_json, snapshot_json, nodes_json, edges_json, summary_json,
                ),
            )

        return get_project(pid, db_path=db_path)  # type: ignore
    finally:
        conn.close()


def get_project(project_id: str, db_path: Optional[Path | str] = None) -> Optional[Dict[str, Any]]:
    """Retrieves a single project by ID."""
    init_db(db_path)
    conn = get_connection(db_path)
    try:
        row = conn.execute(
            "SELECT * FROM projects WHERE id = ?", (project_id,)
        ).fetchone()
        if not row:
            return None
        return {
            "id": row["id"],
            "mode": row["mode"],
            "name": row["name"],
            "createdAt": row["created_at"],
            "updatedAt": row["updated_at"],
            "inputs": json.loads(row["inputs_json"]),
            "recommendationSnapshot": json.loads(row["recommendation_snapshot_json"]),
            "nodes": json.loads(row["nodes_json"]),
            "edges": json.loads(row["edges_json"]),
            "summary": json.loads(row["summary_json"]),
        }
    finally:
        conn.close()


def list_projects(mode: Optional[str] = None, db_path: Optional[Path | str] = None) -> List[Dict[str, Any]]:
    """Lists saved projects, optionally filtered by mode ('build' or 'upgrade')."""
    init_db(db_path)
    conn = get_connection(db_path)
    try:
        if mode:
            rows = conn.execute(
                "SELECT * FROM projects WHERE mode = ? ORDER BY updated_at DESC",
                (mode.casefold(),),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM projects ORDER BY updated_at DESC"
            ).fetchall()

        projects = []
        for r in rows:
            projects.append({
                "id": r["id"],
                "mode": r["mode"],
                "name": r["name"],
                "createdAt": r["created_at"],
                "updatedAt": r["updated_at"],
                "inputs": json.loads(r["inputs_json"]),
                "summary": json.loads(r["summary_json"]),
                "componentCount": len(json.loads(r["nodes_json"])),
            })
        return projects
    finally:
        conn.close()


def delete_project(project_id: str, db_path: Optional[Path | str] = None) -> bool:
    """Deletes a project record by ID."""
    init_db(db_path)
    conn = get_connection(db_path)
    try:
        with conn:
            cursor = conn.execute("DELETE FROM projects WHERE id = ?", (project_id,))
            return cursor.rowcount > 0
    finally:
        conn.close()


def add_history(
    project_id: str,
    mode: str,
    inputs: Dict[str, Any],
    summary: Dict[str, Any],
    db_path: Optional[Path | str] = None,
) -> str:
    """Logs a recommendation generation event to history."""
    init_db(db_path)
    conn = get_connection(db_path)
    try:
        hid = f"h_{int(datetime.now(timezone.utc).timestamp() * 1000)}"
        now_iso = datetime.now(timezone.utc).isoformat()
        with conn:
            conn.execute(
                """
                INSERT INTO history (id, project_id, mode, created_at, inputs_json, summary_json)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (hid, project_id, mode.casefold(), now_iso, json.dumps(inputs), json.dumps(summary)),
            )
        return hid
    finally:
        conn.close()


def list_history(limit: int = 50, db_path: Optional[Path | str] = None) -> List[Dict[str, Any]]:
    """Retrieves recent recommendation history logs."""
    init_db(db_path)
    conn = get_connection(db_path)
    try:
        rows = conn.execute(
            "SELECT * FROM history ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()
        return [
            {
                "id": r["id"],
                "projectId": r["project_id"],
                "mode": r["mode"],
                "createdAt": r["created_at"],
                "inputs": json.loads(r["inputs_json"]),
                "summary": json.loads(r["summary_json"]),
            }
            for r in rows
        ]
    finally:
        conn.close()
