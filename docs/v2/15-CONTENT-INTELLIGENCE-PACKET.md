# 15 — CONTENT INTELLIGENCE PACKET

Current Phase = Phase 8 — Content Intelligence Packet
Status = IMPLEMENTED — PENDING ARCHITECT REVIEW
Core Customer Intelligence MVP = ACCEPTED
Content Route = ACCEPTED
Product Discovery Route = ACCEPTED
Direct Reelo Integration = NOT STARTED
Next Phase = DO NOT START

Owner Phase 8 request authorizes this contract from
`78f47def5614723a1cb973d9c5ae6a5f9d3ca7a5` on `v2-phase-8-content-packet`.
It explicitly accepts Phase 7 Product Discovery and Content Route. No Reelo repository
change, Phase 9, Drive upload, Writer output, experiment execution or main merge.

## Contract and boundaries

Human-Verified Insight → Human-Selected Angle → typed immutable packet. Canonical
`v2.content-intelligence-packet.1`, with machine-readable
[JSON Schema](../../contracts/content-intelligence-packet.schema.json) and
[consumer/versioning rules](../../contracts/README.md). JSON is authoritative; Markdown
is view-only. This is the first production Agent-to-Agent typed contract in the Business
OS architecture, pending architect review; actual cross-repo consumption has not started.
Future specialist handoffs follow typed/versioned/provenance-aware/state-aware/auditable
contracts, with Human Governor at consequential decisions.

| Zone | Meaning | Payload |
|---|---|---|
| A — Customer Truth | Immutable, human-verified within cited corpus | Exact VerifiedInsight object, including Jobs/Pains/Gains/behavior links, B2C scope/audience/context/situation/life_or_business_stage/user_buyer_distinction, evidence summary/refs, variations, contradictions, limitations; literal language bank and relevant complete source snapshots |
| B — Selected Strategy | Human-selected but PROPOSED | Separate opportunity/topic/angle projections, core argument, before/after belief, opening, customer value, Value Scene and optional objective |
| C — Creative Execution | Writer-owned presentation, not customer truth | Explicit may/may-not contract; status not_generated, no final prose in Phase 8 |

The optional user/buyer distinction remains B2C only. Missing audience or Gain stays missing;
packet building performs no inference, extraction, classification or re-mining. Verified
statement remains DERIVED; approval does not make market/purchase flags true. Product
Discovery objects are not accepted in this content contract, even for project_goal=BOTH.

## Hard gates

Builder requires full v2.verified-insights.1, current ContentTree, full
v2.selected-content-angles.1, CURRENT governance ledger and CURRENT selection ledger.
Reuse Phase 5 require_verified, Phase 6 checked_tree/require_selected; additionally check
the supplied tree matches the latest ledger tree and verified artifact. Resolve selected
angle → Topic → Content Opportunity → same Verified Insight. Unselected/rejected/deferred,
machine-only, missing/stale/evidence-mismatched inputs fail before packet creation.
No implicit selection or approval is written by this feature.

Current validation rebuilds the expected packet fields from current inputs and compares
all Zone A/B data, selection and lineage. Save revalidates, CLI reloads inputs after build,
UI revalidates before export. Current data are local trusted files, not packet-supplied
historical authority. Source/selection changes make old packets historical, not silently
updated. Cross-file reads are not distributed transactions; future intake must recheck
currentness or have an explicitly approved immutable-snapshot acceptance policy.

## Portable evidence and language

Copy the approved VerifiedInsight unchanged. Include only source snapshots referenced by
that insight's evidence, context, variations or counter-evidence. Preserve full source text
for context, hashes and quote/span verification; exclude unrelated corpus/history/alternatives.
Lineage contains verified/candidate/pattern/comment IDs, source hashes, opportunity/topic/
angle IDs and hashes, verified/tree/selection-export and authoritative-ledger hashes.
Unknown source route context stays empty; platform values come only from source snapshots.
No required relative paths, report.md, brief.md, niche config, Drive or local Markdown.

Language bank groups only exact upstream language.exact_phrases/emotional_wording/
repeated_expressions refs, preserving literal text and source span/hash. Repeated expressions
retain Phase 1 within-comment semantics; no invented corpus frequency. Up to five distinct
support-source representative quotes are shown; all evidence/counters remain in Zone A.
No minimum quote quota and no generation of missing phrases.

