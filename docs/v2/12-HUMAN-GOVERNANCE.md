# 12 — HUMAN GOVERNANCE

## Current authority — Phase 8 (DEC-062–066)

Current Phase = Phase 8 — Content Intelligence Packet
Status = IMPLEMENTED — PENDING ARCHITECT REVIEW
Core Customer Intelligence MVP = ACCEPTED
Content Route = ACCEPTED
Product Discovery Route = ACCEPTED
Direct Reelo Integration = NOT STARTED
Next Phase = DO NOT START

Owner Phase 8 request accepts Content/Product routes and authorizes only the typed packet
from `78f47def5614723a1cb973d9c5ae6a5f9d3ca7a5` on `v2-phase-8-content-packet`.
Earlier packet prohibitions/pending route acceptance below are historical, superseded by
this explicit request. Evidence, Strategyzer, B2C and human-governance rules remain binding.
Read docs 00–15 and [contracts/README](../../contracts/README.md), including
[15-CONTENT-INTELLIGENCE-PACKET.md](15-CONTENT-INTELLIGENCE-PACKET.md).
No Reelo repository changes, Phase 9, Writer generation, Drive upload or main merge.

Packet requires BOTH current corpus-scoped human insight approval and current human angle selection. Neither means market/purchase validation. Snapshot checks cannot infer current approval; only current authoritative ledgers can authorize a new handoff.

## Earlier phase documentation (historical gates)

## Authority and scope

AGENTS EXECUTE. EVIDENCE INFORMS. HUMAN APPROVES CONSEQUENTIAL DECISIONS.

Phase 5 is the first explicit Human Governor gate. A human decides whether a machine
candidate reasonably represents the cited evidence corpus and stated scope. No LLM,
support-count threshold, likes, scheduler or agent may approve on the human's behalf.
Preparing a queue and applying recorded decisions do not make a decision.

`human_verified=true` means only corpus-scoped semantic approval. It does not prove
population statistics, causality, market demand, product fit or purchase behavior.
`market_validated=false`, `purchase_validated=false`; DERIVED remains DERIVED.

Current Phase = Phase 5 — Human Governor

Status = IMPLEMENTED — PENDING ARCHITECT REVIEW

Core Customer Intelligence MVP = NOT YET ACCEPTED (await architect review)

Next Phase = DO NOT START. Do not start Phase 6.

## Decisions and priority

| Human decision | Result |
|---|---|
| approved | Accept original candidate wording; origin machine_approved |
| edited_and_approved | Accept explicitly edited wording; origin human_edited |
| rejected | No current Verified Insight; preserve history |
| deferred | No current Verified Insight; await further review/evidence |

`verified` is the resulting artifact status, never a review action. Every action needs
reviewer_id, explicit human_attested=true, rationale, exact candidate ID/hash and unique
request_id. Same request ID and identical payload on the same analysis is an idempotent
retry; reuse for different content fails. No action is preselected in the UI.

PriorityDecision: priority_status = unassessed / monitor / priority_need. Optional
important, urgent, frequent, expensive, emotional_intensity = high / medium / low / unknown.
All default unknown. assessment_origin=human_assessment; optional note is not customer truth.
This is the owner's accepted Customer Dossier priority framework, applied as a V2 human
decision, not a measured Strategyzer score or an AI claim. No forced dimension completion.
Only an approved insight can carry non-default priority assessments. Rejection/defer
clears the current assessment; prior priority remains in the previous event.

Display support comment count, unique authors/source count with unknown coverage,
known engagement, context variants, contradictions and wording variations beside the
decision. Deterministic sorting is never labeled market importance or turned into a score.

## Immutable evidence and edit integrity

Original Phase 4 candidate, original machine review, human event, and verified projection
are separate. Human editing changes statement text only. Evidence refs/hashes, scope,
profile links, support metrics, variations, contradictions and limitations are copied
unchanged from the validated candidate. Different evidence needs a new analysis/review.

Human edits pass deterministic numeric/generalization, quote, solution/content and
demographic-scope guards reused from Phase 4. No AI review of the edited meaning; the
renamed-label/shallow filter is not a human veto. Broader strategic ideas belong in
rationale/note, not Verified Insight truth. Guards are conservative EN/VI heuristics,
may over-block legitimate numeric wording and miss paraphrases; no entailment guarantee.

Verified verification.machine_review_passed describes the ORIGINAL candidate only.
machine_review_scope=source_candidate_only makes that explicit, including human edits.
The human-approved text has statement_origin, exact event and rationale; it is not
misrepresented as having passed a fresh machine review. Phase 4 part offsets stay in
the original candidate snapshot; they are not falsely reused for edited text. Verified
statements retain whole-statement pattern/evidence refs, not new AI per-part assertions.

## JSON contracts and revision rules

- Input remains v2.insights.2; Phase 1–4 schemas/behavior are unchanged.
- `insight_reviews.json`, schema v2.insight-reviews.1: ordered immutable full input
  snapshots plus append-only ReviewEvents. Last snapshot is the current analysis.
