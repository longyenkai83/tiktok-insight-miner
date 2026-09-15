# 08 — PROJECT STATE

Current Phase = Phase 6 — Content Route
Status = IMPLEMENTED — PENDING ARCHITECT REVIEW
Core Customer Intelligence MVP = ACCEPTED
Next Phase = DO NOT START

Branch: v2-phase-6-content-route. Base: 7972a849b27fed00308bcfd2870bf8a24c2be216.
Authority: owner Phase 6 request; DEC-053–056; read docs 00–13.

Implemented separate opt-in opportunity/topic/angle generation, code-owned evidence, Value Scene,
literal language bank, replayable typed tree, append-only explicit human selection and export.
Current Phase 5 ledger remains the input gate. New UI exposes evidence at every layer and
supports variable counts / Bung 10 góc. CLI supports build/prepare/select/export.
New generated content is PROPOSED; customer evidence remains immutable.

Default legacy runtime changed: NO. No final scripts/articles, Product Discovery, Reelo,
router/scheduler/adapters, dependency changes or main merge.

## Verification

`python -m pytest tests -q -p no:cacheprovider` → **401 passed in 24.67s**.
36 new offline cases; all 365 previous cases pass. Includes complete Streamlit generation,
explicit selection and fresh-session persistence, CLI roundtrip, closed IDs, fake evidence/
language/prose rejection, Value Scene, stale inputs/history, human gate and schema replay.
Python 3.13.15 / pytest 8.4.2. No live API calls in tests.

Real-data generation: SKIPPED. The existing Phase 5 real-sample ledger has zero human
review events and zero Verified Insights; the owner accepting the MVP does not approve
individual customer insights. No customer decisions or content invented by the agent.
Local review: output/phase6-content-review/phase6-content-review.md (ignored).

## Known limitations

No live provider quality assessment. Lexical guards and near-text dedup are conservative,
not semantic guarantees. All proposed prose flags external checking, including creative framing.
Histories replay full provenance and may become expensive at scale. Local reviewer labels are
not authenticated identities; local atomic operations are not distributed transactions.
Future consumers must validate the current tree and both current ledgers. No next phase started.
