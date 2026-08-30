{
  "period": {
    "start": "2026-08-28",
    "end": "2026-08-28"
  },
  "generated_at": "2026-08-29T00:04:07.701015+00:00",
  "theme": "Daily operating history",
  "summary": "Live weekly report data from git activity, session-file fallback, Hermes Kanban, and report artifacts.",
  "metrics": {
    "projects_total": 0,
    "sessions_total": 1,
    "commits_total": 0,
    "files_changed_total": 0,
    "work_done": 10,
    "work_in_progress": 0,
    "work_planned": 0,
    "momentum_score": 42,
    "kanban_tasks_total": 50
  },
  "projects": [],
  "done": [
    "weekly-report 2026-08-28: automate regeneration [done]",
    "weekly-report 2026-08-23: automate regeneration [done]",
    "weekly-report 2026-08-28: provision Grafana dashboard [done]",
    "weekly-report 2026-08-23: provision Grafana dashboard [done]",
    "weekly-report 2026-08-28: expose Prometheus metrics [done]",
    "weekly-report 2026-08-23: expose Prometheus metrics [done]",
    "weekly-report 2026-08-23: render dashboard [done]",
    "weekly-report 2026-08-28: render dashboard [done]",
    "weekly-report 2026-08-23: collect evidence [done]",
    "weekly-report 2026-08-28: collect evidence [done]"
  ],
  "wip": [],
  "planned": [],
  "daily_activity": [
    {
      "date": "2026-08-28",
      "sessions": 1
    }
  ],
  "agent_activity": [
    {
      "agent": "claude-code",
      "sessions": 1
    }
  ],
  "caveats": [
    "CASS did not provide populated session groups; session counts use bounded file-mtime fallback.",
    "No git repositories with commits were detected in the selected window; check roots or rely on session evidence."
  ],
  "self_improvement": [
    "Dashboard now reads Hermes Kanban state instead of hand-only task lists.",
    "Prometheus exporter and Grafana provisioning artifacts are generated with the bundle.",
    "Session counts use CASS when populated and bounded session-file mtimes as fallback."
  ],
  "evidence": {
    "cass_health": {
      "available": true,
      "healthy": false,
      "error": "TimeoutExpired(['cass', 'health', '--json'], 10)"
    },
    "activity_source": "session-file-mtime-fallback",
    "cass_timeline": {
      "ok": false,
      "error": "TimeoutExpired(['cass', 'timeline', '--since', '2026-08-28', '--until', '2026-08-28', '--json', '--group-by', 'day'], 30)",
      "daily_activity": [],
      "agent_activity": []
    },
    "kanban": {
      "available": true,
      "db_path": "/home/cheta/.hermes/kanban.db",
      "counts": {
        "done": 65
      },
      "done": [
        "weekly-report 2026-08-28: automate regeneration [done]",
        "weekly-report 2026-08-23: automate regeneration [done]",
        "weekly-report 2026-08-28: provision Grafana dashboard [done]",
        "weekly-report 2026-08-23: provision Grafana dashboard [done]",
        "weekly-report 2026-08-28: expose Prometheus metrics [done]",
        "weekly-report 2026-08-23: expose Prometheus metrics [done]",
        "weekly-report 2026-08-23: render dashboard [done]",
        "weekly-report 2026-08-28: render dashboard [done]",
        "weekly-report 2026-08-23: collect evidence [done]",
        "weekly-report 2026-08-28: collect evidence [done]"
      ],
      "wip": [],
      "planned": []
    }
  }
}