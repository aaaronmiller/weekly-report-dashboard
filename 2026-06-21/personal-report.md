{
  "period": {
    "start": "2026-06-15",
    "end": "2026-06-21"
  },
  "generated_at": "2026-06-23T03:13:37.818447+00:00",
  "theme": "Weekly operating history",
  "summary": "Live weekly report data from git activity, session-file fallback, Hermes Kanban, and report artifacts.",
  "metrics": {
    "projects_total": 28,
    "sessions_total": 181,
    "commits_total": 90,
    "files_changed_total": 19669,
    "work_done": 10,
    "work_in_progress": 0,
    "work_planned": 0,
    "momentum_score": 100,
    "kanban_tasks_total": 25
  },
  "projects": [
    {
      "name": "aaa-memory",
      "path": "/home/cheta/code/aaa-memory",
      "state": "active",
      "sessions": 0,
      "commits": 23,
      "files_changed": 472,
      "last_activity": "2026-06-21",
      "evidence": "git",
      "recent_commit_subjects": [
        "fix: repair aaa-memory MCP server",
        "docs: add screenshot to README",
        "docs: add architecture screenshot",
        "docs: add shields.io badges",
        "git-audit-sync: auto-commit",
        "Add integration audit: wiki-memory vs aaa-memory functional comparison",
        "Add memz CLI, fix retrieval pipeline (ClawMem as warm tier), fix dream agent to read from ClawMem documents endpoint",
        "Add setup wizard (python3 -m aaa_memory.setup), fix Claude Code + Codex to point at aaa-memory",
        "Full README rewrite: install instructions per agent, architecture diagram, command reference, agent matrix, config docs, dream agent defaults, vector encoding specs, remote access, web UI status",
        "Cold tier: ClawMem FTS search + local fallback. ClawMem systemd service installed.",
        "Fold wiki-memory into aaa-memory:",
        "Agent integration stubs: hermes provider, qwen context, opencode parser, codex parser. Hermes plugin created at ~/.hermes/hermes-agent/plugins/memory/aaa-memory/"
      ],
      "done": [],
      "wip": [],
      "planned": []
    },
    {
      "name": "claude-code-proxy",
      "path": "/home/cheta/code/claude-code-proxy",
      "state": "active",
      "sessions": 0,
      "commits": 12,
      "files_changed": 102,
      "last_activity": "2026-06-20",
      "evidence": "git",
      "recent_commit_subjects": [
        "Fix SPA deep-link routing + make web UI port-agnostic",
        "Merge remote-tracking branch 'origin/main'",
        "git-audit-sync: auto-commit",
        "Config parity: manifest-driven settings across Web UI + TUI",
        "fix: xx help on bare invocation + correct pi aliases",
        "fix: remove double cg_run wrapping in aliases + installer",
        "Merge xx: --profile flag + Ghostty proxy window + health wait + --no-cg",
        "Wire unfed Prometheus metrics: circuit-breaker state + cascade switches",
        "docs: operator guide for enabling the F18 quota-aware allocator",
        "Merge feat/clutch-dynamic-tool-capability: F18 quota-aware allocator wired into runtime routing + committed hidden test suite",
        "Wire F18 quota-aware allocator into runtime routing; commit hidden test suite",
        "bit by bit"
      ],
      "done": [],
      "wip": [],
      "planned": []
    },
    {
      "name": "crash-guard",
      "path": "/home/cheta/code/crash-guard",
      "state": "active",
      "sessions": 0,
      "commits": 10,
      "files_changed": 14,
      "last_activity": "2026-06-20",
      "evidence": "git",
      "recent_commit_subjects": [
        "fix: restore UX improvements and add xx/rtx wrapper support",
        "refinement: Linux spawn warning + --go flag",
        "fix: add --safe mode + verify all crash paths",
        "fix: arrow_select display corruption + safe-spawn test + dedup",
        "new",
        "fix: session grouping \u2014 suppress singles, emphasize crash groups",
        "fix: terminal safety + ghostty pre-flight for X11/Wayland crash prevention",
        "refinement: multi-select terminal safety + crash-grouping fixes",
        "fix: 'o' toggle for omitted sessions + crash time-window grouping",
        "restore: full multi-select UI with arrows, space, archive, filter"
      ],
      "done": [],
      "wip": [],
      "planned": []
    },
    {
      "name": "custom-skills",
      "path": "/home/cheta/code/custom-skills",
      "state": "active",
      "sessions": 0,
      "commits": 8,
      "files_changed": 12,
      "last_activity": "2026-06-19",
      "evidence": "git",
      "recent_commit_subjects": [
        "git-audit-sync: add Pi model check (warns if current model differs from model-scan recommended)",
        "fix: REMEDIATION_PLAN.md appends with reposcan marker, Pi model check in repo-scan",
        "feat: --fix flag, --table output, REMEDIATION_PLAN.md creation",
        "refine v2: 17 changes from 4-session deliberative refinement",
        "feat: parallel workers, retry, lockfile, JSON output, since filter, submodule support, skip markers, dry-run diffs, custom commit msg",
        "fix: recursive repo discovery with find(1), fetch timeout, --maxdepth flag",
        "refine: git-audit-sync \u2014 6 HIGH-priority fixes from deliberative refinement",
        "feat: git-audit-sync skill \u2014 auto-audit, commit, push, pull all repos"
      ],
      "done": [],
      "wip": [],
      "planned": []
    },
    {
      "name": "datakiln",
      "path": "/home/cheta/code2/datakiln",
      "state": "active",
      "sessions": 0,
      "commits": 5,
      "files_changed": 1621,
      "last_activity": "2026-06-21",
      "evidence": "git",
      "recent_commit_subjects": [
        "README: add status badges",
        "Remediate dependency vulnerabilities",
        "Add project handoff status",
        "Harden live DOM workflow execution",
        "Stabilize workflow schema and executor"
      ],
      "done": [],
      "wip": [],
      "planned": []
    },
    {
      "name": "dalakiln_oldspecs",
      "path": "/home/cheta/code2/dalakiln_oldspecs",
      "state": "active",
      "sessions": 0,
      "commits": 5,
      "files_changed": 1621,
      "last_activity": "2026-06-21",
      "evidence": "git",
      "recent_commit_subjects": [
        "README: add status badges",
        "Remediate dependency vulnerabilities",
        "Add project handoff status",
        "Harden live DOM workflow execution",
        "Stabilize workflow schema and executor"
      ],
      "done": [],
      "wip": [],
      "planned": []
    },
    {
      "name": "super_agent_monitor",
      "path": "/home/cheta/code2/super_agent_monitor",
      "state": "active",
      "sessions": 0,
      "commits": 2,
      "files_changed": 15581,
      "last_activity": "2026-06-21",
      "evidence": "git",
      "recent_commit_subjects": [
        "git-audit-sync: auto-commit",
        "git-audit-sync: auto-commit"
      ],
      "done": [],
      "wip": [],
      "planned": []
    },
    {
      "name": "model-scan",
      "path": "/home/cheta/code/model-scan",
      "state": "active",
      "sessions": 0,
      "commits": 2,
      "files_changed": 18,
      "last_activity": "2026-06-19",
      "evidence": "git",
      "recent_commit_subjects": [
        "Phase 3 complete: arch_predictor, sentiment, reliability, paper extractor, empirical_adjustments, auto-update cron. AA cache refreshed (540 models, recalibrated 2026-06-19). DB scores updated, paid models removed (minimax, qwen3.6 no longer free).",
        "fix: cli_overall uses AI Index, not broken tier labels. -a means AI>45."
      ],
      "done": [],
      "wip": [],
      "planned": []
    },
    {
      "name": "ai-writing-submission-index",
      "path": "/home/cheta/code2/ai-writing-submission-index",
      "state": "active",
      "sessions": 0,
      "commits": 2,
      "files_changed": 4,
      "last_activity": "2026-06-21",
      "evidence": "git",
      "recent_commit_subjects": [
        "git-audit-sync: auto-commit",
        "README: replace Lovable boilerplate with real overview"
      ],
      "done": [],
      "wip": [],
      "planned": []
    },
    {
      "name": "research-lover",
      "path": "/home/cheta/code2/research-lover",
      "state": "active",
      "sessions": 0,
      "commits": 2,
      "files_changed": 4,
      "last_activity": "2026-06-21",
      "evidence": "git",
      "recent_commit_subjects": [
        "git-audit-sync: auto-commit",
        "README: replace Lovable boilerplate with real overview"
      ],
      "done": [],
      "wip": [],
      "planned": []
    },
    {
      "name": "agent-lexicon",
      "path": "/home/cheta/code2/agent-lexicon",
      "state": "active",
      "sessions": 0,
      "commits": 2,
      "files_changed": 4,
      "last_activity": "2026-06-21",
      "evidence": "git",
      "recent_commit_subjects": [
        "git-audit-sync: auto-commit",
        "README: replace Lovable boilerplate with real overview"
      ],
      "done": [],
      "wip": [],
      "planned": []
    },
    {
      "name": "delobotomize",
      "path": "/home/cheta/code2/delobotomize",
      "state": "active",
      "sessions": 0,
      "commits": 1,
      "files_changed": 66,
      "last_activity": "2026-06-21",
      "evidence": "git",
      "recent_commit_subjects": [
        "git-audit-sync: auto-commit"
      ],
      "done": [],
      "wip": [],
      "planned": []
    },
    {
      "name": "Kaleidoscope",
      "path": "/home/cheta/code2/Kaleidoscope",
      "state": "active",
      "sessions": 0,
      "commits": 1,
      "files_changed": 64,
      "last_activity": "2026-06-21",
      "evidence": "git",
      "recent_commit_subjects": [
        "git-audit-sync: auto-commit"
      ],
      "done": [],
      "wip": [],
      "planned": []
    },
    {
      "name": "ult-win-setup",
      "path": "/home/cheta/code2/ult-win-setup",
      "state": "active",
      "sessions": 0,
      "commits": 1,
      "files_changed": 29,
      "last_activity": "2026-06-21",
      "evidence": "git",
      "recent_commit_subjects": [
        "git-audit-sync: auto-commit"
      ],
      "done": [],
      "wip": [],
      "planned": []
    },
    {
      "name": "hand-gesture-music-player",
      "path": "/home/cheta/code2/hand-gesture-music-player",
      "state": "active",
      "sessions": 0,
      "commits": 1,
      "files_changed": 12,
      "last_activity": "2026-06-21",
      "evidence": "git",
      "recent_commit_subjects": [
        "git-audit-sync: auto-commit"
      ],
      "done": [],
      "wip": [],
      "planned": []
    },
    {
      "name": "t3ChatPlus",
      "path": "/home/cheta/code2/t3ChatPlus",
      "state": "active",
      "sessions": 0,
      "commits": 1,
      "files_changed": 12,
      "last_activity": "2026-06-21",
      "evidence": "git",
      "recent_commit_subjects": [
        "git-audit-sync: auto-commit"
      ],
      "done": [],
      "wip": [],
      "planned": []
    },
    {
      "name": "datamine",
      "path": "/home/cheta/code2/datamine",
      "state": "active",
      "sessions": 0,
      "commits": 1,
      "files_changed": 6,
      "last_activity": "2026-06-21",
      "evidence": "git",
      "recent_commit_subjects": [
        "git-audit-sync: auto-commit"
      ],
      "done": [],
      "wip": [],
      "planned": []
    },
    {
      "name": "gollama",
      "path": "/home/cheta/code2/gollama",
      "state": "active",
      "sessions": 0,
      "commits": 1,
      "files_changed": 4,
      "last_activity": "2026-06-21",
      "evidence": "git",
      "recent_commit_subjects": [
        "git-audit-sync: auto-commit"
      ],
      "done": [],
      "wip": [],
      "planned": []
    },
    {
      "name": "voicechat",
      "path": "/home/cheta/code2/voicechat",
      "state": "active",
      "sessions": 0,
      "commits": 1,
      "files_changed": 3,
      "last_activity": "2026-06-21",
      "evidence": "git",
      "recent_commit_subjects": [
        "git-audit-sync: auto-commit"
      ],
      "done": [],
      "wip": [],
      "planned": []
    },
    {
      "name": "agentic_framework_benchmark",
      "path": "/home/cheta/code2/agentic_framework_benchmark",
      "state": "active",
      "sessions": 0,
      "commits": 1,
      "files_changed": 3,
      "last_activity": "2026-06-21",
      "evidence": "git",
      "recent_commit_subjects": [
        "git-audit-sync: auto-commit"
      ],
      "done": [],
      "wip": [],
      "planned": []
    },
    {
      "name": "flowcanvas",
      "path": "/home/cheta/code2/flowcanvas",
      "state": "active",
      "sessions": 0,
      "commits": 1,
      "files_changed": 3,
      "last_activity": "2026-06-21",
      "evidence": "git",
      "recent_commit_subjects": [
        "git-audit-sync: auto-commit"
      ],
      "done": [],
      "wip": [],
      "planned": []
    },
    {
      "name": "prompt-harvester v1",
      "path": "/home/cheta/code2/prompt-harvester v1",
      "state": "active",
      "sessions": 0,
      "commits": 1,
      "files_changed": 3,
      "last_activity": "2026-06-21",
      "evidence": "git",
      "recent_commit_subjects": [
        "git-audit-sync: auto-commit"
      ],
      "done": [],
      "wip": [],
      "planned": []
    },
    {
      "name": "MACS",
      "path": "/home/cheta/code2/MACS",
      "state": "active",
      "sessions": 0,
      "commits": 1,
      "files_changed": 3,
      "last_activity": "2026-06-21",
      "evidence": "git",
      "recent_commit_subjects": [
        "git-audit-sync: auto-commit"
      ],
      "done": [],
      "wip": [],
      "planned": []
    },
    {
      "name": "open-gemini-deep-research",
      "path": "/home/cheta/code2/open-gemini-deep-research",
      "state": "active",
      "sessions": 0,
      "commits": 1,
      "files_changed": 3,
      "last_activity": "2026-06-21",
      "evidence": "git",
      "recent_commit_subjects": [
        "git-audit-sync: auto-commit"
      ],
      "done": [],
      "wip": [],
      "planned": []
    },
    {
      "name": "Tower-Creep-Symbiosis",
      "path": "/home/cheta/code2/Tower-Creep-Symbiosis",
      "state": "active",
      "sessions": 0,
      "commits": 1,
      "files_changed": 2,
      "last_activity": "2026-06-21",
      "evidence": "git",
      "recent_commit_subjects": [
        "git-audit-sync: auto-commit"
      ],
      "done": [],
      "wip": [],
      "planned": []
    },
    {
      "name": "wiki-memory",
      "path": "/home/cheta/code/wiki-memory",
      "state": "active",
      "sessions": 0,
      "commits": 1,
      "files_changed": 1,
      "last_activity": "2026-06-15",
      "evidence": "git",
      "recent_commit_subjects": [
        "test: fix Hermes hook script name in test parametrize"
      ],
      "done": [],
      "wip": [],
      "planned": []
    },
    {
      "name": "ripit",
      "path": "/home/cheta/code2/ripit",
      "state": "active",
      "sessions": 0,
      "commits": 1,
      "files_changed": 1,
      "last_activity": "2026-06-21",
      "evidence": "git",
      "recent_commit_subjects": [
        "README: add status badges"
      ],
      "done": [],
      "wip": [],
      "planned": []
    },
    {
      "name": "terminal_orphan_killer",
      "path": "/home/cheta/code2/terminal_orphan_killer",
      "state": "active",
      "sessions": 0,
      "commits": 1,
      "files_changed": 1,
      "last_activity": "2026-06-21",
      "evidence": "git",
      "recent_commit_subjects": [
        "git-audit-sync: auto-commit"
      ],
      "done": [],
      "wip": [],
      "planned": []
    }
  ],
  "done": [
    "weekly-report 2026-06-21: automate regeneration [done]",
    "weekly-report 2026-06-22: automate regeneration [done]",
    "weekly-report 2026-06-21: provision Grafana dashboard [done]",
    "weekly-report 2026-06-22: provision Grafana dashboard [done]",
    "weekly-report 2026-06-21: expose Prometheus metrics [done]",
    "weekly-report 2026-06-22: expose Prometheus metrics [done]",
    "weekly-report 2026-06-21: render dashboard [done]",
    "weekly-report 2026-06-22: render dashboard [done]",
    "weekly-report 2026-06-22: collect evidence [done]",
    "weekly-report 2026-06-21: collect evidence [done]"
  ],
  "wip": [],
  "planned": [],
  "daily_activity": [
    {
      "date": "2026-06-16",
      "sessions": 5
    },
    {
      "date": "2026-06-17",
      "sessions": 55
    },
    {
      "date": "2026-06-18",
      "sessions": 41
    },
    {
      "date": "2026-06-19",
      "sessions": 32
    },
    {
      "date": "2026-06-20",
      "sessions": 38
    },
    {
      "date": "2026-06-21",
      "sessions": 10
    }
  ],
  "agent_activity": [
    {
      "agent": "claude_code",
      "sessions": 115
    },
    {
      "agent": "pi_agent",
      "sessions": 34
    },
    {
      "agent": "codex",
      "sessions": 22
    },
    {
      "agent": "opencode",
      "sessions": 6
    },
    {
      "agent": "hermes",
      "sessions": 4
    }
  ],
  "caveats": [],
  "self_improvement": [
    "Dashboard now reads Hermes Kanban state instead of hand-only task lists.",
    "Prometheus exporter and Grafana provisioning artifacts are generated with the bundle.",
    "Session counts use CASS when populated and bounded session-file mtimes as fallback."
  ],
  "evidence": {
    "cass_health": {
      "available": true,
      "healthy": false,
      "error": "{\n  \"status\": \"unhealthy\",\n  \"healthy\": false,\n  \"health_level\": \"unhealthy\",\n  \"initialized\": true,\n  \"explanation\": null,\n  \"warnings\": [],\n  \"data_dir\": \"/home/cheta/.local/share/coding-agent-search\",\n  \"recommended_action\": \"Run 'cass status --json' for the exact readiness gap; run 'cass index --full' only for missing or stale derived search assets.\",\n  \"recommended_commands\": [\n    {\n      \"id\": \"refresh-lexical-index\",\n      \"command\": \"cass index --json --no-progress-events --data-dir /home/cheta/.local/share/coding-agent-search\",\n      \"purpose\": \"Index newly discovered sessions without a full rebuild.\",\n      \"safety\": \"writes-cass-archive-and-derived-index\",\n      \"run_when\": \"Run when the index is stale or pending.sessions is nonzero.\",\n      \"success_signal\": \"success=true, then pending.sessions=0 and index.fresh=true\",\n      \"parse_fields\": [\n        \"success\",\n        \"conversations\",\n        \"messages\",\n        \"error\"\n      ],\n      \"retry_after_ms\": null\n    },\n    {\n      \"id\": \"verify-refresh\",\n      \"command\": \"cass health --json --data-dir /home/cheta/.local/share/coding-agent-search\",\n      \"purpose\": \"Confirm the refresh cleared the readiness blocker.\",\n      \"safety\": \"read-only\",\n      \"run_when\": \"Run after refresh-lexical-index finishes.\",\n      \"success_signal\": \"healthy=true or recommended_commands changes to the next blocker\",\n      \"parse_fields\": [\n        \"status\",\n        \"healthy\",\n        \"state.index\",\n        \"recommended_commands\"\n      ],\n      \"retry_after_ms\": null\n    }\n  ],\n  \"errors\": [\n    \"index stale\"\n  ],\n  \"latency_ms\": 1,\n  \"rebuild_progress\": {\n    \"active\": false,\n    \"stalled\": false,\n    \"last_progress_at\": null,\n    \"last_progress_age_ms\": null,\n    \"mode\": null,\n    \"phase\": null,\n    \"processed_conversations\": null,\n    \"total_conversations\": null,\n    \"remaining_conversations\": null,\n    \"completion_ratio\": null,\n    \"indexed_docs\": null,\n    \"runtime_available\": false,\n    \"queue_depth\": null,\n    \"queue_capacity\": null,\n    \"queue_headroom\": null,\n    \"pending_batch_conversations\": null,\n    \"pending_batch_message_bytes\": null,\n    \"inflight_message_bytes\": null,\n    \"max_message_bytes_in_flight\": null,\n    \"inflight_message_bytes_headroom\": null,\n    \"controller_mode\": null,\n    \"controller_reason\": null,\n    \"updated_at\": null\n  },\n  \"db\": {\n    \"exists\": true,\n    \"opened\": true,\n    \"conversations\": null,\n    \"messages\": null,\n    \"open_error\": null,\n    \"counts_skipped\": true,\n    \"open_skipped\": true\n  },\n  \"doctor_summary\": {\n    \"schema_version\": 2,\n    \"surface\": \"health-summary\",\n    \"mode\": \"read-only-check\",\n    \"status\": \"skipped\",\n    \"outcome_kind\": \"no_op\",\n    \"health_class\": \"degraded-derived-assets\",\n    \"risk_level\": \"unknown\",\n    \"asset_class\": \"canonical_archive_db\",\n    \"fallback_mode\": \"none\",\n    \"authority_status\": \"read_only\",\n    \"coverage_delta\": {\n      \"status\": \"unknown\",\n      \"archive_conversation_count\": null,\n      \"visible_source_conversation_count\": null,\n      \"raw_mirror_manifest_count\": null,\n      \"db_projection_only_count\": null,\n      \"missing_current_source_count\": null,\n      \"conversation_delta\": null,\n      \"message_delta\": null,\n      \"semantic_vector_delta\": null,\n      \"derived_asset_delta\": null\n    },\n    \"blocked_reasons\": [],\n    \"plan_fingerprint\": null,\n    \"receipt_path\": null,\n    \"event_log_path\": null,\n    \"artifact_manifest_path\": null,\n    \"recommended_action\": \"Run 'cass doctor check --json' to refresh archive coverage and repair readiness.\",\n    \"redaction_status\": \"redacted\",\n    \"contract_provenance\": \"runtime\",\n    \"operation_outcome\": {\n      \"kind\": \"ok-read-only-diagnosed\",\n      \"reason\": \"health/status used bounded readiness evidence and recommends doctor check for full archive coverage\",\n      \"action_taken\": \"reported bounded health/status doctor summary without mutating archive data\",\n      \"action_not_taken\": \"did not run deep doctor collectors, source sync, rebuild, model verification, or filesystem-wide repair work\",\n      \"safe_to_retry\": true,\n      \"requires_override\": false,\n      \"data_loss_risk\": \"unknown\",\n      \"next_command\": \"cass doctor check --json\",\n      \"artifact_manifest_path\": null,\n      \"exit_code_kind\": \"success\"\n    },\n    \"doctor_available\": true,\n    \"safe_auto_run_eligible\": false,\n    \"last_receipt_path\": null,\n    \"failure_marker_path\": null,\n    \"repair_previously_failed\": false,\n    \"active_repair\": {\n      \"active\": false,\n      \"active_index_maintenance\": false,\n      \"repair_blocked_reason\": null\n    },\n    \"repair_recommended\": false,\n    \"repair_blocked_reason\": null,\n    \"doctor_check_recommended\": true,\n    \"archive_coverage_state\": \"not_checked\",\n    \"source_mirror_state\": \"not_checked\",\n    \"remote_source_sync\": {\n      \"schema_version\": 1,\n      \"status\": \"warn\",\n      \"source\": \"health-fast-local-config\",\n      \"checked\": true,\n      \"archive_checked\": false,\n      \"live_remote_probe_attempted\": false,\n      \"remote_source_state\": \"sync_gaps\",\n      \"sync_staleness\": \"fresh\",\n      \"local_mirror_state\": \"present\",\n      \"configured_remote_source_count\": 1,\n      \"archive_remote_conversation_count\": null,\n      \"sync_gap_count\": 1,\n      \"highest_gap_severity\": \"low\",\n      \"recommended_action\": \"Inspect the checksum-fingerprinted local mirror before deciding whether to index or promote remote evidence.\",\n      \"recommended_sync_commands\": [],\n      \"notes\": [\n        \"remote_source_sync is read-only and local-only: it reads sources.toml, sync_status.json, local mirror directories, and archive provenance rows only.\",\n        \"Missing or stale remote sync state is a freshness gap, not proof that archived cass conversations are lost.\",\n        \"Doctor never opens SSH sessions or mutates provider session logs while building this report.\",\n        \"health-fast-local-config checked remote source config, sync status, and local cass mirrors without live SSH probes or provider log mutation\"\n      ]\n    },\n    \"sole_copy_conversation_count\": 0,\n    \"cleanup_reclaimable_bytes\": null,\n    \"quarantine_summary\": null,\n    \"coverage_source\": {\n      \"status\": \"not_checked\",\n      \"source\": \"health-fast-state\",\n      \"confidence_tier\": \"unchecked\",\n      \"generated_at\": \"2026-06-23T03:13:10+00:00\",\n      \"stale_after_seconds\": 0,\n      \"source_report_id\": null,\n      \"recommended_action\": \"Run cass doctor check --json for current archive coverage; health/status did not run deep collectors.\"\n    },\n    \"health_status\": \"unhealthy\",\n    \"db_exists\": true\n  },\n  \"remote_source_sync\": {\n    \"schema_version\": 1,\n    \"status\": \"warn\",\n    \"source\": \"health-fast-local-config\",\n    \"checked\": true,\n    \"archive_checked\": false,\n    \"live_remote_probe_attempted\": false,\n    \"remote_source_state\": \"sync_gaps\",\n    \"sync_staleness\": \"fresh\",\n    \"local_mirror_state\": \"present\",\n    \"configured_remote_source_count\": 1,\n    \"archive_remote_conversation_count\": null,\n    \"sync_gap_count\": 1,\n    \"highest_gap_severity\": \"low\",\n    \"recommended_action\": \"Inspect the checksum-fingerprinted local mirror before deciding whether to index or promote remote evidence.\",\n    \"recommended_sync_commands\": [],\n    \"notes\": [\n      \"remote_source_sync is read-only and local-only: it reads sources.toml, sync_status.json, local mirror directories, and archive provenance rows only.\",\n      \"Missing or stale remote sync state is a freshness gap, not proof that archived cass conversations are lost.\",\n      \"Doctor never opens SSH sessions or mutates provider session logs while building this report.\",\n      \"health-fast-local-config checked remote source config, sync status, and local cass mirrors without live SSH probes or provider log mutation\"\n    ]\n  },\n  \"coverage_risk\": {\n    \"schema_version\": 1,\n    \"status\": \"unchecked_fast_health\",\n    \"confidence_tier\": \"unchecked\",\n    \"archive_conversation_count\": 0,\n    \"missing_current_source_count\": 0,\n    \"db_without_raw_mirror_count\": 0,\n    \"db_projection_only_count\": 0,\n    \"mirror_without_db_link_count\": 0,\n    \"current_source_newer_than_archive_count\": 0,\n    \"raw_mirror_db_link_count\": 0,\n    \"sole_copy_warning_count\": 0,\n    \"recommended_action\": \"Run 'cass doctor --json' for source coverage and sole-copy analysis.\"\n  },\n  \"policy_registry\": {\n    \"schema_version\": \"1\",\n    \"controllers\": [\n      {\n        \"controller_id\": \"lexical_rebuild_pipeline\",\n        \"policy_id\": \"lexical_rebuild.pipeline.v1\",\n        \"policy_version\": \"pipeline_settings_v1\",\n        \"status\": \"active\",\n        \"fallback_state\": \"not_needed\",\n        \"conservative_fallback\": false,\n        \"decision_reason\": \"pipeline settings active\",\n        \"inputs\": {\n          \"controller_loadavg_high_watermark_1m\": \"15.0\",\n          \"controller_loadavg_low_watermark_1m\": \"14.0\",\n          \"controller_mode\": \"auto\",\n          \"controller_restore_clear_samples\": \"3\",\n          \"controller_restore_hold_ms\": \"5000\",\n          \"page_prep_workers\": \"7\",\n          \"pipeline_channel_size\": \"4\",\n          \"pipeline_max_message_bytes_in_flight\": \"536870912\",\n          \"staged_merge_workers\": \"3\",\n          \"staged_shard_builders\": \"1\"\n        }\n      },\n      {\n        \"controller_id\": \"semantic_search\",\n        \"policy_id\": \"semantic.hybrid_preferred.v1\",\n        \"policy_version\": \"semantic_schema_1+chunking_1\",\n        \"status\": \"active\",\n        \"fallback_state\": \"not_needed\",\n        \"conservative_fallback\": false,\n        \"decision_reason\": \"semantic policy active\",\n        \"inputs\": {\n          \"chunk_timeout_seconds\": \"120\",\n          \"chunking_strategy_version\": \"1\",\n          \"download_policy\": \"opt_in\",\n          \"fast_dimension\": \"256\",\n          \"fast_tier_embedder\": \"hash\",\n          \"idle_delay_seconds\": \"30\",\n          \"max_backfill_rss_mb\": \"256\",\n          \"max_backfill_threads\": \"1\",\n          \"max_model_size_mb\": \"300\",\n          \"max_refinement_docs\": \"100\",\n          \"min_free_disk_mb\": \"200\",\n          \"mode\": \"hybrid_preferred\",\n          \"quality_dimension\": \"384\",\n          \"quality_tier_embedder\": \"minilm\",\n          \"quality_weight\": \"0.7\",\n          \"reranker\": \"ms-marco-minilm\",\n          \"semantic_available\": \"true\",\n          \"semantic_budget_mb\": \"500\",\n          \"semantic_fallback_mode\": \"none\",\n          \"semantic_schema_version\": \"1\"\n        }\n      }\n    ]\n  },\n  \"ingest_quarantine\": {\n    \"schema_version\": 1,\n    \"status\": \"ok\",\n    \"quarantined_conversations\": 0,\n    \"recent_quarantined_conversations\": 0,\n    \"recent_window_seconds\": 3600,\n    \"circuit_breaker_limit\": 25,\n    \"circuit_breaker_active\": false,\n    \"quarantine_files\": [],\n    \"newest_last_attempt_at_ms\": null,\n    \"recommended_action\": null\n  },\n  \"responsiveness\": {\n    \"current_capacity_pct\": 100,\n    \"resource_policy\": {\n      \"available_parallelism\": 16,\n      \"reserved_cores\": 2,\n      \"max_workers\": 14,\n      \"effective_worker_ceiling\": 14,\n      \"max_inflight_bytes\": 536870912,\n      \"min_inflight_bytes\": 1048576\n    },\n    \"healthy_streak\": 0,\n    \"shrink_count\": 0,\n    \"grow_count\": 0,\n    \"ticks_total\": 0,\n    \"disabled_via_env\": false,\n    \"last_snapshot\": null,\n    \"last_reason\": null,\n    \"recent_decisions\": [],\n    \"calibration\": {\n      \"mode\": \"conformal\",\n      \"load_window_len\": 0,\n      \"psi_window_len\": 0,\n      \"conformal_k\": 256,\n      \"conformal_k_min\": 32,\n      \"conformal_alpha_pressured\": 0.05000000074505806,\n      \"conformal_alpha_severe\": 0.009999999776482582,\n      \"drift_reset_count\": 0,\n      \"outliers_rejected\": 0,\n      \"observations_total\": 0,\n      \"load_pressured_q\": null,\n      \"load_severe_q\": null,\n      \"psi_pressured_q\": null,\n      \"psi_severe_q\": null\n    }\n  },\n  \"parallel_wal_shadow\": {\n    \"recent_chunks\": [],\n    \"chunks_observed\": 0,\n    \"cumulative_wall_micros\": 0,\n    \"chunk_errors\": 0,\n    \"active\": true,\n    \"epoch_plan_manifest\": {\n      \"schema_version\": 1,\n      \"mode\": \"shadow_epoch_plan\",\n      \"epoch_micros\": 40000,\n      \"commit_mode_allowed\": false,\n      \"fallback_decision\": \"collect_shadow_evidence\",\n      \"fallback_reason\": \"no shadow chunks observed yet; commit-mode promotion has no evidence window\",\n      \"logical_digest\": \"d9c2dba932c2b67701c69d4a4f054db1e5489f6835e068e8d1456e6bdd4a6d45\",\n      \"window_chunks\": 0,\n      \"total_chunks_observed\": 0,\n      \"successful_chunks\": 0,\n      \"failed_chunks\": 0,\n      \"total_conversations\": 0,\n      \"estimated_fsyncs_saved_vs_per_chunk\": 0,\n      \"planned_epochs\": [],\n      \"proof_obligations\": [\n        \"shadow-vs-baseline persisted-row digest equality\",\n        \"deterministic crash/replay at epoch flush checkpoints\",\n        \"fallback to current begin-concurrent writer on any chunk or manifest validation error\",\n        \"no commit-mode exposure while commit_mode_allowed is false\"\n      ]\n    }\n  },\n  \"runtime_optimizations\": {\n    \"simd_dot\": true,\n    \"parallel_search\": true,\n    \"preconvert_f16\": true,\n    \"config_source\": \"default\"\n  },\n  \"state\": {\n    \"index\": {\n      \"exists\": true,\n      \"status\": \"stale\",\n      \"reason\": \"lexical rebuild checkpoint is incomplete\",\n      \"fresh\": false,\n      \"last_indexed_at\": \"2026-06-21T13:01:32.742+00:00\",\n      \"age_seconds\": 137498,\n      \"stale\": true,\n      \"stale_threshold_seconds\": 300,\n      \"rebuilding\": false,\n      \"stalled\": false,\n      \"activity_at\": null,\n      \"documents\": null,\n      \"empty_with_messages\": false,\n      \"quarantined_conversations\": 0,\n      \"fingerprint\": {\n        \"current_db_fingerprint\": null,\n        \"checkpoint_fingerprint\": \"content-pending-v1:1159\",\n        \"matches_current_db_fingerprint\": null\n      },\n      \"checkpoint\": {\n        \"present\": true,\n        \"completed\": false,\n        \"db_matches\": true,\n        \"schema_matches\": true,\n        \"page_size_matches\": true,\n        \"page_size_compatible\": true\n      }\n    },\n    \"database\": {\n      \"exists\": true,\n      \"opened\": true,\n      \"conversations\": null,\n      \"messages\": null,\n      \"open_error\": null,\n      \"open_retryable\": false,\n      \"counts_skipped\": true,\n      \"open_skipped\": true\n    },\n    \"pending\": {\n      \"sessions\": 0,\n      \"watch_active\": false,\n      \"orphaned\": false\n    },\n    \"rebuild\": {\n      \"active\": false,\n      \"stalled\": false,\n      \"last_progress_at\": null,\n      \"last_progress_age_ms\": null,\n      \"orphaned\": false,\n      \"pid\": null,\n      \"mode\": null,\n      \"job_id\": null,\n      \"job_kind\": null,\n      \"phase\": null,\n      \"started_at\": null,\n      \"updated_at\": null,\n      \"processed_conversations\": null,\n      \"total_conversations\": null,\n      \"indexed_docs\": null,\n      \"pipeline\": {\n        \"workers\": 14,\n        \"available_parallelism\": 16,\n        \"reserved_cores\": 2,\n        \"tantivy_writer_threads\": 1,\n        \"staged_shard_builders\": 1,\n        \"staged_merge_workers\": 3,\n        \"controller_mode\": \"auto\",\n        \"controller_restore_clear_samples\": 3,\n        \"controller_restore_hold_ms\": 5000,\n        \"pipeline_max_message_bytes_in_flight\": 536870912,\n        \"page_prep_workers\": 7,\n        \"page_size\": 1024,\n        \"steady_batch_fetch_conversations\": 512,\n        \"startup_batch_fetch_conversations\": 32,\n        \"steady_commit_every_conversations\": 10000,\n        \"startup_commit_every_conversations\": 2048,\n        \"steady_commit_every_messages\": 800000,\n        \"startup_commit_every_messages\": 800000,\n        \"steady_commit_every_message_bytes\": 536870912,\n        \"startup_commit_every_message_bytes\": 134217728,\n        \"pipeline_channel_size\": 4,\n        \"controller_loadavg_high_watermark_1m\": 15.0,\n        \"controller_loadavg_low_watermark_1m\": 14.0,\n        \"runtime\": null\n      }\n    },\n    \"semantic\": {\n      \"status\": \"building\",\n      \"availability\": \"index_building\",\n      \"summary\": \"semantic fast tier is usable; higher-quality semantic backfill is still in progress\",\n      \"available\": true,\n      \"can_search\": true,\n      \"fallback_mode\": null,\n      \"preferred_backend\": \"fastembed\",\n      \"embedder_id\": \"fnv1a-384\",\n      \"vector_index_path\": \"/home/cheta/.local/share/coding-agent-search/vector_index/index-fnv1a-384.fsvi\",\n      \"model_dir\": null,\n      \"hnsw_path\": \"/home/cheta/.local/share/coding-agent-search/vector_index/hnsw-fnv1a-384.chsw\",\n      \"hnsw_ready\": false,\n      \"progressive_ready\": false,\n      \"feature_compiled_in\": true,\n      \"quality_tier_published\": false,\n      \"semantic_only_search_available\": true,\n      \"hint\": \"Semantic refinement is already usable; continue searching while higher-quality backfill finishes.\",\n      \"fast_tier\": {\n        \"present\": true,\n        \"ready\": true,\n        \"current_db_matches\": null,\n        \"conversation_count\": 752,\n        \"doc_count\": 65330,\n        \"embedder_id\": \"fnv1a-384\",\n        \"model_revision\": \"hash\",\n        \"completed_at\": \"2026-06-02T20:01:45.974+00:00\",\n        \"size_bytes\": 58092736\n      },\n      \"quality_tier\": {\n        \"present\": false,\n        \"ready\": false,\n        \"current_db_matches\": null,\n        \"conversation_count\": null,\n        \"doc_count\": null,\n        \"embedder_id\": null,\n        \"model_revision\": null,\n        \"completed_at\": null,\n        \"size_bytes\": null\n      },\n      \"backlog\": {\n        \"total_conversations\": 752,\n        \"fast_tier_processed\": 752,\n        \"fast_tier_remaining\": 0,\n        \"quality_tier_processed\": 0,\n        \"quality_tier_remaining\": 752,\n        \"pending_work\": true,\n        \"current_db_matches\": null,\n        \"computed_at\": \"2026-06-02T20:01:45.974+00:00\"\n      },\n      \"checkpoint\": {\n        \"active\": false,\n        \"tier\": null,\n        \"current_db_matches\": null,\n        \"completed\": null,\n        \"conversations_processed\": null,\n        \"total_conversations\": null,\n        \"progress_pct\": null,\n        \"docs_embedded\": null,\n        \"last_offset\": null,\n        \"saved_at\": null\n      }\n    },\n    \"ingest_quarantine\": {\n      \"schema_version\": 1,\n      \"status\": \"ok\",\n      \"quarantined_conversations\": 0,\n      \"recent_quarantined_conversations\": 0,\n      \"recent_window_seconds\": 3600,\n      \"circuit_breaker_limit\": 25,\n      \"circuit_breaker_active\": false,\n      \"quarantine_files\": [],\n      \"newest_last_attempt_at_ms\": null,\n      \"recommended_action\": null\n    },\n    \"policy_registry\": {\n      \"schema_version\": \"1\",\n      \"controllers\": [\n        {\n          \"controller_id\": \"lexical_rebuild_pipeline\",\n          \"policy_id\": \"lexical_rebuild.pipeline.v1\",\n          \"policy_version\": \"pipeline_settings_v1\",\n          \"status\": \"active\",\n          \"fallback_state\": \"not_needed\",\n          \"conservative_fallback\": false,\n          \"decision_reason\": \"pipeline settings active\",\n          \"inputs\": {\n            \"controller_loadavg_high_watermark_1m\": \"15.0\",\n            \"controller_loadavg_low_watermark_1m\": \"14.0\",\n            \"controller_mode\": \"auto\",\n            \"controller_restore_clear_samples\": \"3\",\n            \"controller_restore_hold_ms\": \"5000\",\n            \"page_prep_workers\": \"7\",\n            \"pipeline_channel_size\": \"4\",\n            \"pipeline_max_message_bytes_in_flight\": \"536870912\",\n            \"staged_merge_workers\": \"3\",\n            \"staged_shard_builders\": \"1\"\n          }\n        },\n        {\n          \"controller_id\": \"semantic_search\",\n          \"policy_id\": \"semantic.hybrid_preferred.v1\",\n          \"policy_version\": \"semantic_schema_1+chunking_1\",\n          \"status\": \"active\",\n          \"fallback_state\": \"not_needed\",\n          \"conservative_fallback\": false,\n          \"decision_reason\": \"semantic policy active\",\n          \"inputs\": {\n            \"chunk_timeout_seconds\": \"120\",\n            \"chunking_strategy_version\": \"1\",\n            \"download_policy\": \"opt_in\",\n            \"fast_dimension\": \"256\",\n            \"fast_tier_embedder\": \"hash\",\n            \"idle_delay_seconds\": \"30\",\n            \"max_backfill_rss_mb\": \"256\",\n            \"max_backfill_threads\": \"1\",\n            \"max_model_size_mb\": \"300\",\n            \"max_refinement_docs\": \"100\",\n            \"min_free_disk_mb\": \"200\",\n            \"mode\": \"hybrid_preferred\",\n            \"quality_dimension\": \"384\",\n            \"quality_tier_embedder\": \"minilm\",\n            \"quality_weight\": \"0.7\",\n            \"reranker\": \"ms-marco-minilm\",\n            \"semantic_available\": \"true\",\n            \"semantic_budget_mb\": \"500\",\n            \"semantic_fallback_mode\": \"none\",\n            \"semantic_schema_version\": \"1\"\n          }\n        }\n      ]\n    },\n    \"_meta\": {\n      \"timestamp\": \"2026-06-23T03:13:10+00:00\",\n      \"data_dir\": \"/home/cheta/.local/share/coding-agent-search\",\n      \"db_path\": \"/home/cheta/.local/share/coding-agent-search/agent_search.db\"\n    }\n  }\n}"
    },
    "activity_source": "cass",
    "cass_timeline": {
      "ok": true,
      "raw_shape": [
        "range",
        "total_sessions",
        "groups"
      ],
      "daily_activity": [
        {
          "date": "2026-06-16",
          "sessions": 5
        },
        {
          "date": "2026-06-17",
          "sessions": 55
        },
        {
          "date": "2026-06-18",
          "sessions": 41
        },
        {
          "date": "2026-06-19",
          "sessions": 32
        },
        {
          "date": "2026-06-20",
          "sessions": 38
        },
        {
          "date": "2026-06-21",
          "sessions": 10
        }
      ],
      "agent_activity": [
        {
          "agent": "claude_code",
          "sessions": 115
        },
        {
          "agent": "pi_agent",
          "sessions": 34
        },
        {
          "agent": "codex",
          "sessions": 22
        },
        {
          "agent": "opencode",
          "sessions": 6
        },
        {
          "agent": "hermes",
          "sessions": 4
        }
      ],
      "source": "cass"
    },
    "kanban": {
      "available": true,
      "db_path": "/home/cheta/.hermes/kanban.db",
      "counts": {
        "done": 25
      },
      "done": [
        "weekly-report 2026-06-21: automate regeneration [done]",
        "weekly-report 2026-06-22: automate regeneration [done]",
        "weekly-report 2026-06-21: provision Grafana dashboard [done]",
        "weekly-report 2026-06-22: provision Grafana dashboard [done]",
        "weekly-report 2026-06-21: expose Prometheus metrics [done]",
        "weekly-report 2026-06-22: expose Prometheus metrics [done]",
        "weekly-report 2026-06-21: render dashboard [done]",
        "weekly-report 2026-06-22: render dashboard [done]",
        "weekly-report 2026-06-22: collect evidence [done]",
        "weekly-report 2026-06-21: collect evidence [done]"
      ],
      "wip": [],
      "planned": []
    }
  }
}