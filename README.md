# Weekly Report Dashboard — Project Plan (Overarching)

**Version:** 0.4.0 — ACR-I loop iteration 2, 6-meta assessed (2026-08-09)
**Status:** Active, 29 tests green, 34 weeks (26 primary via cass/raw-mirror Feb–Aug, 1610 sessions, 1968 effective), 1.40 MB, idempotent second run True, dev server `http://127.0.0.1:8765/index.html`, audit `11.7/14 READY`
**Constitution:** `/.specify/memory/constitution.md` — Principles I (canonical table first), II (missing≠0), III (provenance), IV (isolate per-item failure), V (self-validating), VI (legibility), VII (evidence over impression). Offline, stdlib-only, read-only corpus.

---

## 1. Why this project exists

Weekly summaries (`weekly-report-*.md` + 6 `weekly-metrics.json`) were a temporary crutch. `2026-02-07→2026-08-08` raw harness logs (1722 manifests across 8 providers: claude 524, claude_code 672, pi_agent 260, codex 117, antigravity 52, hermes 47, gemini 43, opencode 7) prove graphs of 12 weeks understated history by ~3 months and 53 sessions on `2026-08-01` alone. This dashboard now derives from **primary sources first**, weekly summaries second — with a dropdown to compare (`Data source: Primary vs Legacy`).

## 2. Meta-categories for organization & reporting

Six meta-domains, each with its own data source, visualizations, and audit. This replaces ad-hoc charts with need-driven groups.

| # | Meta | Source (harness locations via `platforms.json` + `/home/cheta/code/agents/sync.sh` + `raw-mirror/v1`) | Key questions | Owner |
|---|---|---|---|---|
| **M1** | **Telemetry / Heuristics** | `agent_search.db: token_usage, token_daily_stats, daily_stats, conversations.messages` + `~/.hermes/logs`, `~/.codex/sessions`, `~/.local/share/muse/sessions`, `~/.hermes/conversations` | What models/providers when/how? Error logs, API failure rates, latency, cache hit rates? Cost per harness? | `scripts/primary_audit.py` + `scripts/telemetry_audit.py` (new) |
| **M2** | **Projects — what’s done / remains** | `weekly-report-* -personal.md` Pipeline with Carry-Over + `carry_over` ledger (fuzzy/exact) + `weekly-metrics.json` Kanban fields | What’s incomplete and what unblocks it? Which projects stalled >3w? Easy wins? | `canonicalize.py` (fuzzy 61 vs exact 67) |
| **M3** | **Git Status** — via `git-audit-sync` | `~/code/*/.git` discovered by `scripts/audit_sync.py` (`repo ~/code --audit-only` → `~/git-audit-logs/*.json` + `.md`) — fast-forward pullable, pushable if origin owned, else flagged `NEEDS AGENT/INPUT` | Clean/dirty, ahead/behind, diverged, unpushed, no-remote, foreign origin? Which projects need push/pull? | `git-audit-sync` skill output (never mutated by dashboard, read-only) |
| **M4** | **Obsidian Vault** (`C:/Users/Administrator/Documents/chetaZ` → `/mnt/c/...` 352 md) | `*.md` frontmatter YAML, length, quantity, topic, linked files | Type/length/quantity/topic? Which vault notes map to which git project (missing yaml `project:` k-v)? Stale notes? | `scripts/vault_audit.py` (new) — audits each file, populates yaml, never deletes |
| **M5** | **Economics / Cost & Value** *(proposed)* | `token_usage` + model pricing + `agent_search.db:token_daily_stats` + manual time | Token $/project, session $/commit, value delivered per cost? Which harness is cheapest for which task? | `scripts/cost_audit.py` (new) |
| **M6** | **Health & Ops** *(proposed)* | `session.jsonl` resource_usage_sampled, `cass health`, disk, context-window pressure, `silence` failures | System health, stalled workers, quarantined conversations, burnout signals? | `scripts/health_audit.py` (new) |

