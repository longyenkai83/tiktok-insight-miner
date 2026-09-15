# 13 — CONTENT ROUTE

Current Phase = Phase 6 — Content Route

Status = IMPLEMENTED — PENDING ARCHITECT REVIEW

Core Customer Intelligence MVP = ACCEPTED (owner's Phase 6 authorization).

Next Phase = DO NOT START. No Product Discovery, final writing or Reelo integration.

## Boundary and authority

Verified Insight → Content Opportunity → Topic → Angle → Human Angle Selection.
Every edge supports one-to-many expansion. Content Opportunity is a useful conversation,
Topic is a territory, Angle is a specific argument/lens; these are not interchangeable titles.
The current authoritative Phase 5 ledger must validate the full `v2.verified-insights.1`
artifact at generation, persistence, selection and export. A boolean, machine candidate,
stale projection or broken evidence chain is insufficient. Approval is corpus-scoped,
not proof of purchase or market demand. B2C identity and Strategyzer foundations remain binding.

## Typed transport and code-owned evidence

`content_route_models.py` defines separate opportunity/topic/angle types in a combined
`v2.content-tree.1` envelope. Object schema versions are `v2.content-opportunities.1`,
`v2.topics.1`, `v2.angles.1`. Each carries project/run, producer, time, generation ID,
verified insight ID/hash, supporting patterns, scope/profile links, evidence references,
counts, contradictions, variations, limitations and constraints. IDs/hashes and all evidence
fields are assembled by code. Models only return local proposal IDs, the supplied closed
parent ID, proposed prose, purpose/type and optional Value Scene evidence IDs.
Unknown IDs/extra evidence fields are rejected; persisted objects replay against transports
and upstream evidence. Customer truth remains a separate immutable DERIVED statement.
All new content objects and prose are PROPOSED; selecting them never upgrades their truth.

Opportunity: statement, purpose, customer_value. Topic: title, description, customer_value,
content_opportunity_id. Angle: title, angle_type, core_argument, belief_before, belief_after,
opening_direction, customer_value, value_scene, language_bank, topic/opportunity IDs.
Purpose and angle enums are small/general, with `other`; no legacy eight-type backbone.
`selected_angles` V1 is not the V2 schema or naming authority.

All generated prose uses `ProposedText(text, claim_kind, truth_type=PROPOSED,
needs_external_evidence=true)`. `claim_kind` separates general explanation from creative
framing. The conservative external-evidence flag means pending checking, even for creative
framing; it does not license invented facts. Lexical guards reject numeric claims, fabricated
quotes, named research/cases, unsupported demographics, generalized customer truth and
obvious final-script/product-discovery output. They do not prove semantic entailment.
No generated framing is written back into customer evidence, profile, Gain or verified insight.

## Value Scene and language

Need moment → Current struggle → Desired future. Each field is nullable, exact source wording
with an upstream reference, or explicitly PROPOSED framing with a pending external check.
Grounded need moment accepts context or behavior.trigger; struggle accepts pains/behavior;
desired future accepts gains only. A pain cannot be relabeled a grounded Gain. Missing Gain
stays null or proposed aspiration. Code copies exact quotes and original OBSERVED/DERIVED
truth from the validated reference. Language bank includes only upstream `language.*` refs;
it can be empty. Model titles, openings and paraphrases never become customer language.

## Generation and persistence

Requested counts 1–50, optional objective and angle-type preference are controls, not quotas
or success thresholds. UI includes “Bung 10 góc”. Fewer valid outputs are allowed. Exact/near
duplicate normalized arguments (including before/after belief) are rejected within a parent;
changing just the title does not create a distinct angle. Text similarity is not a semantic
diversity guarantee; architect/human review remains necessary. Generation failures retain
issue codes without private exception bodies. Payloads above the provider limit and truncated
responses fail explicitly. No automatic retry that silently changes grounding.

Selection history `v2.content-selection-history.1` uses append-only, hash-linked events with
selected/rejected/deferred, reviewer label, explicit human attestation, time, rationale,
angle hash and full tree hash. No initial selection. Exact request retries are idempotent.
Later reject/defer revokes eligibility. A changed tree requires fresh selection; historical
choices remain visible. Atomic JSON replacement, OS file locks and optimistic hashes reuse
Phase 5 storage. This is local integrity, not authenticated reviewer identity or distributed
transactional authorization. Callers must use the current tree and governance/selection ledger.

Export is `v2.selected-content-angles.1`, a replayable typed projection with its selection
history, not a Content Intelligence Packet. Phase 8 packet and Phase 9 Reelo are future work.

## Explicit UI / CLI

Existing webapp: enable **V2 Content Route** in sidebar, choose Human Review workspace and
content run. Select a Verified Insight, create opportunities, expand topics, generate angles,
inspect inline evidence/contradictions/Value Scene/language, then explicitly select/reject/defer.
Selections survive new sessions. No verified insights means no AI request.

Independent commands (default legacy commands are unchanged):

```text
tim build-content-tree --verified-insights verified_insights.json --reviews insight_reviews.json --project-id demo --run-id research --opportunities 2 --topics 2 --angles 10 -o content_tree.json
tim prepare-content-selection --tree content_tree.json --reviews insight_reviews.json --selections content_selections.json
tim select-content-angle --tree content_tree.json --reviews insight_reviews.json --selections content_selections.json --angle-id ID --angle-hash HASH --tree-hash HASH --request-id UNIQUE --reviewer OWNER --confirm-human --decision selected
tim export-content-selection --tree content_tree.json --reviews insight_reviews.json --selections content_selections.json -o selected_content_angles.json
```

Use current hashes printed by prepare; never manufacture human decisions. Build accepts
`--objective`, `--angle-type`, `--model`; model precedence is explicit option,
CONTENT_ROUTE_MODEL, ANTHROPIC_MODEL, existing default. All content files contain upstream
customer data and must remain local/ignored. Read docs 00–13 before architecture/product logic.

## Review limits

Offline fixtures explicitly simulate human approval; they are not customer approvals.
Real-data generation must be SKIPPED when the actual ledger has no approved insights.
No numeric quality threshold is invented. Full tests validate integrity and workflows, not
live model quality. Retained raw proposals may include rejected text and must be treated as
untrusted private data. Conservative lexical guards may reject useful phrasing or miss
subtle unsupported implications. Large histories duplicate provenance and replay it, so
performance is suited to a local MVP and remains a review concern.