Value Scene preserves Phase 6 tagged types: source_wording means grounded, proposed_framing
means PROPOSED. Grounded need moment requires context/behavior.trigger; current struggle
requires pains/behavior; grounded desired future requires gains. Every grounded ref must
belong to this insight and exact text/truth must match. Proposed future never becomes an
observed Gain. Null components remain null.

## External evidence and Writer permissions

Code walks all selected ProposedText fields and records each pending external-evidence
requirement with exact proposed text and field path, purpose and required_before_publish.
Phase 6 flags all proposed prose conservatively, so creative framing may also be flagged.
This preserves pending checks without inventing external research or certifying the claim.
Packet builder does not fetch research or generate additional customer truth.

Writer MAY create hook/title/structure, analogies/metaphors, clearly labeled illustrative
examples, storytelling format, voice adaptation, clarity and CTA. Writer MAY NOT change
Verified Insight/profile/scope/evidence/quotes/contradictions/limitations, invent statistics/
real customers/cases/demographics/research, upgrade evidence or claim market/purchase
validation. Constant permission fields appear in runtime and JSON Schema. Future Writer
output validation is Phase 9 work, not implemented here. Brand/offer facts are not invented
or imported from local config; unsupported external facts remain requirements.

## Validation, revisions and trust

Standalone validate-content-packet checks **snapshot** integrity and reports current
authorization NOT_CHECKED_OFFLINE. JSON Schema alone checks structure/constants, not hashes,
source spans or revocation. Provide all five current inputs to check current authorization.
Old packets remain valid historical snapshots even after revocation; never label offline
PASS as current approval. No unsigned packet can authenticate a malicious complete rewrite;
hashes are audit/integrity links, not signatures. Trust/currentness integration is future work.

packet_revision starts at 1. Explicit previous packet from same project/run enables
supersedes_packet_id and next revision. Unchanged content/current lineage/goal returns
the previous object unchanged. Changed truth/angle/state creates new ID and revision.
packet_id hashes canonical complete packet fields except itself, including time/revision.
Old files are immutable; save to a separate path, refuse overwrite with different data.
Atomic JSON replacement and local OS locks reuse governance storage. No global mutable
latest-packet registry; retain ancestor files and validate_revision to audit the chain.

## CLI and UI

```text
tim build-content-packet --verified-insights verified_insights.json --content-tree content_tree.json --selection selected_content_angles.json --reviews insight_reviews.json --selection-ledger content_selections.json --angle-id ANGLE_ID -o content_intelligence_packet.json
tim validate-content-packet content_intelligence_packet.json
tim validate-content-packet content_intelligence_packet.json --verified-insights verified_insights.json --content-tree content_tree.json --selection selected_content_angles.json --reviews insight_reviews.json --selection-ledger content_selections.json --preview
```

Build supports --project-goal CONTENT|BOTH and --previous packet.json. Require all five
current inputs together when checking current authorization. No AI/API calls.

Sidebar **V2 — Packet Preview** (off by default): select Human Review workspace/Content run,
select an already selected angle → Build Packet → validate → PASS/FAIL → inspect Zone A/B/C
and external evidence requirements → local JSON export. Optional previous packet creates
revision. Files live in output/v2-content-packets/workspace/run, ignored by Git. FAIL hides
export. Markdown preview answers “REELO SẼ NHẬN ĐƯỢC GÌ?” and is never parser authority.

## Compatibility and verification

Read docs 00–15 plus contracts/README before architecture/product work. Contract release
1.0.0: PATCH clarification/non-wire metadata; MINOR optional capability with a new published
schema version; MAJOR breaking semantics with migration/review. Strict consumers must
explicitly support a new version. Never silently repurpose .1 fields or truth semantics.

Synthetic fixture under contracts/fixtures contains no real owner approvals/customer data.
Tests cover provenance, currentness, zones, immutable revisions, JSON Schema, CLI and UI.
Actual real-data generation is SKIPPED without a real approved insight AND selected angle.
Existing Content/Product engines and defaults remain unchanged. No Reelo repo modifications.
