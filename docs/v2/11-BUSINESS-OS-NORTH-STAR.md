# 11 — BUSINESS OS NORTH STAR

## Current authority — Phase 6 (DEC-053–056)

Current Phase = Phase 6 — Content Route
Status = IMPLEMENTED — PENDING ARCHITECT REVIEW
Core Customer Intelligence MVP = ACCEPTED
Next Phase = DO NOT START

The owner's Phase 6 request authorizes Content Opportunity → Topic → Angle → Human
Angle Selection from base `7972a849b27fed00308bcfd2870bf8a24c2be216` on
`v2-phase-6-content-route`. Read all fourteen documents 00–13, including
[13-CONTENT-ROUTE.md](13-CONTENT-ROUTE.md). It supersedes earlier Phase 6 prohibitions
and MVP acceptance status below. Earlier phase sections are historical scope records;
their evidence, B2C, Strategyzer and human-governance principles remain binding.
No Product Discovery, final writing, Reelo integration, next phase or main merge.

The core sensing MVP is now ACCEPTED by explicit owner authorization. The Content Route is implemented pending review, not an autonomous Business OS router. Product Route, new adapters, scheduler and Reelo remain unimplemented.

## Earlier phase documentation (historical gates)

## Phase 5 — first explicit Human Governor implemented, pending acceptance

AGENTS EXECUTE. EVIDENCE INFORMS. HUMAN APPROVES CONSEQUENTIAL DECISIONS.
The current implementation ends at human-approved, corpus-scoped Verified Insight / human
Priority Need. When Phase 5 passes architect review, the core Customer Intelligence MVP is
the first usable sensing module of Business OS. It is currently NOT YET ACCEPTED.

Source Router and Downstream Router below remain future contracts. Their downstream branches
must use the current-human-review gate; approval is not market/purchase/product validation.
Future profile updates may PROPOSE add/merge/supersede/archive, with human supersession approval.
No living-profile merge, downstream generation, Reelo integration, source scheduler or new
adapter here. Governance authority, storage and trust boundary: [12](12-HUMAN-GOVERNANCE.md).
Read docs 00–12. Do not start Phase 6.

## Phase 4.1 — Source Router and Downstream Router (ACCEPTED future architecture)

Customer Intelligence is the FIRST sensing layer of Business OS. Agents execute.
Evidence informs. Human approves consequential decisions. Phase 5 Human Approval is the
first explicit Human Governor gate and authoritative semantic gate; implemented in the Phase 5 slice.
Phase 4 ends at Insight Candidates, not Verified Insights; machine review remains fallible.

### SOURCE ROUTER — activate only what the user needs

| Route | Sources |
|---|---|
| A. SOCIAL LISTENING | TikTok; YouTube comments; Facebook public posts/groups; Reddit |
| B. OWNED CUSTOMER VOICE | Facebook Page comments; Facebook Inbox; future owned channels |
| C. REVIEW MINING | Google Maps; Trustpilot; Shopee; Lazada; future review sources |
| D. FORUM / COMMUNITY / PUBLIC DISCUSSION | VOZ; Webtretho; Tinhte; comments under news articles; future forums |
| E. MANUAL RESEARCH | Paste; CSV; Excel |

Every route may be independently enabled, disabled, run manually or scheduled independently.
Ingestion frequency and analysis frequency are separate: Facebook Inbox may ingest daily
and analyze weekly; Trustpilot may activate only for market/product research; YouTube may
activate for a specific research project. These are examples, not configured schedules.

All active routes converge to Normalized Evidence → Signal → Context → Pattern → Insight
Candidate. No source creates a separate intelligence engine. Adapter target fields and
UNKNOWN != ZERO are in [02](02-DATA-SCHEMA.md); review purchase rules in [03](03-EVIDENCE-RULES.md).
No router/scheduler/new adapter or state-store runtime in Phase 4.1.

### DOWNSTREAM ROUTER — only after HUMAN-VERIFIED insight