Two new metas suggested above (M5/M6) close the loop between effort and outcome — essential for “what to fund next” decisions your prior 3 needs (immediate projects) omitted.

**Vault linking requirement:** Vault `352` files currently have sparse YAML. Need per-file audit: extract frontmatter, infer `project:` via basename/path/repo name fuzzy match, `topic:` via keywords, `length:` `wc -w`, `updated:` mtime, then populate `project:` + `status:` + `linked_repo:` k-v pairs. Produce `vault_project_map.json` for dashboard overlay.

## 3. Grouped visualizations (utility-driven, 4 groups × 3-4)

Each group answers a Need (N1-13 from prior analysis) and contains 3-4 mutually assisting charts — hover/brushing links them (Grafana-style correlations).

| Group | Need | Current + New Graphs | Utility | LLM summary location |
|---|---|---|---|---|
| **A: Stalled Work & Delivery Risk** | N1,N6,N10 | A1 Stall histogram (age), A2 Carry×Sessions scatter, A3 Completion velocity, A4 Dark lane (F2+) | “What is stalled, what needs doing?” | Group A header + `#viz-audit` |
| **B: Focus & Neglect · Easy Wins** | N2,N3,N7 | B1 Stacked sessions by harness (primary `agent_breakdown`), B2 Neglect detector (commits last 4w), B3 Easy-win table (`uncommitted 1-3`) | “What am I focused on vs ignoring?” | Group B header |
| **C: Rhythm & Sustainability** | N5,N8,N9 | C1 Contribution heatmap (weeks×Mon-Sun, synthetic when `daily_sessions` null), C3 Commit-size hist (files/commit) | “Am I sustainable or spiky?” | Group C header |
| **D: Narrative & Action** | N12,N13 | D1 Week story card (2-sentence synthesis), D2 Plan lane, D3 Diff since last week, Overall summary before data | “What’s the weekly story, what next?” | `#overall-summary` top + `#prose-panel` per-week + Group D footer |

Legacy `F1-F4`, table, ledger remain as detail-on-demand. Anti-slop (taste): no purple gradient, no Inter-only, no bento-everything — dark `bg #08090a`, `7170ff` accent sparingly, hierarchy via size/weight.

**LLM summaries:** Generated offline at build time via `scripts/summarize.py` (rule-templated synthesis, no network; future local `hermes`/`muse` model drop-in). Placement: overall top (`#overall-summary`), per-group headers (`#group-*-summary`), per-week 2-sentence card (`D1`/`#prose-panel`). Overall = copy-paste-ready weekly report conclusion.

## 4. Assess → Compare → Refine → Improve (ACR-I) — perpetual loop

Reusable, idempotent, loop-robust (can be run `n` times, second run identical if inputs unchanged).

```text
Assess  → scripts/audit_viz.py (7 dims, 0-2, max 14, threshold 10) + scripts/primary_audit.py --check + repo --audit-only + vault_audit --check
Compare → payload `algorithms` (primary vs legacy, fuzzy vs exact, weighted vs legacy, improved vs legacy, combined vs threshold/adaptive) + `Data source` dropdown live compare + table row hide/show
Refine  → edit viz that scored <10 (e.g., legacy 9/14 → add correlation), or data source that missed months (add primary)
Improve → python3 scripts/build_dashboard.py (byte-identical if inputs unchanged) → re-audit → score 11.7/14 READY
```

**Loop contract:**
- Pure functions, stdlib only, `isolate per-item failure` (one corrupt manifest → problem, not abort).
- Provenance on every number (`source_bundle`, `retrieved_at`, `per_harness`).
- Idempotent: `retrieved_at = max started_at` per week, not `now()`; re-run `n` times yields identical `index.html` after warmup (verified `idempotent True` second run).
- Invoke: `python3 scripts/audit_viz.py --json && python3 scripts/build_dashboard.py --check && python3 scripts/audit_viz.py` — loop until `ready:true`.

## 5. Next step proposal — should we run the loop again?

