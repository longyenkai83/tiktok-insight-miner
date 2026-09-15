# 14 — PRODUCT DISCOVERY ROUTE

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

Product Discovery Route is ACCEPTED per Phase 8 request. Phase 7 runtime remains unchanged; its proposed products/assumptions/plans must not enter Content Packet. This acceptance does not manufacture real sample Priority Needs or validate product demand.

## Earlier phase documentation (historical gates)

Current Phase = Phase 7 — Product Discovery Route
Status = IMPLEMENTED — PENDING ARCHITECT REVIEW
Core Customer Intelligence MVP = ACCEPTED
Content Route = IMPLEMENTED
Product Discovery Route = PENDING ARCHITECT REVIEW
Next Phase = DO NOT START

## Authority and meaning

Owner Phase 7 request authorizes this separate route from
`4b11e45c55a33030d030b14cfd06ce10f285730f`, branch `v2-phase-7-product-discovery`.
No main merge, Content Packet, Reelo, external experiments or Customer Profile updates.

Human-Verified Insight + human Priority Need → Product Opportunity → Possible Value Map
→ Assumptions → Experiment Plan → Human Decision To Test.

Product means a way to help customer progress: tool, worksheet, checklist, template,
calculator, diagnostic, scorecard, guide, report, lead magnet, course/workshop, service,
feature, automation, free resource, paid product or commercial offer. `other` and unknown/null
type are valid; commercial model defaults undecided, never paid. Competing alternatives
are supported; no opportunity score or automatic investment decision.

## Strategyzer trace and epistemic boundary

**SOURCE PRINCIPLE:** Customer Profile = Jobs / Pains / Gains + Context, independent of
our solution; AI assists but cannot invent customer demand. Customer speech is not purchase
proof. Value Proposition Canvas distinguishes customer side from Products & Services,
Pain Relievers and Gain Creators on the solution side.

**V2 DECISION:** Customer Profile → Value Map → possible Fit, then Value Map → Assumptions
→ Experiments → Evidence → Decision. Product Opportunity is the V2 product-research object,
not a claimed Strategyzer source term. Phase 7 implements proposals/plans and human choice
only, not collected experiment evidence, actual fit or validated product.

**DERIVED IMPLEMENTATION RULE:** every product preserves immutable Priority Need, scope,
profile links, evidence/quotes, contradictions, variants, limitations and source hashes.
Value Map fit links are PROPOSED relationships, not measured causal effectiveness.
Assumptions are HYPOTHESIS; opportunity, map, progress proposal and plan are PROPOSED.
Customer truth remains DERIVED with exact upstream OBSERVED/DERIVED source references.
Explore means choose for testing, never approve a product as validated.

## Input gate and customer progress

Require the full `v2.verified-insights.1` envelope against the CURRENT authoritative Phase 5
ledger and `priority_status=priority_need`. Machine candidates, flags without provenance,
stale/rejected/deferred/unassessed/monitor insights cannot generate. A mixed verified envelope
may contain other priorities, but only Priority Needs enter generation. If none exist, fail
before model calls. Priority removal or evidence changes invalidate downstream use.

Current struggle references an existing pains/behavior span; job references jobs. Missing
either means no candidate can pass the progress gate; report the issue rather than invent it.
Optional need moment references context/behavior.trigger. Optional supported Gain references
gains only. Desired progress is always explicitly PROPOSED, even with a separate supporting
Gain, so a generated future is never customer-stated. Together these fields provide an optional
Product Value Scene: grounded Need Moment → grounded Current Struggle → Proposed Future.

## Types and closed transport

`product_models.py` defines a combined `v2.product-discovery.1` JSON envelope with separable:

| Type | Version | Main fields |
|---|---|---|
| Product Opportunity | v2.product-opportunities.1 | opportunity_statement/type/mechanism, delivery/commercial model, customer_progress, immutable priority_need, refs, metadata, validation |
| Possible Value Map | v2.value-maps.1 | products_services, pain_relievers, gain_creators, parent opportunity ID |
| Assumption | v2.product-assumptions.1 | risk_category, observable_behavior, offered_value, observation_method, subject_scope_ref, evidence_strength, importance |
| Experiment Plan | v2.experiment-plans.1 | assumption/opportunity IDs, current level, nested proposed plan with target/type/procedure/measurement/conditions/evidence_to_collect/optional threshold |
| Human selection | v2.selected-product-opportunities.1 | current decision history hash, full history, selected opportunities for testing |

Model transport proposes a complete alternative bundle per Priority Need. It supplies closed
verified insight/evidence IDs plus local service/fit/assumption/experiment IDs. Code constructs
global IDs, exact references, hashes, source counts and generation metadata. Every nested
object resolves through its parent to the same immutable evidence. Unknown/foreign/duplicate
IDs and invented evidence fields are rejected. Complete bundle validation is atomic per
candidate: an invalid map/assumption/plan rejects that alternative, without partial orphan output.

Every service has one or more existing Jobs/Pains/Gains evidence targets. A Pain Reliever
links an existing service to an exact pains reference targeted by that service; Gain Creator
does the same for gains. No orphan services/fit items. Gain Creators may be empty. A source
pain or job cannot be relabeled a Gain. Fit objects contain PROPOSED mechanism and code-copied
target evidence, giving Product/Service → Reliever/Creator → exact Pain/Gain traceability.

Counts 1–20 are requests, not quotas or quality thresholds. Dedup compares normalized
mechanism text within a need; renaming the opportunity or changing type does not suffice.
It is near-text dedup, not proof of semantic diversity. Raw transports and issue codes remain
local in history; rejected transports are untrusted proposals, not customer truth.

## Assumptions and evidence ladder

