{
  "period": {
    "start": "2026-07-08",
    "end": "2026-07-08"
  },
  "generated_at": "2026-07-09T04:12:39.940388+00:00",
  "theme": "Daily operating history",
  "summary": "Live weekly report data from git activity, session-file fallback, Hermes Kanban, and report artifacts.",
  "metrics": {
    "projects_total": 3,
    "sessions_total": 4,
    "commits_total": 3,
    "files_changed_total": 88,
    "work_done": 10,
    "work_in_progress": 0,
    "work_planned": 0,
    "momentum_score": 100,
    "kanban_tasks_total": 50
  },
  "projects": [
    {
      "name": "living-documents",
      "path": "/home/cheta/code/living-documents",
      "state": "active",
      "sessions": 0,
      "commits": 1,
      "files_changed": 72,
      "last_activity": "2026-07-08",
      "evidence": "git",
      "recent_commit_subjects": [
        "Initial import"
      ],
      "done": [],
      "wip": [],
      "planned": []
    },
    {
      "name": "reggae-wars",
      "path": "/home/cheta/code/reggae-wars",
      "state": "active",
      "sessions": 0,
      "commits": 1,
      "files_changed": 15,
      "last_activity": "2026-07-08",
      "evidence": "git",
      "recent_commit_subjects": [
        "Initial import"
      ],
      "done": [],
      "wip": [],
      "planned": []
    },
    {
      "name": "quartermaster",
      "path": "/home/cheta/code/quartermaster",
      "state": "active",
      "sessions": 0,
      "commits": 1,
      "files_changed": 1,
      "last_activity": "2026-07-08",
      "evidence": "git",
      "recent_commit_subjects": [
        "server"
      ],
      "done": [],
      "wip": [],
      "planned": []
    }
  ],
  "done": [
    "weekly-report 2026-07-08: automate regeneration [done]",
    "weekly-report 2026-07-08: provision Grafana dashboard [done]",
    "weekly-report 2026-07-08: expose Prometheus metrics [done]",
    "weekly-report 2026-07-08: render dashboard [done]",
    "weekly-report 2026-07-08: collect evidence [done]",
    "weekly-report 2026-07-07: automate regeneration [done]",
    "weekly-report 2026-07-05: automate regeneration [done]",
    "weekly-report 2026-07-05: provision Grafana dashboard [done]",
    "weekly-report 2026-07-07: provision Grafana dashboard [done]",
    "weekly-report 2026-07-05: expose Prometheus metrics [done]"
  ],
  "wip": [],
  "planned": [],
  "daily_activity": [
    {
      "date": "2026-07-08",
      "sessions": 4
    }
  ],
  "agent_activity": [
    {
      "agent": "codex",
      "sessions": 4
    }
  ],
  "caveats": [
    "CASS did not provide populated session groups; session counts use bounded file-mtime fallback."
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
      "error": "{\n  \"status\": \"rebuilding\",\n  \"healthy\": false,\n  \"health_level\": \"rebuilding\",\n  \"initialized\": true,\n  \"explanation\": null,\n  \"warnings\": [],\n  \"data_dir\": \"/home/cheta/.local/share/coding-agent-search\",\n  \"recommended_action\": \"Index rebuild is already in progress\",\n  \"recommended_commands\": [\n    {\n      \"id\": \"poll-active-rebuild\",\n      \"command\": \"cass status --json --data-dir /home/cheta/.local/share/coding-agent-search\",\n      \"purpose\": \"Poll the active rebuild without starting a second writer.\",\n      \"safety\": \"read-only\",\n      \"run_when\": \"Run after a short delay while rebuild_progress.active is true.\",\n      \"success_signal\": \"rebuild_progress.active=false\",\n      \"parse_fields\": [\n        \"status\",\n        \"rebuild.active\",\n        \"rebuild_progress\",\n        \"recommended_commands\"\n      ],\n      \"retry_after_ms\": 30000\n    }\n  ],\n  \"errors\": [\n    \"index stale\",\n    \"index rebuild in progress\"\n  ],\n  \"latency_ms\": 113,\n  \"rebuild_progress\": {\n    \"active\": true,\n    \"stalled\": false,\n    \"last_progress_at\": \"2026-07-09T04:12:06.220+00:00\",\n    \"last_progress_age_ms\": 5890,\n    \"mode\": \"index\",\n    \"phase\": \"index\",\n    \"processed_conversations\": 1396,\n    \"total_conversations\": 1396,\n    \"remaining_conversations\": 0,\n    \"completion_ratio\": 1.0,\n    \"indexed_docs\": 116461,\n    \"runtime_available\": false,\n    \"queue_depth\": null,\n    \"queue_capacity\": null,\n    \"queue_headroom\": null,\n    \"pending_batch_conversations\": null,\n    \"pending_batch_message_bytes\": null,\n    \"inflight_message_bytes\": null,\n    \"max_message_bytes_in_flight\": null,\n    \"inflight_message_bytes_headroom\": null,\n    \"controller_mode\": null,\n    \"controller_reason\": null,\n    \"updated_at\": \"2026-07-09T04:12:11.329+00:00\"\n  },\n  \"db\": {\n    \"exists\": true,\n    \"opened\": true,\n    \"conversations\": null,\n    \"messages\": null,\n    \"open_error\": null,\n    \"counts_skipped\": true,\n    \"open_skipped\": true\n  },\n  \"doctor_summary\": {\n    \"schema_version\": 2,\n    \"surface\": \"health-summary\",\n    \"mode\": \"read-only-check\",\n    \"status\": \"blocked\",\n    \"outcome_kind\": \"blocked\",\n    \"health_class\": \"repair-blocked\",\n    \"risk_level\": \"unknown\",\n    \"asset_class\": \"canonical_archive_db\",\n    \"fallback_mode\": \"none\",\n    \"authority_status\": \"read_only\",\n    \"coverage_delta\": {\n      \"status\": \"unknown\",\n      \"archive_conversation_count\": null,\n      \"visible_source_conversation_count\": null,\n      \"raw_mirror_manifest_count\": null,\n      \"db_projection_only_count\": null,\n      \"missing_current_source_count\": null,\n      \"conversation_delta\": null,\n      \"message_delta\": null,\n      \"semantic_vector_delta\": null,\n      \"derived_asset_delta\": null\n    },\n    \"blocked_reasons\": [\n      \"index maintenance is active; mutating doctor repair should wait\"\n    ],\n    \"plan_fingerprint\": null,\n    \"receipt_path\": null,\n    \"event_log_path\": null,\n    \"artifact_manifest_path\": null,\n    \"recommended_action\": \"Wait for the active index operation to finish, then run 'cass doctor check --json'.\",\n    \"redaction_status\": \"redacted\",\n    \"contract_provenance\": \"runtime\",\n    \"operation_outcome\": {\n      \"kind\": \"repair-blocked\",\n      \"reason\": \"repair readiness is blocked by active work\",\n      \"action_taken\": \"reported bounded health/status doctor summary without mutating archive data\",\n      \"action_not_taken\": \"did not run deep doctor collectors, source sync, rebuild, model verification, or filesystem-wide repair work\",\n      \"safe_to_retry\": false,\n      \"requires_override\": false,\n      \"data_loss_risk\": \"unknown\",\n      \"next_command\": \"cass doctor check --json\",\n      \"artifact_manifest_path\": null,\n      \"exit_code_kind\": \"lock-busy\"\n    },\n    \"doctor_available\": true,\n    \"safe_auto_run_eligible\": false,\n    \"last_receipt_path\": null,\n    \"failure_marker_path\": null,\n    \"repair_previously_failed\": false,\n    \"active_repair\": {\n      \"active\": false,\n      \"active_index_maintenance\": true,\n      \"repair_blocked_reason\": \"index maintenance is active; mutating doctor repair should wait\"\n    },\n    \"repair_recommended\": false,\n    \"repair_blocked_reason\": \"index maintenance is active; mutating doctor repair should wait\",\n    \"doctor_check_recommended\": true,\n    \"archive_coverage_state\": \"not_checked\",\n    \"source_mirror_state\": \"not_checked\",\n    \"remote_source_sync\": {\n      \"schema_version\": 1,\n      \"status\": \"warn\",\n      \"source\": \"health-fast-local-config\",\n      \"checked\": true,\n      \"archive_checked\": false,\n      \"live_remote_probe_attempted\": false,\n      \"remote_source_state\": \"sync_gaps\",\n      \"sync_staleness\": \"fresh\",\n      \"local_mirror_state\": \"present\",\n      \"configured_remote_source_count\": 1,\n      \"archive_remote_conversation_count\": null,\n      \"sync_gap_count\": 1,\n      \"highest_gap_severity\": \"low\",\n      \"recommended_action\": \"Inspect the checksum-fingerprinted local mirror before deciding whether to index or promote remote evidence.\",\n      \"recommended_sync_commands\": [],\n      \"notes\": [\n        \"remote_source_sync is read-only and local-only: it reads sources.toml, sync_status.json, local mirror directories, and archive provenance rows only.\",\n        \"Missing or stale remote sync state is a freshness gap, not proof that archived cass conversations are lost.\",\n        \"Doctor never opens SSH sessions or mutates provider session logs while building this report.\",\n        \"health-fast-local-config checked remote source config, sync status, and local cass mirrors without live SSH probes or provider log mutation\"\n      ]\n    },\n    \"sole_copy_conversation_count\": 0,\n    \"cleanup_reclaimable_bytes\": null,\n    \"quarantine_summary\": null,\n    \"coverage_source\": {\n      \"status\": \"not_checked\",\n      \"source\": \"health-fast-state\",\n      \"confidence_tier\": \"unchecked\",\n      \"generated_at\": \"2026-07-09T04:12:12+00:00\",\n      \"stale_after_seconds\": 0,\n      \"source_report_id\": null,\n      \"recommended_action\": \"Run cass doctor check --json for current archive coverage; health/status did not run deep collectors.\"\n    },\n    \"health_status\": \"rebuilding\",\n    \"db_exists\": true\n  },\n  \"remote_source_sync\": {\n    \"schema_version\": 1,\n    \"status\": \"warn\",\n    \"source\": \"health-fast-local-config\",\n    \"checked\": true,\n    \"archive_checked\": false,\n    \"live_remote_probe_attempted\": false,\n    \"remote_source_state\": \"sync_gaps\",\n    \"sync_staleness\": \"fresh\",\n    \"local_mirror_state\": \"present\",\n    \"configured_remote_source_count\": 1,\n    \"archive_remote_conversation_count\": null,\n    \"sync_gap_count\": 1,\n    \"highest_gap_severity\": \"low\",\n    \"recommended_action\": \"Inspect the checksum-fingerprinted local mirror before deciding whether to index or promote remote evidence.\",\n    \"recommended_sync_commands\": [],\n    \"notes\": [\n      \"remote_source_sync is read-only and local-only: it reads sources.toml, sync_status.json, local mirror directories, and archive provenance rows only.\",\n      \"Missing or stale remote sync state is a freshness gap, not proof that archived cass conversations are lost.\",\n      \"Doctor never opens SSH sessions or mutates provider session logs while building this report.\",\n      \"health-fast-local-config checked remote source config, sync status, and local cass mirrors without live SSH probes or provider log mutation\"\n    ]\n  },\n  \"coverage_risk\": {\n    \"schema_version\": 1,\n    \"status\": \"unchecked_fast_health\",\n    \"confidence_tier\": \"unchecked\",\n    \"archive_conversation_count\": 0,\n    \"missing_current_source_count\": 0,\n    \"db_without_raw_mirror_count\": 0,\n    \"db_projection_only_count\": 0,\n    \"mirror_without_db_link_count\": 0,\n    \"current_source_newer_than_archive_count\": 0,\n    \"raw_mirror_db_link_count\": 0,\n    \"sole_copy_warning_count\": 0,\n    \"recommended_action\": \"Run 'cass doctor --json' for source coverage and sole-copy analysis.\"\n  },\n  \"policy_registry\": {\n    \"schema_version\": \"1\",\n    \"controllers\": [\n      {\n        \"controller_id\": \"lexical_rebuild_pipeline\",\n        \"policy_id\": \"lexical_rebuild.pipeline.v1\",\n        \"policy_version\": \"pipeline_settings_v1\",\n        \"status\": \"active\",\n        \"fallback_state\": \"not_needed\",\n        \"conservative_fallback\": false,\n        \"decision_reason\": \"pipeline settings active\",\n        \"inputs\": {\n          \"controller_loadavg_high_watermark_1m\": \"15.0\",\n          \"controller_loadavg_low_watermark_1m\": \"14.0\",\n          \"controller_mode\": \"auto\",\n          \"controller_restore_clear_samples\": \"3\",\n          \"controller_restore_hold_ms\": \"5000\",\n          \"page_prep_workers\": \"7\",\n          \"pipeline_channel_size\": \"4\",\n          \"pipeline_max_message_bytes_in_flight\": \"536870912\",\n          \"staged_merge_workers\": \"3\",\n          \"staged_shard_builders\": \"1\"\n        }\n      },\n      {\n        \"controller_id\": \"semantic_search\",\n        \"policy_id\": \"semantic.hybrid_preferred.v1\",\n        \"policy_version\": \"semantic_schema_1+chunking_1\",\n        \"status\": \"active\",\n        \"fallback_state\": \"not_needed\",\n        \"conservative_fallback\": false,\n        \"decision_reason\": \"semantic policy active\",\n        \"inputs\": {\n          \"chunk_timeout_seconds\": \"120\",\n          \"chunking_strategy_version\": \"1\",\n          \"download_policy\": \"opt_in\",\n          \"fast_dimension\": \"256\",\n          \"fast_tier_embedder\": \"hash\",\n          \"idle_delay_seconds\": \"30\",\n          \"max_backfill_rss_mb\": \"256\",\n          \"max_backfill_threads\": \"1\",\n          \"max_model_size_mb\": \"300\",\n          \"max_refinement_docs\": \"100\",\n          \"min_free_disk_mb\": \"200\",\n          \"mode\": \"hybrid_preferred\",\n          \"quality_dimension\": \"384\",\n          \"quality_tier_embedder\": \"minilm\",\n          \"quality_weight\": \"0.7\",\n          \"reranker\": \"ms-marco-minilm\",\n          \"semantic_available\": \"true\",\n          \"semantic_budget_mb\": \"500\",\n          \"semantic_fallback_mode\": \"none\",\n          \"semantic_schema_version\": \"1\"\n        }\n      }\n    ]\n  },\n  \"ingest_quarantine\": {\n    \"schema_version\": 1,\n    \"status\": \"ok\",\n    \"quarantined_conversations\": 0,\n    \"recent_quarantined_conversations\": 0,\n    \"recent_window_seconds\": 3600,\n    \"circuit_breaker_limit\": 25,\n    \"circuit_breaker_active\": false,\n    \"quarantine_files\": [],\n    \"newest_last_attempt_at_ms\": null,\n    \"recommended_action\": null\n  },\n  \"search_completeness\": {\n    \"quarantine_status\": \"ok\",\n    \"quarantined_conversations\": 0,\n    \"complete\": true,\n    \"can_search\": true,\n    \"coverage_suspect\": false,\n    \"impact\": \"search covers all known conversations; nothing is quarantined\",\n    \"next_command\": \"cass status --json\"\n  },\n  \"responsiveness\": {\n    \"current_capacity_pct\": 100,\n    \"resource_policy\": {\n      \"available_parallelism\": 16,\n      \"reserved_cores\": 2,\n      \"max_workers\": 14,\n      \"effective_worker_ceiling\": 14,\n      \"max_inflight_bytes\": 536870912,\n      \"min_inflight_bytes\": 1048576\n    },\n    \"healthy_streak\": 0,\n    \"shrink_count\": 0,\n    \"grow_count\": 0,\n    \"ticks_total\": 0,\n    \"disabled_via_env\": false,\n    \"last_snapshot\": null,\n    \"last_reason\": null,\n    \"recent_decisions\": [],\n    \"calibration\": {\n      \"mode\": \"conformal\",\n      \"load_window_len\": 0,\n      \"psi_window_len\": 0,\n      \"conformal_k\": 256,\n      \"conformal_k_min\": 32,\n      \"conformal_alpha_pressured\": 0.05000000074505806,\n      \"conformal_alpha_severe\": 0.009999999776482582,\n      \"drift_reset_count\": 0,\n      \"outliers_rejected\": 0,\n      \"observations_total\": 0,\n      \"load_pressured_q\": null,\n      \"load_severe_q\": null,\n      \"psi_pressured_q\": null,\n      \"psi_severe_q\": null\n    }\n  },\n  \"parallel_wal_shadow\": {\n    \"recent_chunks\": [],\n    \"chunks_observed\": 0,\n    \"cumulative_wall_micros\": 0,\n    \"chunk_errors\": 0,\n    \"active\": true,\n    \"epoch_plan_manifest\": {\n      \"schema_version\": 1,\n      \"mode\": \"shadow_epoch_plan\",\n      \"epoch_micros\": 40000,\n      \"commit_mode_allowed\": false,\n      \"fallback_decision\": \"collect_shadow_evidence\",\n      \"fallback_reason\": \"no shadow chunks observed yet; commit-mode promotion has no evidence window\",\n      \"logical_digest\": \"d9c2dba932c2b67701c69d4a4f054db1e5489f6835e068e8d1456e6bdd4a6d45\",\n      \"window_chunks\": 0,\n      \"total_chunks_observed\": 0,\n      \"successful_chunks\": 0,\n      \"failed_chunks\": 0,\n      \"total_conversations\": 0,\n      \"estimated_fsyncs_saved_vs_per_chunk\": 0,\n      \"planned_epochs\": [],\n      \"proof_obligations\": [\n        \"shadow-vs-baseline persisted-row digest equality\",\n        \"deterministic crash/replay at epoch flush checkpoints\",\n        \"fallback to current begin-concurrent writer on any chunk or manifest validation error\",\n        \"no commit-mode exposure while commit_mode_allowed is false\"\n      ]\n    }\n  },\n  \"runtime_optimizations\": {\n    \"simd_dot\": true,\n    \"parallel_search\": true,\n    \"preconvert_f16\": true,\n    \"config_source\": \"default\"\n  },\n  \"state\": {\n    \"index\": {\n      \"exists\": true,\n      \"status\": \"building\",\n      \"reason\": \"lexical rebuild is in progress\",\n      \"fresh\": false,\n      \"partial\": false,\n      \"partial_reason\": null,\n      \"last_indexed_at\": \"2026-07-08T19:04:38.026+00:00\",\n      \"age_seconds\": 32854,\n      \"stale\": false,\n      \"stale_threshold_seconds\": 300,\n      \"rebuilding\": true,\n      \"stalled\": false,\n      \"activity_at\": \"2026-07-09T04:12:11.329+00:00\",\n      \"documents\": null,\n      \"empty_with_messages\": false,\n      \"quarantined_conversations\": 0,\n      \"fingerprint\": {\n        \"current_db_fingerprint\": null,\n        \"checkpoint_fingerprint\": \"content-v1:1396:1396:123904\",\n        \"matches_current_db_fingerprint\": null\n      },\n      \"checkpoint\": {\n        \"present\": true,\n        \"completed\": true,\n        \"db_matches\": true,\n        \"schema_matches\": true,\n        \"page_size_matches\": true,\n        \"page_size_compatible\": true\n      }\n    },\n    \"database\": {\n      \"exists\": true,\n      \"opened\": true,\n      \"conversations\": null,\n      \"messages\": null,\n      \"open_error\": null,\n      \"open_retryable\": false,\n      \"counts_skipped\": true,\n      \"open_skipped\": true\n    },\n    \"pending\": {\n      \"sessions\": 0,\n      \"watch_active\": false,\n      \"orphaned\": false\n    },\n    \"rebuild\": {\n      \"active\": true,\n      \"stalled\": false,\n      \"last_progress_at\": \"2026-07-09T04:12:06.220+00:00\",\n      \"last_progress_age_ms\": 5890,\n      \"orphaned\": false,\n      \"pid\": 1608619,\n      \"mode\": \"index\",\n      \"job_id\": \"lexical_refresh-1783570274648-1608619\",\n      \"job_kind\": \"lexical_refresh\",\n      \"phase\": \"index\",\n      \"started_at\": \"2026-07-09T04:11:14.648+00:00\",\n      \"updated_at\": \"2026-07-09T04:12:11.329+00:00\",\n      \"processed_conversations\": 1396,\n      \"total_conversations\": 1396,\n      \"indexed_docs\": 116461,\n      \"pipeline\": {\n        \"workers\": 14,\n        \"available_parallelism\": 16,\n        \"reserved_cores\": 2,\n        \"tantivy_writer_threads\": 1,\n        \"staged_shard_builders\": 1,\n        \"staged_merge_workers\": 3,\n        \"controller_mode\": \"auto\",\n        \"controller_restore_clear_samples\": 3,\n        \"controller_restore_hold_ms\": 5000,\n        \"pipeline_max_message_bytes_in_flight\": 536870912,\n        \"page_prep_workers\": 7,\n        \"page_size\": 1024,\n        \"steady_batch_fetch_conversations\": 512,\n        \"startup_batch_fetch_conversations\": 32,\n        \"steady_commit_every_conversations\": 10000,\n        \"startup_commit_every_conversations\": 2048,\n        \"steady_commit_every_messages\": 800000,\n        \"startup_commit_every_messages\": 800000,\n        \"steady_commit_every_message_bytes\": 536870912,\n        \"startup_commit_every_message_bytes\": 134217728,\n        \"pipeline_channel_size\": 4,\n        \"controller_loadavg_high_watermark_1m\": 15.0,\n        \"controller_loadavg_low_watermark_1m\": 14.0,\n        \"runtime\": null\n      }\n    },\n    \"semantic\": {\n      \"status\": \"building\",\n      \"availability\": \"index_building\",\n      \"summary\": \"semantic fast tier is usable; higher-quality semantic backfill is still in progress\",\n      \"available\": true,\n      \"can_search\": true,\n      \"fallback_mode\": null,\n      \"preferred_backend\": \"fastembed\",\n      \"embedder_id\": \"fnv1a-384\",\n      \"vector_index_path\": \"/home/cheta/.local/share/coding-agent-search/vector_index/index-fnv1a-384.fsvi\",\n      \"model_dir\": null,\n      \"hnsw_path\": \"/home/cheta/.local/share/coding-agent-search/vector_index/hnsw-fnv1a-384.chsw\",\n      \"hnsw_ready\": false,\n      \"progressive_ready\": false,\n      \"feature_compiled_in\": true,\n      \"quality_tier_published\": false,\n      \"semantic_only_search_available\": true,\n      \"hint\": \"Semantic refinement is already usable; continue searching while higher-quality backfill finishes.\",\n      \"fast_tier\": {\n        \"present\": true,\n        \"ready\": true,\n        \"current_db_matches\": null,\n        \"conversation_count\": 752,\n        \"doc_count\": 65330,\n        \"embedder_id\": \"fnv1a-384\",\n        \"model_revision\": \"hash\",\n        \"completed_at\": \"2026-06-02T20:01:45.974+00:00\",\n        \"size_bytes\": 58092736\n      },\n      \"quality_tier\": {\n        \"present\": false,\n        \"ready\": false,\n        \"current_db_matches\": null,\n        \"conversation_count\": null,\n        \"doc_count\": null,\n        \"embedder_id\": null,\n        \"model_revision\": null,\n        \"completed_at\": null,\n        \"size_bytes\": null\n      },\n      \"backlog\": {\n        \"total_conversations\": 752,\n        \"fast_tier_processed\": 752,\n        \"fast_tier_remaining\": 0,\n        \"quality_tier_processed\": 0,\n        \"quality_tier_remaining\": 752,\n        \"pending_work\": true,\n        \"current_db_matches\": null,\n        \"computed_at\": \"2026-06-02T20:01:45.974+00:00\"\n      },\n      \"checkpoint\": {\n        \"active\": false,\n        \"tier\": null,\n        \"current_db_matches\": null,\n        \"completed\": null,\n        \"conversations_processed\": null,\n        \"total_conversations\": null,\n        \"progress_pct\": null,\n        \"docs_embedded\": null,\n        \"last_offset\": null,\n        \"saved_at\": null\n      }\n    },\n    \"ingest_quarantine\": {\n      \"schema_version\": 1,\n      \"status\": \"ok\",\n      \"quarantined_conversations\": 0,\n      \"recent_quarantined_conversations\": 0,\n      \"recent_window_seconds\": 3600,\n      \"circuit_breaker_limit\": 25,\n      \"circuit_breaker_active\": false,\n      \"quarantine_files\": [],\n      \"newest_last_attempt_at_ms\": null,\n      \"recommended_action\": null\n    },\n    \"policy_registry\": {\n      \"schema_version\": \"1\",\n      \"controllers\": [\n        {\n          \"controller_id\": \"lexical_rebuild_pipeline\",\n          \"policy_id\": \"lexical_rebuild.pipeline.v1\",\n          \"policy_version\": \"pipeline_settings_v1\",\n          \"status\": \"active\",\n          \"fallback_state\": \"not_needed\",\n          \"conservative_fallback\": false,\n          \"decision_reason\": \"pipeline settings active\",\n          \"inputs\": {\n            \"controller_loadavg_high_watermark_1m\": \"15.0\",\n            \"controller_loadavg_low_watermark_1m\": \"14.0\",\n            \"controller_mode\": \"auto\",\n            \"controller_restore_clear_samples\": \"3\",\n            \"controller_restore_hold_ms\": \"5000\",\n            \"page_prep_workers\": \"7\",\n            \"pipeline_channel_size\": \"4\",\n            \"pipeline_max_message_bytes_in_flight\": \"536870912\",\n            \"staged_merge_workers\": \"3\",\n            \"staged_shard_builders\": \"1\"\n          }\n        },\n        {\n          \"controller_id\": \"semantic_search\",\n          \"policy_id\": \"semantic.hybrid_preferred.v1\",\n          \"policy_version\": \"semantic_schema_1+chunking_1\",\n          \"status\": \"active\",\n          \"fallback_state\": \"not_needed\",\n          \"conservative_fallback\": false,\n          \"decision_reason\": \"semantic policy active\",\n          \"inputs\": {\n            \"chunk_timeout_seconds\": \"120\",\n            \"chunking_strategy_version\": \"1\",\n            \"download_policy\": \"opt_in\",\n            \"fast_dimension\": \"256\",\n            \"fast_tier_embedder\": \"hash\",\n            \"idle_delay_seconds\": \"30\",\n            \"max_backfill_rss_mb\": \"256\",\n            \"max_backfill_threads\": \"1\",\n            \"max_model_size_mb\": \"300\",\n            \"max_refinement_docs\": \"100\",\n            \"min_free_disk_mb\": \"200\",\n            \"mode\": \"hybrid_preferred\",\n            \"quality_dimension\": \"384\",\n            \"quality_tier_embedder\": \"minilm\",\n            \"quality_weight\": \"0.7\",\n            \"reranker\": \"ms-marco-minilm\",\n            \"semantic_available\": \"true\",\n            \"semantic_budget_mb\": \"500\",\n            \"semantic_fallback_mode\": \"none\",\n            \"semantic_schema_version\": \"1\"\n          }\n        }\n      ]\n    },\n    \"_meta\": {\n      \"timestamp\": \"2026-07-09T04:12:12+00:00\",\n      \"data_dir\": \"/home/cheta/.local/share/coding-agent-search\",\n      \"db_path\": \"/home/cheta/.local/share/coding-agent-search/agent_search.db\"\n    }\n  }\n}"
    },
    "activity_source": "session-file-mtime-fallback",
    "cass_timeline": {
      "ok": true,
      "raw_shape": [
        "range",
        "total_sessions",
        "groups"
      ],
      "daily_activity": [],
      "agent_activity": []
    },
    "kanban": {
      "available": true,
      "db_path": "/home/cheta/.hermes/kanban.db",
      "counts": {
        "done": 55
      },
      "done": [
        "weekly-report 2026-07-08: automate regeneration [done]",
        "weekly-report 2026-07-08: provision Grafana dashboard [done]",
        "weekly-report 2026-07-08: expose Prometheus metrics [done]",
        "weekly-report 2026-07-08: render dashboard [done]",
        "weekly-report 2026-07-08: collect evidence [done]",
        "weekly-report 2026-07-07: automate regeneration [done]",
        "weekly-report 2026-07-05: automate regeneration [done]",
        "weekly-report 2026-07-05: provision Grafana dashboard [done]",
        "weekly-report 2026-07-07: provision Grafana dashboard [done]",
        "weekly-report 2026-07-05: expose Prometheus metrics [done]"
      ],
      "wip": [],
      "planned": []
    }
  }
}