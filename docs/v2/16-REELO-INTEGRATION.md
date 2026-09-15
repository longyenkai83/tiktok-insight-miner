# 16 — Direct Reelo Integration

Phase 9 implementation; pending architect review. Owner blueprint and shared map r6
(C4.1 PASS, D13–D17) authorize this scope from Insight ca09ae4d and Reelo 764f992d.

## Execution boundary

`send_packet` is a callable application service. CLI `send-content-packet` and the existing
packet-preview UI are adapters. The operator supplies the Reelo implementation workspace,
native executable, LOCALAPPDATA state directory and exact read-only creative asset files.
UI configuration comes from server-owned `REELO_CONFIG`, never a visitor-entered code path.
Default legacy commands and Content/Product extraction engines are unchanged.

The producer reloads verified insights, content tree, selection export and both authoritative
ledgers before dispatch. The Reelo consumer independently checks the pinned .1 contract,
source spans, hashes, language, selection lineage and permissions. It does not import the
producer extraction/governance pipeline. Its bounded Pydantic port has schema/fixture parity.
Only the trusted application callback establishes current authorization; a model cannot
supply an `authorized` flag. Local reads reduce but do not constitute a distributed transaction.

Before host launch, Reelo stores the entire canonical packet/context and an intake receipt
in local SQLite. Same packet and request ID reuses one generation, including concurrent
requests. A new generation requires an explicit parent. New packet revisions must extend
the known chain; old packets remain readable and cannot be dispatched after supersession.
Canonical packet_id, created_at, revision and A/B/C are not rebuilt by Reelo.

The configured native Claude 2.1.270 launches a copy of the existing `batch-content.js` with
validated context embedded after its mandatory first `meta` statement. Model args carry no
customer authority. There is no PATH fallback or new generic orchestration engine.
The controlled CLI profile disables hooks/plugins/MCP and allows Workflow/Read only. Creative
asset files are explicit and hashed. Reelo keeps its Writer, independent Critic, hook/title,
story, voice and format craft. V2 overrides only conflicting authority and uses all 8 title
criteria. Returned content is saved by code in distinct local versions, not written into
the operational brand vault by a creative worker.

Writer → Critic → at most one rewrite → Critic again. A/B context accompanies every call.
Unknown evidence IDs, missing results and null/failing slots cannot become a successful
draft. Critic is a fallible semantic check, not mathematical proof of customer truth.
Unsupported external assertions must be omitted/softened while retaining B or produce
BLOCKED_PENDING_RESEARCH. No research agent or automatic demand/validation promotion.

## State and handoff

Receipt contains ingestion_id, original packet_id/revision/hash and immutable context_hash.
ExecutionResult contains generation/parent, explicit status, critic state, validation issues,
host/task correlation, immutable draft versions and provenance. Human approval remains
PENDING; publication remains false. No automatic customer/content approval is created.

ACK and exit zero are not completion. Correlate the actual Workflow tool call, task_started
and terminal task_notification, then parse its returned artifact path. Never guess private
Claude journal paths or trust prose. Timeout/lost completion is UNKNOWN and transport retry
does not relaunch. Operator must reconcile the existing run; do not delete its row to retry.

Notion is a Main-owned draft handoff, not a Writer tool. The local outbox prepares a payload
using the fetched destination schema, rechecks currentness, claims once and records a URL
only after connector fetch verifies draft status and Source ID. Lost response requires
reconciliation rather than a second create. Human approval, Critic PASS, Notion DRAFT and
publication are separate. Existing database properties are used; no new database schema.

## Validation and limits

Offline suites cover contract/provenance rejection before launch, current-ledger reload,
concurrency, idempotency, revision forks, supersession, failure retention, bounded rewrite,
title/truth vetoes, terminal correlation and Notion draft outbox. The explicit live-host
fixture script is `tests/fixtures/phase9_host_e2e.py`: real native Workflow with controlled
creative responses and synthetic human decisions. This tests transport/control, not writing
quality or real customer approval. A separate controlled real-assets check remains a quality
review artifact; private assets/results are not committed.

SQLite is single-machine state outside cloud sync. No remote service, distributed lock,
unified web redesign, Source Router, ad/sales pipeline, social publication or main merge.
Web Business OS is the future target surface; Phase 9's core service is UI independent.