Choose relevant DESIRABILITY / FEASIBILITY / VIABILITY / SURVIVABILITY categories; no forced
completion. Each assumption records one observable behavior/outcome, offered value and
observation method. Subject/context resolve from the parent Priority Need rather than an
invented segment. Compound conjunctions and very short/non-specific fields are rejected;
human review must still assess actual precision and testability. No automatic riskiest flag.
Importance defaults unknown; human may select an assumption to test first and assess its
importance and `riskiest_assumption=true` in the decision event without changing the original
assumption. Neither flag is accepted in AI transport; the riskiest marker requires an explicitly
chosen assumption and human Explore.

Owner-specified V2 operational evidence ladder (not a claim of a universal source scoring API):

| Level | Evidence |
|---|---|
| 0 | Idea only |
| 1 | Customer speech |
| 2 | Speech plus artifact/prototype reaction |
| 3 | Light behavior |
| 4 | Commitment/deposit/meaningful action |
| 5 | Real market behavior |

Current source schema supports customer speech: customer-need level is fixed at 1 regardless
of comment count, even for speech describing payment. Proposed-solution assumption strength
and experiment current level are 0: nobody has tested the specific proposed solution yet.
These measure different claims and are shown separately. No automatic promotion from breadth,
human approval, generated plans or human Explore. All demand/market/purchase/product validation
flags are fixed false. Higher evidence collection and validation need a later phase.

## Experiment plans only

Each assumption needs a linked plan. Target must match interview=1, prototype_reaction=2,
behavior_test=3, commitment_test=4, market_test=5. A target is a proposed evidence objective,
not an achieved level. Plans targeting above 2 display an escalation caution; prefer cheap
speech/prototype learning first. No full-product build, external publication, recruiting,
payments, experiments or investment is executed.

Qualitative success/failure conditions are preferred. Numeric thresholds exist only in
`threshold={label:PROPOSED_TEST_THRESHOLD, metric, value, unit, operator}`; they are proposed
test design, never market statistics or an approved success criterion. Other numeric prose,
fake quotes, demand certainty, fabricated research, demographic leakage, content prose and
unknown extra fields are rejected/flagged by deterministic guards. These are conservative
EN/VI checks, not semantic proof; incidental unsupported claims still need architect/human review.

## Human decisions, revisions and durability

`v2.product-decisions.1` is authoritative JSON with immutable full tree revisions and
hash-linked append-only events. Actions explore/reject/defer require reviewer label,
attestation, rationale, exact tree/opportunity hash and unique request ID. Explore may
choose `assumption_to_test_first` belonging to that opportunity and human importance.
Reject/defer cannot carry that test choice. No action is preselected or generated by AI.

Only latest Explore on the current tree appears in selected-product projection. Reject/defer
revokes selection; changed tree requires fresh human choice conservatively, even if the
last generation only added issues. Original opportunities/maps/assumptions/events remain.
Identical requests are idempotent; request reuse with different data fails. Historical trees
cannot reactivate. Consumers validate current tree, current product ledger AND current
Phase 5 ledger; embedded historical state alone is insufficient.

Reuse local OS file locks, optimistic hashes, fsync and atomic replacement from Phase 5.
Tree and ledger are separate atomic files, not a distributed transaction. If interrupted
between saves, prepare again from current tree; old selected export fails the current-tree
gate. JSON hashes detect inconsistent edits, not malicious rewrite by a trusted filesystem
user. Reviewer label is self-declared; this patch does not implement authentication/RBAC.

## UI and CLI

Enable sidebar **V2 — Product Discovery** after the existing app user/password gate. Choose
Human Review workspace and Product run. Inspect Priority Need/profile/context → generate
alternative products → Possible Value Map → assumptions/evidence levels → plans → explicit
Explore/Reject/Defer. Expand **TẠI SAO MÁY ĐỀ XUẤT SẢN PHẨM NÀY?** for Priority Need →
Verified Insight → Pattern → Signal → source snapshots, exact quotes and contradictions.
Original source evidence is one click away; no separate analysis workflow. History persists
across sessions. Selected output is for testing, not a Content Packet or validated product.

```text
tim build-product-opportunities --verified-insights verified_insights.json --reviews insight_reviews.json --project-id demo --run-id research --count 3 -o product_discovery.json
tim prepare-product-selection --tree product_discovery.json --reviews insight_reviews.json --decisions product_decisions.json
tim select-product-opportunity --tree product_discovery.json --reviews insight_reviews.json --decisions product_decisions.json --tree-hash HASH --opportunity-id ID --opportunity-hash HASH --request-id UNIQUE --reviewer OWNER --confirm-human --decision explore --rationale "Choose for testing"
tim export-product-selection --tree product_discovery.json --reviews insight_reviews.json --decisions product_decisions.json -o selected_product_opportunities.json
```

Optional selection `--assumption ID --importance high|medium|low|unknown --riskiest-assumption`;
generation `--model`.
Model precedence: explicit option, PRODUCT_DISCOVERY_MODEL, ANTHROPIC_MODEL, existing default.
API input/response limits fail visibly without truncation; no automatic retries or secret
exception bodies in artifacts. No customer data committed. Existing Content Route and legacy
pipeline remain unchanged; no package rename, new adapter, scheduler or dependency.

## Review status and limits

Offline tests use explicit synthetic human approvals/Priority Needs. Real generation is
SKIPPED unless an actual owner-approved Priority Need exists locally. No approvals fabricated.
Full tests validate structure/workflows, not live model quality or proven demand. Large
histories duplicate/replay provenance and may be costly; lexical guards can over-reject and
miss subtle paraphrases. No future phase is authorized by tests, commit or push.
