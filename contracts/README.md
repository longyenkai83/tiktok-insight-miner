# Content Intelligence Packet contract

Canonical schema: **v2.content-intelligence-packet.1**. Contract release: **1.0.0**.
Machine-readable schema: [content-intelligence-packet.schema.json](content-intelligence-packet.schema.json),
JSON Schema Draft 2020-12 (Pydantic export). Runtime models and snapshot/current validators:
`tiktok_insight_miner/content_packet_models.py`, `content_packet_validator.py`.

This is the first production Agent-to-Agent typed contract defined for Business OS.
Implementation is PENDING ARCHITECT REVIEW; no production handoff/deployment or Reelo
integration has happened. Phase 9 will consume the typed packet directly. Drive is legacy/
backup only; brief.md, insights-pack and phan-tich-toan-dien.md are not this contract.

## Claim zones

| Zone | Contract field | Consumer authority |
|---|---|---|
| A — Customer Truth | customer_truth | Immutable verified insight, Jobs/Pains/Gains/behavior links, five B2C identity/context fields in scope, evidence, exact language, counters and limitations |
| B — Selected Strategy | content_strategy | Opportunity, Topic, Angle, Value Scene and objective are selected strategy, still PROPOSED; no promotion to customer truth |
| C — Creative Execution | creative_execution | Permission/constraint contract only, status not_generated; Writer may create presentation later without changing A or the selected meaning of B |

Writer may create hooks/titles/structure, analogies/metaphors, explicitly illustrative
examples, storytelling format, brand voice adaptation, clarity and CTA. Writer may not
invent customer facts, quotes, statistics, real cases, demographics, research, evidence,
market/purchase validation or remove inconvenient contradictions. Runtime Literal fields
and JSON Schema const constraints encode these permissions. Phase 8 does not generate
Zone C prose or validate a future WriterResult; that belongs to later integration.

## Portable snapshot and trust

Each packet contains exactly one selected angle and one verified insight. It includes
the full cited source snapshots needed for its evidence, context and counter-evidence,
not the complete run, previous approval history or unrelated alternatives. No relative
paths, Markdown parsing, Google Drive, niche config or Miner output folder is required
to understand the selected customer intelligence. Source metadata remains untrusted data.
Profile links/pattern IDs retain explicit immutable identifiers for deeper audit.

Two validation levels must remain distinct:

1. **Snapshot integrity:** JSON Schema shape/types plus runtime quote/span/source hash,
   packet checksum, language, scene, internal lineage and external-requirement consistency.
   This can run offline and leaves current authorization **NOT_CHECKED_OFFLINE**.
2. **Current authorization:** runtime validation against current verified artifact,
   Content Tree, selected-angles export, authoritative governance ledger and selection
   ledger. The entire projected snapshot must match. Build, save and UI export require
   this level. Never substitute a packet's historical hashes for actual current state.

JSON Schema alone cannot verify source spans, semantic fidelity, hashes or revocation.
Unsigned hashes are integrity links, not authenticated signatures. A malicious party who
rewrites all data/hashes cannot be authenticated offline by this contract. Phase 9 must
define a trusted intake/currentness mechanism without reopening customer truth through AI.
An old packet can remain structurally valid while no longer authorized for new work.
External requirements must be researched/grounded before publication, not fabricated.

## Revisions and immutability

packet_id is `CIP-` plus SHA-256 of canonical packet data excluding packet_id, using
the existing project's `value_hash` canonical JSON (`ensure_ascii=False`, sorted keys,
default JSON separators). created_at is timezone-aware. packet_revision starts at 1;
later revisions identify supersedes_packet_id. Use the Python builder for canonical
hash/time serialization; JSON Schema alone does not prescribe cross-language serializers.

Build with an explicit previous packet from the same project/run to establish revision
lineage. Unchanged inputs return the previous packet unchanged; material state/goal/angle
changes produce a new ID/revision. Immutable storage refuses replacement of a different
packet at an existing path. Save each revision separately and retain ancestors. Consumers
check revision links with validate_revision when traversing history; the predecessor need
not be re-authorized today to remain a historical record. This is not a distributed registry
or automatic latest-version index; concurrent branches/forks remain explicit references.

## Compatibility/versioning

- **PATCH:** wording/clarification or non-wire release metadata that does not change accepted
  JSON, validation semantics or immutable packet meaning; release 1.0.x.
- **MINOR:** optional backward-compatible capability; new published schema identifier and
  release 1.x.0, with fixtures and compatibility tests. Strict old consumers reject unknown
  fields/versions until they explicitly adopt the new schema.
- **MAJOR:** breaking field/truth/permission/lineage semantics; new schema identifier,
  release x.0.0, explicit migration and architect review.

The current identifier `.1` is a schema revision identifier, not a floating version range.
Do not silently change semantics or treat schema version acceptance as permission to upgrade
evidence. Existing producer and consumer must pin the exact supported version.

## Synthetic interoperability fixture

[fixtures/synthetic-content-intelligence-packet.json](fixtures/synthetic-content-intelligence-packet.json)
contains **SYNTHETIC TEST ONLY** source comments, a synthetic approved insight, synthetic
human selection, grounded language, counter-evidence and grounded/proposed Value Scene.
No customer data or real owner decisions. It is portable input for later Reelo contract tests.
The synthetic upstream producer is `tests/fixtures/content_packet_fixture.py`.

Regenerate intentionally from repository root:

```text
python -m tests.fixtures.export_content_packet_contract
python -m pytest tests/unit/test_content_packet.py -q -p no:cacheprovider
```

Regeneration creates new synthetic upstream IDs/timestamps; review and commit fixture changes
deliberately. Tests compare exported schema to runtime schema to detect drift. jsonschema is
a dev-only dependency. No model/API call is used in packet generation or contract tests.