## C5.1 bounded quality closure

Owner authorizes only selected-direction preservation and creative timeout/quality work.
V2 now uses Zone B direction with no forced legacy TRUC_POOL axis. Legacy remains unchanged.
Read-only source discovery is bounded to operator-selected concrete assets, not an index-only
knowledge grant. Writer records usage/omissions; Critic independently verifies relevant sources.

Operator config optionally accepts effort_level=low/medium/high for one native host session.
Omitting it preserves inherited settings. It changes neither model nor customer truth guards,
permissions, packet/currentness, provenance or the 600-second default timeout. No global setting
is edited. Result host metadata records requested effort; it is not proof of actual thinking time.
Controlled tests compare inherited effort with an explicit medium session; all remain synthetic
customer truth plus real read-only creative assets, never fabricated real customer approvals.
No Notion write, publication, merge, Source Router or Unified Web is authorized by this patch.

The consumer draft gate accepts verified support refs plus validated contradiction counter_refs;
these are already source-span/hash checked by the canonical snapshot validator. No unknown IDs.
C5.1 acceptance remains BLOCKED: final native task stopped during rewrite, before second Critic.
First Critic findings cannot be ignored just because its verdict string says PASS. See doc 08.

## C5.2 — owner-authorized bounded follow-up

Q1 remains CLOSED/PASS. Only native lifecycle diagnosis, V2 Critic terminal semantics,
creator/external attribution and context/scope quality closure are authorized.
No merge, Source Router, Unified Web, legacy refactor or Phase 8 packet schema change.

V2 reviews now separate blocking_issues from informational notes and use PASS/REVISE.
Code retains the original review and projects PASS only when no blockers remain and all
strict truth/intent/limitations/external/creator/context/source checks plus eight title
criteria pass. Missing or malformed checks remain blockers. Notes alone do not require
rewrite; every factual or source-verification defect must remain a blocker. One rewrite
maximum, independent Critic again, and human approval still PENDING.

A stopped native task is not completed even when CLI exit/result says success. Consumer
records workflow_stopped_completion_unknown and retains UNKNOWN/no automatic retry.
Public stream lifecycle metadata and local native debug logs improve diagnosis, never
replace the task-correlated structured output contract. No undocumented API or timeout
increase is introduced. One controlled real-assets attempt is authorized before STOP/report.

## C5.3 — exact redundant output-read classification

Only the post-terminal Read of the exact correlated output_file may be non-blocking after
Python independently reads/validates the artifact and checks the entire receipt/context/
generation identity. Denied tool ID must match a unique Read call after the terminal event;
aggregate denial-report order alone is insufficient. Record an audit note, never widen the
host allowlist. Every other denial or validation failure remains blocking. Main/model Read
is unnecessary and not authoritative. Q1 and the creative/packet schemas are unchanged.
Owner authorizes one final controlled attempt, no retry or merge. Human quality review and
Architect integrity review remain separate from technical completion.

## C5.4 — deterministic stage boundary

Owner/Architect explicitly authorizes the minimum Phase 9 state machine in Reelo's local
integration layer. Each native 2.1.270 invocation runs one Writer/Critic/rewrite agent only.
Identical canonical A/B/C plus identity/lineage accompany every stage; only the required
previous draft and review accompany that stage. Creative prompts/craft and packet .1 stay intact.

Code validates and atomically persists each terminal output before choosing the next stage.
Completed stage records retain identity, parent stage/artifact hash, raw/normalized outputs and
host task/session correlation. Prior records are checked before continuation and final PASS.
Malformed/stopped/timeout/identity mismatch stops UNKNOWN without retry, preserving predecessors.
One rewrite maximum; final REVISE = CRITIC_FAILED. DRAFT_READY requires final Critic PASS and zero
blockers plus immutable context/identity/hash checks. Approval PENDING, published false, no Notion.

Timeout and budget are per stage, at most four invocations. No generic queue/resume system,
legacy refactor, Phase8 schema change, Source Router, Unified Web or merge. Existing synthetic
live-host fixture is adapted to return the controlled response for each bound stage; it is not
creative-quality evidence. C5.4 permits exactly one real-assets controlled acceptance after full
suites pass; its local REPORT-C5.4.md is the sole owner-mediated review handoff.