```text
A. CONTENT RESEARCH
Verified Insight → Content Opportunity → Topic → Angle → Human Selection
→ Content Intelligence Packet → Reelo

B. PRODUCT DISCOVERY
Verified Insight → Priority Need → Product Opportunity → Possible Value Map
→ Assumptions → Experiments → Evidence → Decision

C. CUSTOMER PROFILE UPDATE
Verified Insight → propose update to living Customer Profile
→ human approve supersession/merge
```

Future Business OS agents may consume the same verified insight contract. Product Opportunity
remains PROPOSED; human approval does not prove market demand. Profile updates cannot silently
replace conflicting knowledge. Reelo continues Writer → Critic → Output after direct typed
packet ingestion. Drive remains legacy compatibility/backup, never the primary future bridge.
Retain existing Topic/Angle/Human Selection gates even in condensed transport diagrams.

New V2 modules/endpoints/concepts must be platform-neutral. Do not introduce tiktok_* names
unless specifically a TikTok source adapter; do not rename the legacy Python package.

## Accepted product principles — Phase 4 authorization

Customer Intelligence is the sensing/understanding layer of an AI-native Business OS:

```text
Market / Customer Data → Customer Intelligence → Verified Customer Understanding
→ Decision Layer → Specialist Agents → Execution → Results / Evidence
→ Business Memory → next cycle
```

Specialist agents may serve Content, Product, Marketing, Sales, Operations, Finance
and future functions. This is long-term architecture, not additional Phase 4 runtime.

**AGENTS EXECUTE. EVIDENCE INFORMS. HUMAN APPROVES CONSEQUENTIAL DECISIONS.**

The owner is Governor/Approver at consequential gates: important customer truth,
Priority Need/opportunity, experiment/investment, strategic content angle, material
campaign budget, and Continue/Pivot/Kill. Do not require approval for every low-risk
mechanical step. Phase 4 does not implement an approval workflow; its candidates
remain pending_human_review, never automatically human_verified.

Agent handoffs must carry typed contracts, provenance, truth/epistemic status,
state and IDs. Prompt prose alone is not a durable integration contract.

## Productization and sources

Internal use → prove workflow → standardize → productize → distribute → Business OS.
Prefer reusable core, configurable niche/user layers, portable schemas,
platform-neutral naming and separation from owner-specific assumptions. Keep B2C-first
and Customer Profile = Jobs / Pains / Gains + Context independent from the solution.
No multi-tenancy or legacy Python package rename in Phase 4.

Source adapters: TikTok; Facebook Page comments/inbox; Facebook Group/comments;
manual paste; CSV/Excel; future YouTube and other sources → Normalized Evidence
→ shared Customer Intelligence Engine. YouTube is future source work only.

## Future incremental ingestion, separate from analysis frequency

Owned-source comments/inbox may arrive continuously/daily; intelligence analysis
may run periodically or manually. Future store: NEW → PROCESSING → PROCESSED,
with FAILED and IGNORED side states. Preserve source_platform, source_type,
source_item_id, source_url, received_at, processed_at, processing_status,
processing_batch_id and content_hash.

Deduplicate by durable source ID, with content hash as secondary protection.
PROCESSED items are not reprocessed by default; FAILED items can be retried;
every processing batch is traceable. No ingestion-state runtime in Phase 4.

## Future direct Reelo handoff

Google Drive is not the primary V2 bridge. Legacy export remains compatible/backup.
Target: Verified Insight → Content Opportunity → Human Selection → typed Content
Intelligence Packet → direct Reelo ingestion → Writer → Critic → Output.
This transport view retains the existing Topic/Angle and Human Selection gates;
it does not authorize bypassing them. Prefer typed API or equivalent structured
handoff. brief.md is not the contract.

Preserve useful /nap-insight dedupe, supersession, provenance and human approval
when replacing contradictory customer knowledge. Implement transport later, not
in Phase 4. Attached evidence is not human-, market- or purchase-validated.

## Operational rule

Read docs/v2/00–12 before architecture/product-logic work; STOP and report conflicts
with accepted decisions or Strategyzer foundations. Phase 4 ends at evidence-linked
Insight Candidates. No priority ranking, downstream generation, Reelo integration,
YouTube, ingestion state or Phase 6 is authorized by this north star; Phase 5 is separately authorized by DEC-048.
