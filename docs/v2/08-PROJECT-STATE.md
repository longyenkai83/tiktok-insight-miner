# 08 — PROJECT STATE

Current Phase = Phase 5 — Human Governor

Status = IMPLEMENTED — PENDING ARCHITECT REVIEW

Core Customer Intelligence MVP = NOT YET ACCEPTED (await architect review)

Next Phase = DO NOT START

Do not start Phase 6. Do not merge main.

## Authorized implementation

Base v2-phase-4-evidence-insight@66b387e4af0e79e0f4fc4e77a766eaf55a228b40.
Branch v2-phase-5-human-governor; DEC-048–052. Read docs 00–12, including new
[12-HUMAN-GOVERNANCE.md](12-HUMAN-GOVERNANCE.md). Earlier phase restrictions are historical
unless reaffirmed; evidence/Strategyzer/B2C/Business OS principles remain in force.

- Added platform-neutral governance models/engine/store/CLI/UI in the existing package.
- v2.insights.2 → durable v2.insight-reviews.1 → v2.verified-insights.1. Input candidates
  and original machine reviews are immutable; approved/edited_and_approved/rejected/deferred
  events are append-only with reviewer/rationale/time/hash chain. No automatic approvals.
- Verified projection uses only latest explicit approvals in current analysis snapshot.
  New upstream hash means fresh pending review; identical prepare/apply/request retries
  idempotent; later rejection/defer revokes current eligibility; revisions retain supersedes.
- Human edits preserve evidence/scope/counters/limitations; deterministic integrity guards,
  no AI review/veto of human semantics. DERIVED unchanged; market/purchase false. Machine
  review flag explicitly scoped to original candidate, not falsely to edited text.
- Human Priority Need and optional dimensions, unknown valid; counts/engagement displayed
  separately and never auto-scored. Downstream requires full verified artifact plus current
  authoritative ledger, not a standalone flag. Future profile merge contract only.
- JSON writes use local OS locking, optimistic history hash, append-only prefix checks,
  fsync and atomic replacement. Verified projection separately rebuildable; stale export fails gate.
- Existing webapp gets opt-in sidebar Human Review, filters, evidence expand, all four human
  actions and optional priority. Existing user label/password gate reused, no new identity claims.
- Independent CLI: prepare-insight-review, record-insight-review, apply-insight-review.
- No Content/Product generation, Reelo integration, living profile merge, router/scheduler/
  source adapters/state-store, multi-tenancy, dependency change or package rename.
- Default legacy runtime behavior changed: **NO**. New governance runs only by explicit CLI/UI action.

## Tests

`python -m pytest tests -q -p no:cacheprovider` → **365 passed in 5.29s**.
Python 3.13.15 / pytest 8.4.2. **48 new offline cases**, including four Streamlit AppTest
human-action flows and fresh-session durable-state checks; all 317 previous tests green.
No live model/API calls. Tests cover no auto-approval, all decisions, edited integrity,
immutable evidence, strict truth/verification flags, priority, append-only/retry/revision,
changed source/statement, downstream revocation/staleness, atomic interruption, lock conflict,
JSON replay, CLI, UI helpers/filters and safe review workspace paths.

## Real-data preparation — no customer decisions

Source: Phase 4.1 local insights.json, the same 50 comments / 85 patterns / 12 machine candidates.
Prepared a local queue and human preview only; **no owner decisions made by the agent**.

| Check | Result |
|---|---:|
| Pending review | 12 |
| Human review events | 0 |
| Verified Insights | 0 |
| Priority Needs | 0 |
| Candidates with representative exact evidence | 12 |
| Candidates with 3–5 representative distinct comments | 10 |
| Candidates with fewer than 3 comments | 2 |
| Candidates with possible contradictions | 8 |
| Counter-evidence links summed across candidates | 83 |
| Candidates with cited context | 12 |
| Context variants summed across candidates | 71 |

The link/variant sums can repeat the same underlying evidence across candidates; they are
not counts of independent people or verified contradictions. Two narrow candidates show
only available sources. Phase 4 semantic limitations remain visible for the human to judge.

Local-only preview:
`D:/Tuan-CoWork/TUAN-insight-miner/output/v2-phase5-worktree/output/v2-human-review/phase5-real-sample/phase5-human-review-preview.md`

Sibling files: insight_reviews.json, empty verified_insights.json, metrics.json and OS lock
files. All ignored, no private sample committed. In the Phase 5 webapp select Human Review,
workspace phase5-real-sample to inspect this queue; do not auto-approve.

## MVP and known limits

Source Evidence → Signal → Context → Pattern → Insight Candidate → Human Governor
→ Verified Insight / human Priority Need is implemented, **NOT YET ACCEPTED** by architect.
Downstream Content/Product routes are separate subsequent phases.

- Current user/reviewer IDs are self-declared labels behind the existing optional shared
  password gate, not individually authenticated signatures. Human attestation is explicit;
  trusted local operators must not impersonate a reviewer. No RBAC/auth overhaul in this scope.
- Hash chains/replay detect inconsistent edits but cannot stop deliberate complete rewriting
  by someone with filesystem access. Local file locks are not distributed-store guarantees.
- Ledger commit and verified export are separate atomic files. Interrupted/stale projection
  must rebuild; downstream needs the trusted current ledger to detect revocation.
- Any source envelope hash change conservatively resets pending state, even metadata-only
  timestamps. Full immutable snapshots/history can grow; no pruning/scaling engine here.
- Human edit guards use conservative EN/VI lexical checks and may over-block or miss wording.
  No claim of complete semantic proof. Original Phase 4 overclaim/context/causality/shallow
  misses remain for the human; approval is only within cited corpus, not market validation.
- New candidate IDs are not semantically auto-linked for supersession; full profile
  add/merge/supersede/archive remains future work. No technical blocker to branch review.

STOP. Next Phase = DO NOT START.
