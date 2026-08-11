"""Config helpers for env file."""
from __future__ import annotations
from pathlib import Path

ENV_PATH = Path(__file__).parent.parent / "config.env"

def load_env(path: Path = ENV_PATH) -> dict:
    data = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            line=line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k,v=line.split("=",1)
                k=k.strip()
                v=v.strip().strip('"').strip("'")
                data[k]=v
    return data

def save_env(updates: dict, path: Path = ENV_PATH) -> None:
    # preserve comments and other keys, update only given keys
    existing = {}
    comments = []
    order = []
    if path.exists():
        for line in path.read_text().splitlines():
            if line.strip().startswith("#") or not line.strip():
                comments.append(line)
            elif "=" in line:
                k,v=line.split("=",1)
                k=k.strip()
                existing[k]=v.strip().strip('"').strip("'")
                order.append(k)
    for k,v in updates.items():
        existing[k]=v
        if k not in order:
            order.append(k)
    # rewrite
    out_lines = []
    out_lines.append("# Weekly Report Dashboard Schedule")
    out_lines.append("# Controls how often the dashboard regeneration scripts run via cron/schedule.py")
    for k in order:
        if k in existing:
            # quote if contains space
            val = existing[k]
            if " " in val:
                val = f'"{val}"'
            out_lines.append(f"{k}={val}")
    # ensure known keys present
    for k in ["DASHBOARD_SCHEDULE","DASHBOARD_CRON"]:
        if k not in existing:
            out_lines.append(f"{k}=" + (existing.get(k,"") ))
    path.write_text("\n".join(out_lines) + "\n", encoding="utf-8")

def get_schedule() -> str:
    env = load_env()
    # DASHBOARD_CRON takes precedence if non-empty
    if env.get("DASHBOARD_CRON"):
        return env["DASHBOARD_CRON"]
    return env.get("DASHBOARD_SCHEDULE","daily")
