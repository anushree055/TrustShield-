import sqlite3
import json
from pathlib import Path
from datetime import datetime, timezone

DB_PATH = Path(__file__).resolve().parent.parent / "database" / "trustshield.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_conn() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            input_type TEXT NOT NULL,
            input_preview TEXT NOT NULL,
            risk_score INTEGER NOT NULL,
            risk_level TEXT NOT NULL,
            scam_type TEXT NOT NULL,
            confidence INTEGER NOT NULL,
            result_json TEXT NOT NULL
        )
        """)
        # Recovery-assistant usage log (no sensitive data stored here)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS recovery_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            analysis_id INTEGER,
            created_at TEXT NOT NULL,
            severity TEXT NOT NULL,
            interaction_categories TEXT NOT NULL
        )
        """)
        conn.commit()

def save_analysis(input_type: str, input_preview: str, result: dict) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO analyses (created_at,input_type,input_preview,risk_score,risk_level,scam_type,confidence,result_json) VALUES (?,?,?,?,?,?,?,?)",
            (
                datetime.now(timezone.utc).isoformat(), input_type, input_preview[:160],
                result["risk_score"], result["risk_level"], result["likely_scam_type"], result["confidence"], json.dumps(result)
            )
        )
        conn.commit()
        return cur.lastrowid

def save_recovery_use(analysis_id: int | None, severity: str, interactions: list) -> None:
    """Log recovery-assistant usage without storing any sensitive credentials."""
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO recovery_log (analysis_id,created_at,severity,interaction_categories) VALUES (?,?,?,?)",
            (analysis_id, datetime.now(timezone.utc).isoformat(), severity, json.dumps(interactions))
        )
        conn.commit()

def list_history(limit: int = 100):
    with get_conn() as conn:
        rows = conn.execute("SELECT id,created_at,input_type,input_preview,risk_score,risk_level,scam_type,confidence FROM analyses ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        return [dict(r) for r in rows]

def get_history_item(item_id: int):
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM analyses WHERE id=?", (item_id,)).fetchone()
        if not row:
            return None
        data = dict(row)
        data["result"] = json.loads(data.pop("result_json"))
        return data

def delete_item(item_id: int):
    with get_conn() as conn:
        cur = conn.execute("DELETE FROM analyses WHERE id=?", (item_id,))
        conn.commit()
        return cur.rowcount > 0

def clear_history():
    with get_conn() as conn:
        conn.execute("DELETE FROM analyses")
        conn.commit()

def stats():
    with get_conn() as conn:
        total = conn.execute("SELECT COUNT(*) FROM analyses").fetchone()[0]
        high = conn.execute("SELECT COUNT(*) FROM analyses WHERE risk_score >= 61").fetchone()[0]
        avg = conn.execute("SELECT AVG(risk_score) FROM analyses").fetchone()[0]
        common = conn.execute("SELECT scam_type,COUNT(*) c FROM analyses GROUP BY scam_type ORDER BY c DESC LIMIT 1").fetchone()
        return {
            "total": total,
            "high_risk": high,
            "average_risk": round(avg or 0, 1),
            "most_common_scam": common[0] if common else "—"
        }