**Yes — with the new meta-framework as the Assess input.** Prior loop (Analysis → Grouped upgrade + Primary pipeline) raised `Overall 11.7/14 READY` from `~9` but legacy F1-F4 still isolated, vault unlinked, telemetry absent.

**Proposed next iteration (not yet executed, awaiting approval):**
1. **Assess** with 6-meta audit: run `repo ~/code --audit-only` → ingest `~/git-audit-logs/*.json` for M3; run `scripts/vault_audit.py --check /mnt/c/.../chetaZ` → report yaml coverage (expected <30% `project:` populated); run `scripts/telemetry_audit.py --check` → error rate per provider.
2. **Compare** primary heatmap vs legacy gaps (28 weeks missing bundles) + vault `352` files vs 12 linked repos → gap size.
3. **Refine** implement M1/M3/M4 minimal viz: `M1: Provider × Error rate`, `M3: Git clean/dirty matrix`, `M4: Vault files per project` (bar, linked vs unlinked), plus M5/M6 stubs.
4. **Improve** rebuild, re-score — target `Overall ≥12.5/14`, and `README` self-updates (this file) with new scores.

**Robustness of loop:** Yes — each Aug 9 run demonstrated `pytest 29 passed`, `idempotent True` after warmup, `extra --check` stable. Loop can run perpetually; to make it fully hands-off add `scripts/refine_loop.sh` wrapper that loops `audit → build → audit` until `ready`.

## 6. Status post-improvements (this version — iteration 2, ACR-I loop)

- **Done:** Primary pipeline (26w, 1610 sess, 34 merged), 5 dropdowns (default better, primary vs legacy), 4 groups (12 new charts: A1 histogram, A2 scatter, A3 velocity, B1 stacked harness, B2 neglect, B3 easy-win table, C1 heatmap, C3 hist, D1 story card/Diff), 3 summary layers (overall/group/week), 7-dim audit `11.7/14 READY`, idempotent second run True, `pytest 29`.
- **Iteration 2 assessments (2026-08-09):**
  - **M3 Git:** `repo ~/code --audit-only` 60 repos → `clean 44, pushable 4, no-remote 7, no-upstream 2, dirty-even 1 (custom-skills 2 uncommitted), pullable 1, detached 1` — `weekly-report-dashboard` is `no-upstream` on `001-weekly-report-dashboard` (3 flagged, 95% clean health). JSON: `~/git-audit-logs/git-audit-2026-08-09_172935.json`.
  - **M4 Vault:** 352 md, 165,981 lines, sample yaml coverage ~30% (e.g., “Embedding Model Intelligence Report” has yaml `tags: [embedding-models...]`, but “20 OpenClaw Prompts”, “skill-audit MVP spec” have none) — needs per-file `project:` inference and linking to 12 git projects.
  - **M1 Telemetry:** `raw-mirror` 1722 manifests, `daily_stats` 5720 sessions — provider split already used; full `token_usage` per model pending `telemetry_audit.py`.
- **Not yet:** M1/M5/M6 live token/cost/health ingestion into dashboard sections (stubbed, not yet rendered as dedicated charts), vault yaml population + `vault_project_map.json` overlay, heatmap real-daily backfill from blob parsing (currently `weekly/7` synthetic), `commits/files` backfill for Feb-Apr (currently `null`).
- **Debt:** Same as prior plus `git-audit-sync` output not yet rendered inside `#group-*` (only logged), vault linking not yet automated.

## 7. Validation gates (loop exit)

- `python3 scripts/build_dashboard.py --check` `34 weeks (primary:26) All assertions passed`
- `python3 -m pytest tests/ -q` `29 passed`
- Visual: `Data source Primary` shows 34 rows log-F1, `Legacy` shows 12, `2026-08-01` flagged, hover dims, `F1 log-scale`, `A1 histogram`, `B1 stacked`, `C1 heatmap` render, `Overall` narrative before data
- `python3 scripts/audit_viz.py` `Overall 11.7/14 READY` (next loop target 12.5)

---
*This README is the overarching project plan — self-updating. Each ACR-I loop rewrites §5/§6 with new scores and meta coverage.*
