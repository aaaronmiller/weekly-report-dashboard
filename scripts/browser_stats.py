"""Browser section — browsing + YouTube history from Chrome.

Chrome History (Windows side, WSL mount) is a SQLite DB (urls, visits).
Copied to a temp file first to avoid lock contention; never writes to the
original. Graceful when the profile or DB is unavailable.

Chrome epoch: microseconds since 1601-01-01 UTC -> unix seconds = us/1e6 - 11644473600.
"""
from __future__ import annotations

import shutil
import sqlite3
import tempfile
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import urlparse
from typing import Any

CHROME_HISTORY = Path("/mnt/c/Users/Administrator/AppData/Local/Google/Chrome/User Data/Default/History")
CHROME_EPOCH_OFFSET = 11644473600  # seconds between 1601-01-01 and 1970-01-01


def _chrome_ts_to_iso(us: int) -> str | None:
    try:
        return datetime.fromtimestamp(us / 1e6 - CHROME_EPOCH_OFFSET, tz=timezone.utc).strftime("%Y-%m-%d %H:%M")
    except Exception:
        return None


def _domain(url: str) -> str:
    try:
        return urlparse(url).netloc.replace("www.", "")
    except Exception:
        return "?"


def build_browser_stats(problems: list[dict] | None = None) -> dict[str, Any]:
    if problems is None:
        problems = []
    if not CHROME_HISTORY.exists():
        problems.append({"path": str(CHROME_HISTORY), "reason": "chrome History not found; no browser data"})
        return {"months": [], "top_domains": [], "top_yt": [], "source": "chrome", "notes": ["Chrome History unavailable"]}

    # Consistent snapshot via SQLite backup (Chrome writes the DB live); cache
    # keyed by source mtime so repeated builds are byte-identical (SC-005).
    import hashlib
    cache_dir = Path(tempfile.gettempdir()) / "wr-dashboard"
    cache_dir.mkdir(exist_ok=True)
    key = hashlib.sha256(str(CHROME_HISTORY.stat().st_mtime_ns).encode()).hexdigest()[:16]
    tmp = cache_dir / f"history-{key}.db"
    if not tmp.exists():
        try:
            src = sqlite3.connect(f"file:{CHROME_HISTORY}?mode=ro", uri=True)
            dst = sqlite3.connect(tmp)
            src.backup(dst)
            dst.close(); src.close()
        except Exception as e:
            problems.append({"path": str(CHROME_HISTORY), "reason": f"backup failed: {e}"})
            return {"months": [], "top_domains": [], "top_yt": [], "source": "chrome", "notes": [f"backup failed: {e}"]}
    try:
        con = sqlite3.connect(f"file:{tmp}?mode=ro", uri=True)
        cur = con.cursor()
        cur.execute("""SELECT v.visit_time, u.url, u.title FROM visits v JOIN urls u ON u.id = v.url
                       ORDER BY v.visit_time DESC LIMIT 200000""")
        rows = cur.fetchall()
        con.close()
    except Exception as e:
        problems.append({"path": str(CHROME_HISTORY), "reason": f"history query failed: {e}"})
        return {"months": [], "top_domains": [], "top_yt": [], "source": "chrome", "notes": [f"query failed: {e}"]}

    months: dict[str, int] = {}
    domains: dict[str, int] = {}
    yt: dict[str, int] = {}
    yt_titles: dict[str, str] = {}
    hours = [0]*24
    for visit_us, url, title in rows:
        iso = _chrome_ts_to_iso(visit_us)
        if not iso:
            continue
        m = iso[:7]
        months[m] = months.get(m, 0) + 1
        d = _domain(url or "")
        domains[d] = domains.get(d, 0) + 1
        try:
            from datetime import datetime as _dt, timezone as _tz
            hours[_dt.fromtimestamp(visit_us/1e6 - CHROME_EPOCH_OFFSET, tz=_tz.utc).hour] += 1
        except Exception:
            pass
        if "youtube.com/watch" in (url or "") or "youtu.be" in (url or ""):
            key = url or "?"
            yt[key] = yt.get(key, 0) + 1
            if title and title.strip():
                yt_titles[key] = title.strip()[:90]

    month_out = [{"month": m, "visits": months[m]} for m in sorted(months)]
    top_domains = sorted(domains.items(), key=lambda kv: -kv[1])[:20]
    top_yt = [{"url": u, "title": yt_titles.get(u, u[:60]), "visits": c}
              for u, c in sorted(yt.items(), key=lambda kv: -kv[1])[:15]]
    total = sum(months.values())
    return {
        "source": "chrome history (windows profile, read-only copy)",
        "total_visits": total,
        "months": month_out,
        "top_domains": top_domains,
        "top_yt": top_yt,
        "hours": hours,
        "notes": ["History DB copied to temp before querying; original untouched.",
                  "YouTube rows = visits to watch URLs; titles from history titles."],
    }


if __name__ == "__main__":
    import json
    print(json.dumps(build_browser_stats(), indent=1, default=str))