- ReviewEvent: review_event_id, sequence, previous_event_id, source_schema_version,
  source_insights_hash, action, reviewed_at (timezone-aware), original_statement,
  approved_statement (null for reject/defer). action contains the exact human decision,
  reviewer, rationale and priority. IDs hash canonical event content and previous event ID.
- `verified_insights.json`, schema v2.verified-insights.1: input_reviews_hash, embedded
  review_history, verified_insights. The full provenance envelope is the boundary contract.
- VerifiedInsight: stable event-derived ID, source_candidate_id/hash, source_insights_hash,
  revision, supersedes, DERIVED statement/origin, unchanged evidence/profile/scope/support,
  HumanReview summary, HumanVerification, human PriorityDecision and status=verified.

Latest decision for a candidate in the CURRENT snapshot controls the projection. Reject
or defer after approval removes it from current verified output; the earlier approval
event remains auditable. Reapproval produces a new revision/supersedes pointer. Material
candidate changes create a new candidate ID under Phase 4 identity rules; do not infer
that different IDs mean the same customer insight or auto-link semantic supersession.

Identical input preparation preserves decisions. Any input envelope hash change, even
generated_at alone, creates a fresh pending analysis revision conservatively; no silent
approval inheritance. Historical snapshots cannot become active again by re-uploading.
No full living Customer Profile merge engine is implemented. Future profile updates may
PROPOSE add / merge / supersede / archive; human approval is required for supersession.

## Storage, concurrency and downstream gate

JSON is authoritative; Markdown is only a view. Ledger mutations hold an OS file lock,
validate previous history, preserve old snapshot/event prefixes, flush and fsync a
same-directory temporary file, then os.replace it. UI submissions check expected history
hash to avoid lost updates. Busy/stale writes fail visibly. OS releases locks on process
exit; stable .lock files may remain and are not stale-lock ownership markers.

Verified JSON is a deterministic rebuildable projection. Its write is atomic separately
from the ledger, not a two-file transaction. After interruption or a new decision, an old
export may exist: rebuild with apply-insight-review. UI does not offer stale exports as
current. Existing unrelated files cannot be overwritten by apply. File durability follows
local filesystem/volume guarantees; this is not a distributed database or immutable archive.

`require_verified(artifact, current_reviews)` revalidates the full verified envelope and
requires its ledger hash to equal the CURRENT authoritative ledger loaded by the consumer.
It rejects Phase 4 candidates, bare booleans/records, forged evidence and stale/revoked
projections. Do not trust the packet's embedded historical ledger as the current ledger.
Only this gated contract may later enter Content/Product/Profile/Business OS routes.
No downstream generator, Reelo integration or content selection implementation here.

Review labels are configurable; web reuses the existing user label after the app's
existing password gate. That label is self-declared, not an independently authenticated
individual identity. CLI requires --reviewer and --confirm-human. Never store more PII
for this patch or use reviewer identity as evidence. Trusted humans/local access are the
MVP boundary: JSON hashes detect inconsistent edits, not malicious rewriting by someone
with filesystem access. RBAC, signatures and tamper-proof external audit remain future work.
Agents must not fabricate human_attested=true or submit customer decisions without an
explicit corresponding human instruction. Synthetic test decisions are not customer approvals.

## UI and CLI

Existing webapp: enter current user label, enable sidebar **V2 — Human Review** (off by
default). Choose a review workspace under output/v2-human-review, upload v2.insights.2
and explicitly prepare the queue. Select Pending/Approved/Rejected/Deferred/Priority Needs;
sort by support/source/contradiction count. One expand **TẠI SAO MÁY NÓI VẬY?** shows exact
quotes, complete source text and refs. All evidence, context, counter-evidence, variations,
machine review and limitations remain on the screen. Show up to five representative
distinct comments; if fewer than three exist, show actual available evidence only.

Choose Approve/Edit + Approve/Reject/Defer, enter rationale, optional human priority,
attest the decision and submit. No approval on upload, navigation or filter change.
Rebuild/download verified JSON with the explicit export button; history JSON also downloads.

```sh
tim prepare-insight-review --insights insights.json -o insight_reviews.json
# Returns candidate IDs/hashes and current history hash; no approval.
tim record-insight-review --reviews insight_reviews.json --candidate-id <ID> \
  --candidate-hash <HASH> --request-id <UNIQUE-ACTION-ID> --reviewer <HUMAN-LABEL> \
  --confirm-human --decision approved --rationale "Reason for this corpus-scoped decision"
tim apply-insight-review --reviews insight_reviews.json -o verified_insights.json
```

Record supports --statement only with edited_and_approved; --priority and optional
--important/--urgent/--frequent/--expensive/--emotional-intensity. CLI/API never calls AI.
Legacy run/web pipeline remains default. Human Review does not consume scrape/AI run quota.

## MVP checkpoint

Source Evidence → Signal → Context → Pattern → Insight Candidate → Human Governor
→ Verified Insight / human Priority Need is the core Customer Intelligence MVP.
When Phase 5 passes architect review, this is the first usable Business OS sensing module.
It is **NOT YET ACCEPTED**. Downstream Content/Product routes are separate subsequent phases.
No Phase 6 authorization is implied by green tests, a prepared queue or a push.
