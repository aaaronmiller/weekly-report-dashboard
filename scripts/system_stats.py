"""System section — cronjobs, updates, temperature, uptime, services.

Sources: crontab, /var/log/apt (package upgrades per month), systemd timers
and user services, thermal zones, uptime/kernel. Every source is optional and
failure-isolated (WSL limits battery/thermal data).
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Any


def _sh(cmd: list[str], timeout: int = 6) -> str:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.stdout
    except Exception:
        return ""


def _apt_upgrades_per_month() -> dict[str, int]:
    out: dict[str, int] = {}
    for p in [Path("/var/log/apt/history.log")] + sorted(Path("/var/log/apt").glob("history.log.*.gz")):
        try:
            if p.suffix == ".gz":
                import gzip
                text = gzip.open(p, "rt", errors="replace").read()
            else:
                text = p.read_text(errors="replace")
        except Exception:
            continue
        cur = None
        for line in text.splitlines():
            m = re.match(r"Start-Date:\s*(\d{4})-(\d{2})-\d{2}", line)
            if m:
                cur = f"{m.group(1)}-{m.group(2)}"
                continue
            if cur and ("Upgrade:" in line or "Install:" in line):
                out[cur] = out.get(cur, 0) + 1
    return out


def _cronjobs() -> list[str]:
    raw = _sh(["crontab", "-l"])
    return [l.strip() for l in raw.splitlines() if l.strip() and not l.strip().startswith("#")]


def _timers() -> list[str]:
    # strip the ticking LEFT column (would break SC-005): keep NEXT + UNIT + ACTIVATES
    raw = _sh(["systemctl", "list-timers", "--no-pager"])
    out = []
    for l in raw.splitlines():
        toks = l.split()
        if len(toks) >= 6:
            out.append(f"{toks[0]} {toks[1]} {toks[2]} -> {toks[-2]} ({toks[-1]})")
    return out[:12]


def _thermal() -> list[str]:
    out = []
    for z in sorted(Path("/sys/class/thermal").glob("thermal_zone*")):
        try:
            t = (z / "temp").read_text().strip()
            out.append(f"{z.name}: {int(t)/1000:.1f}°C")
        except Exception:
            pass
    return out


def build_system_stats(problems: list[dict] | None = None) -> dict[str, Any]:
    if problems is None:
        problems = []
    # boot time is stable per boot (uptime -p would change every minute and
    # break byte-identical rebuilds, SC-005)
    try:
        up_secs = float(Path("/proc/uptime").read_text().split()[0])
        from datetime import datetime, timezone, timedelta
        boot_time = (datetime.now(timezone.utc) - timedelta(seconds=up_secs)).strftime("%Y-%m-%d %H:%M UTC")
    except Exception:
        boot_time = "?"
    kernel = _sh(["uname", "-r"]).strip()
    try:
        from datetime import datetime, timezone
        boot = datetime.now(timezone.utc).isoformat()
    except Exception:
        boot = "?"
    upgrades = _apt_upgrades_per_month()
    cron = _cronjobs()
    timers = _timers()
    thermal = _thermal()
    # shell history: lines per month (zsh history, best effort)
    shell_by_month: dict[str, int] = {}
    zh = Path.home() / ".zsh_history"
    if zh.exists():
        try:
            import re as _re
            for line in zh.read_text(errors="replace").splitlines():
                mt = _re.search(r":\s*(\d{10})", line)
                if mt:
                    import datetime as _dt
                    mo = _dt.datetime.fromtimestamp(int(mt.group(1))).strftime("%Y-%m")
                    shell_by_month[mo] = shell_by_month.get(mo, 0) + 1
        except Exception:
            pass

    # dpkg install count (all-time, last 2000 lines)
    dpkg = _sh(["bash", "-c", "grep -c ' install ' /var/log/dpkg.log 2>/dev/null || echo 0"]).strip()
    # cronjobs log outcomes: parse ~/.local/state/cronjobs/logs/*.log per day
    cron_logs: dict[str, dict[str, Any]] = {}
    cron_dir = Path.home() / ".local/state/cronjobs/logs"
    if cron_dir.exists():
        for logf in sorted(cron_dir.glob("*.log")):
            job = logf.stem
            try:
                lines = logf.read_text(errors="replace").splitlines()
            except Exception:
                continue
            for line in lines[-400:]:
                m2 = re.match(r"(\d{4}-\d{2}-\d{2})", line)
                if m2:
                    day = m2.group(1)
                    slot = cron_logs.setdefault(day, {"day": day, "jobs": {}})
                    slot["jobs"].setdefault(job, {"runs": 0, "last": "?"})
                    slot["jobs"][job]["runs"] += 1
                    slot["jobs"][job]["last"] = line.strip()[:80]

    return {
        "cron_logs": [{"day": k, "jobs": v["jobs"]} for k, v in sorted(cron_logs.items())],
        "boot_time": boot_time,
        "kernel": kernel,
        "upgrades_by_month": [{"month": m, "packages": upgrades[m]} for m in sorted(upgrades)],
        "cronjobs": cron,
        "timers": timers,
        "shell_by_month": [{"month": k, "commands": shell_by_month[k]} for k in sorted(shell_by_month)],
        "thermal": thermal,
        "dpkg_installs_total": dpkg,
        "notes": ["WSL2 host: battery/temperature sources are limited; thermal zones read when present.",
                  "apt history parsed for package upgrades per month; dpkg total from dpkg.log."],
    }


if __name__ == "__main__":
    import json
    print(json.dumps(build_system_stats(), indent=1, default=str))
