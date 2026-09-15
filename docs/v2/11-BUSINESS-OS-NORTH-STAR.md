# 11 — BUSINESS OS NORTH STAR

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
in Phase 4. Evidence-backed is not human-, market- or purchase-validated.

## Operational rule

Read docs/v2/00–11 before architecture/product-logic work; STOP and report conflicts
with accepted decisions or Strategyzer foundations. Phase 4 ends at evidence-backed
Insight Candidates. No priority ranking, downstream generation, Reelo integration,
YouTube, ingestion state or Phase 5 is authorized by this north star.
