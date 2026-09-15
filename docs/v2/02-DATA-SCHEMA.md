# 02 — DATA SCHEMA

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

New typed objects: v2.content-opportunities.1, v2.topics.1, v2.angles.1, combined v2.content-tree.1; selection history v2.content-selection-history.1 and export v2.selected-content-angles.1. See document 13 for fields and provenance.

## Earlier phase documentation (historical gates)

## Phase 5 — executable human contracts

`v2.insight-reviews.1`: ordered immutable v2.insights.2 snapshots and append-only events;
last snapshot is current. Event: review_event_id, sequence, previous_event_id,
source_schema_version, source_insights_hash, action, reviewed_at, original_statement,
approved_statement. Action: request_id, candidate_insight_id/hash, decision, reviewer_id,
human_attested=true, edited_statement when edited, rationale and PriorityDecision.
Decision is approved / edited_and_approved / rejected / deferred, never verified.

`v2.verified-insights.1`: input_reviews_hash, review_history, verified_insights. Every record
has verified_insight_id, source_candidate_id/hash, source_insights_hash, revision, supersedes,
DERIVED statement with machine_approved/human_edited origin, unchanged evidence/profile/scope,
relationship type, support_pattern_ids, human_review, verification, priority, status=verified.
No rejected/deferred record in current projection. Original candidate and machine review stay
in immutable snapshots; original and edited text remain in the event. Whole-statement refs
are retained; old machine part offsets are not reused for edited wording.

Verification: source_grounded=true, evidence_support_present=true, machine_review_passed=true
with machine_review_scope=source_candidate_only, human_verified=true, market_validated=false,
purchase_validated=false. Human edits are not falsely claimed to have fresh machine review.
Only explicit approved/edited_and_approved events can materialize these records; a flag alone
is not enough. Full envelope replay checks event chain, source/hash, decision and copied fields.

PriorityDecision: priority_status unassessed/monitor/priority_need, assessment_origin human_assessment;
optional important/urgent/frequent/expensive/emotional_intensity high/medium/low/unknown (default
unknown), note. No auto score or forced completeness. Non-default priority requires approval.

Downstream must use require_verified(full_artifact, current_authoritative_reviews), not a
standalone VerifiedInsight flag. Old ledgers/candidates/stale projections fail. Source schema
v2.insights.2 and earlier extraction contracts remain unchanged. Detailed contracts and
revision/storage rules: [12-HUMAN-GOVERNANCE.md](12-HUMAN-GOVERNANCE.md).

## Phase 4.1 schema transition — explicit rejection, no implicit migration

`v2.insights.1` → `v2.insights.2` is an intentional unreleased V2 contract break.
Readers reject old/unknown versions with an explicit expected-version error, before
validating the payload. Keep old artifacts as historical files; do not only edit their
version or rename evidence_backed. Rebuild from the original validated patterns plus
saved candidate/review transports (or explicitly requested new synthesis), writing a
separate file. No silent promotion, automatic migration or Phase 1–3 schema change.

- Remove verification.evidence_backed; add evidence_support_present=true and
  machine_review_passed (strict boolean, required in verification).
- machine_accepted replaces outcome accepted; Insight status remains pending_human_review.
- Each outcome also carries machine_review_passed: true only for a usable, correctly
  bound review passing all existing checks; false for negative, missing, duplicate,
  stale, malformed or invalid-support review, and candidates never reviewed.
  False alone does not distinguish failed from not run: inspect review/issues.
- Deduplicated candidates still passed review; they point to the retained candidate.
- Envelope replay checks outcome flags against reviews and emitted verification against
  code-built evidence. An empty/missing/forged evidence bundle cannot claim support.
- Structural source validity and attached support are not semantic certainty. Phase 5
  alone may later approve a Verified Insight; its schema/workflow is defined in 12-HUMAN-GOVERNANCE.md.

## Future normalized source adapter contract — design only (DEC-045)

Target fields:

```text
source_platform, source_type, source_item_id, thread_or_parent_id,
source_url, source_title_or_context, text, author, created_at,
likes, reply_count, rating, verified_purchase,
received_at, processed_at, processing_status, processing_batch_id, content_hash
```

Unavailable fields remain unknown/null: UNKNOWN != ZERO. This includes verified_purchase:
missing is not false. A reliable explicit source verified_purchase field may be represented
separately by a future adapter with provenance; star rating/text/platform cannot fill it.
Preserve author privacy; do not infer identity. No new adapter or source-store runtime here.
Source item lifecycle NEW → PROCESSING → PROCESSED; FAILED/IGNORED side states.
Durable source ID (namespaced to source) is primary dedupe key when available, content hash
secondary protection. Do not reprocess PROCESSED by default; FAILED can retry; retain batch
trace. Analysis can be periodic/manual independently of ingestion.

## Phase 4.1 — executable `v2.insights.2`

Strict envelope: schema_version, generated_at UTC, method=closed_patterns_semantic_review.1,
producer/model/prompt version, input_patterns_hash and embedded v2.patterns.1 snapshot,
synthesis_status complete/error, insights, candidate outcomes, upstream_issues and new
validation_issues. Full artifact is private/local; never commit source snapshots.

Transport: candidates[{insight_candidate_id, support_pattern_ids, relationship_type,
concise_statement}]. No model quotes/comments/metrics/demographics/truth override fields.
Short pattern IDs are exact-mapped in synthesis and review transports; unknown IDs rejected,
never fuzzy repaired. Invalid item rejected separately; valid items survive. Duplicate
candidate IDs reject all affected candidates; duplicate support IDs reject the candidate.

Relationship types: single_pattern; job_pain; pain_behavior; pain_gain; situation_pain;
stage_decision; current_solution_frustration; language_behavior; pattern_relationship.
Code checks category/path compatibility. Pattern_relationship covers a supported form not
captured by the specific examples, not permission for unconstrained speculation.

Separate semantic review binds candidate ID/hash and unchanged support IDs to supported,
adds_understanding, scope_preserved, no_unsupported_causality, no_demographic_leak,
no_solution_leak, no_market_generalization and reason_code. Every check must pass. Code splits statement parts at sentence/semicolon boundaries;
review returns one closed pattern-ID mapping per part. Missing/duplicate/unprovided part
or pattern mappings reject. Final statement_support uses code-computed Unicode offsets
and validated pattern IDs for each part, including the scope-prefix offset.
Missing/duplicate/unknown/invalid review cannot approve a candidate. A saved review is a
machine assessment, not a human signature or objective entailment proof.

Insight: deterministic insight_id; statement{text,truth_type=DERIVED}; relationship_type;
support_pattern_ids; customer_profile_links (jobs/pains/gains/behavior/language/context →
existing pattern IDs only); scope; evidence_summary; exact evidence_refs; variations;
possible contradictions; verification; evidence_kind; limitations; pending_human_review;
semantic_review, statement_support and validation_issues. Code adds a cited-evidence scope prefix to statement.
All evidence fields are assembled from selected input patterns, not model output.

Scope: population=cited_source_comments_only, source_comment_ids, shared_comment_ids,
relationship_scope=within_comments/across_corpus, five B2C context arrays and missing context.
Shared means intersection of supporting patterns' comment sets; it does not mean every
member expresses the whole relationship. No intersection forbids within-person inference;
scope explicitly limits interpretation to corpus comparison. Context variants remain separate.

evidence_summary reuses Phase 3 Support: distinct source comments/authors/videos, totals null
when any source metric is unknown, known sums and missing coverage. A source present in
several patterns contributes once. Counter-evidence does not inflate supporting count unless
its source is also explicitly in another selected support pattern; such tension stays visible.

EvidenceKind vocabulary: customer_speech/customer_behavior/commitment/payment/market_behavior.
Current v2.patterns.1 sources only support customer_speech, including text self-reporting
behavior or payment. No promotion from platform/name/keywords. Future stronger evidence needs
typed observations and a separately reviewed adapter/schema; enum existence is not proof.

Verification has source_grounded=true and evidence_support_present=true for emitted candidates;
machine_review_passed=true is computed from the bound automated review, not semantic certainty.
human_verified=false, market_validated=false, purchase_validated=false are enforced literals.
Outcome status machine_accepted/rejected/deduplicated preserves candidate, issues and review binding;
deduplicated items reference the kept insight. Rejected malformed transport is not imported
as customer truth. Reader revalidates nested provenance and replays deterministic fields,
statement construction, review binding, code guards and dedupe. Hashes are not signatures.

Dedupe requires identical sorted support IDs, relationship type and ordered normalized
statement tokens (Unicode NFKC, case/whitespace/punctuation). Different wording order,
negation or scope is not merged merely for sharing keywords; semantic paraphrase dedupe is
not implemented. Numeric assertions are conservatively rejected from generated prose;
measured numbers remain in code-generated evidence_summary and exact source context.

CLI: `tim build-insights --patterns patterns.json [-o insights.json] [--model MODEL]`.
Model explicit → INSIGHT_MODEL → ANTHROPIC_MODEL → existing default. Output defaults beside
input; no input overwrite. Exit 0 completed/no issues; 2 rejected candidates, upstream/new
issues or provider failure; 1 malformed input/output. Complete refers to finished processing,
not universal candidate acceptance. Empty valid results are allowed, not filled to a quota.
Provider limits: 200 patterns, 300,000 characters per request; explicit error, no truncation.
Semantic review batches of six; limits are transport bounds, not numeric quality thresholds.

## Phase 3 — executable schema `v2.patterns.1`

`pattern_models.py` là contract strict, extra fields bị từ chối. Input Phase 1/2 không đổi schema hoặc extraction behavior.

Envelope: schema_version, generated_at UTC, method=`closed_relations_complete_link.1`, label_method=`extractive_representative.1`, similarity_provider/model/prompt version, semantic_status (`complete`, `not_requested`, `error`), input_signals_hash/input_contexts_hash, embedded input_signals/input_contexts snapshots, accepted relations, patterns, language_bank, validation_issues, limitations. Canonical hashes dùng cùng SHA-256 sort-keys JSON như Phase 2.

Embedded snapshots làm file tự đủ để kiểm cả source span **và claim membership**, không chỉ kiểm quote có trong comment. Artifact này chứa dữ liệu khách, chỉ lưu private/local, không commit. Reader/save revalidate upstream models, source hashes, matching input artifact hash và replay deterministic groups/metrics/labels/refs; output sửa/bịa member/quote/metric/label bị từ chối. Hash không phải chữ ký xác thực.

Pattern: pattern_id (hash của sorted evidence IDs), pattern_type (`jobs/pains/gains/behavior/language/context`), subcategory (hoặc mixed, refs giữ subtype thật), label, normalized_meaning, truth_type=DERIVED, support, evidence_refs, context_distribution, missing_context_comments, variations, contradictions, contradiction_search, pattern_status=candidate, validation_issues.

EvidenceRef: evidence_id, origin signal/context, upstream_claim_id, comment_id, source_record_id, source_hash, start/end, exact evidence_quote, signal_path, original truth_type OBSERVED/DERIVED. Reuse `validate_source_span` và source snapshot models; không tự nâng upstream truth type. Context pattern chỉ dùng claim của context record có matching signal **record**; record no_signal vẫn tồn tại và có thể có context hợp lệ.

Relations: left/right evidence IDs, kind same_meaning/variation/contradiction, truth_type=DERIVED. Không nhận member text hoặc new claims từ model. Pair lặp bị loại có issue. Nếu merge và contradiction xung đột, không merge; giữ possible counter-ref kèm conflicting_relation để review, không giấu phản chứng. Label/variation label DERIVED; counter relationship DERIVED/possible_contradiction, giữ supporting_ref và counter_ref có truth type gốc.

Support tính trên distinct source_record_id: comment_count; unique_authors/source_count nullable; known_author_count/known_source_count và unknown_*_comments; total_likes/total_replies nullable, known_*_sum và unknown_*_comments. Total là null nếu **bất kỳ** member thiếu metric, known sum vẫn có coverage. Measured zero được giữ là zero. Author đếm theo platform+supplied author ID; không xác minh số người thật. Source count theo platform+video_url. Không dedup văn bản trùng giữa các ID khác nhau thành một người; không khôi phục identity/repost mà adapter không có.

Context distribution gồm field, exact representative label, DERIVED, evidence_refs và support; giữ riêng năm field đã khóa. Unknown là missing_context_comments, không final segment. Variations giữ từng exact wording cùng refs, không giả định mọi khác biệt từ vựng là cơ chế đã xác minh.

Language bank nhóm theo **exact original phrase**, giữ refs của accepted language spans và distinct-comment/author counts. Có thể giữ singleton phrase nhưng chỉ từ hai comment phân biệt mới là lặp trong mẫu; không suy market prevalence. Phase 1 repeated_expressions giữ nguyên nghĩa lặp trong một comment; spans đó có thể đóng góp exact phrase ở Phase 3, không sửa input.

CLI: `tim build-patterns --signals signals.json --contexts contexts.json -o patterns.json [--model MODEL] [--exact-only]`.
Contexts optional; default output cạnh signals. Semantic model explicit → PATTERN_MODEL → ANTHROPIC_MODEL → existing default. Exit 0 complete, 2 khi có upstream/semantic issues, 1 input/output lỗi. Không ghi đè input. Python API `build_patterns(..., provider=None)` là exact offline baseline; CLI mặc định truyền semantic adapter.

## Phase 2 — per-comment Customer Context

Input duy nhất của CLI là `signals.json` schema `v2.signals.1`, được load và revalidate trước API. Output `contexts.json` schema `v2.contexts.1` không sửa hoặc thay thế signals.json. CustomerContext chưa phải cluster, final segment, customer profile toàn corpus hoặc Verified Insight.

Transport: `results[{comment_id, contexts[{field, evidence_quote, truth_type, confidence}]}]`. Model không sinh claim. `field` chỉ có audience_segment, context, situation, life_or_business_stage, user_buyer_distinction; chỉ OBSERVED/DERIVED, confidence high/medium/low. Code tạo final claim từ exact validated source span, không thêm demographics/meaning bằng paraphrase.

Envelope: schema_version, generated_at UTC, model, prompt_version=phase2.context.1, derivation_method=source_span_context_assignment, input_schema_version, input_signals_hash, upstream_issues, records và validation_issues. input_signals_hash là SHA-256 của input model JSON canonical (sort keys), phục vụ đối chiếu artifact Phase 1, không là chữ ký xác thực.

Record: comment_id, source (SignalSource nguyên snapshot Phase 1), source_hash, upstream_status/upstream_issues, customer_identity, extraction_status, validation_issues. `customer_identity` luôn có đúng năm arrays theo field đã khóa; unknown là array rỗng, user_buyer_distinction không cần thì rỗng. Mỗi ContextClaim có field, claim_id, claim, evidence_quote, truth_type, confidence, comment_id, source_record_id, source_snapshot_hash, start/end. Claim ID xác định bởi snapshot hash + field + span; không reset theo category.

Claim và evidence_quote bằng chính source.text[start:end]. Chỉ chuẩn hóa whitespace để tìm span; giữ exact source wording trong output, không chữa quote bịa. Helper `quote_span` và `validate_source_span`, SignalSource/hash, StrictModel/TruthType/ValidationIssue được reuse từ Phase 1; không thay schema hoặc luật Phase 1. `ContextIssue` mở rộng issue bằng field nullable để đếm rejection theo field; field lạ không được tự map sang field hợp lệ.

Status: ok có claims không có lỗi; no_context là extraction hợp lệ rỗng; partial có item lỗi (kể cả không còn claim); error là record/batch không dùng được. Missing/duplicate model IDs tạo error cho source tương ứng; unknown IDs bị loại và ghi envelope issue. Item lỗi bị loại riêng, giữ item tốt. API/refusal/truncated/JSON lỗi tạo error records, authentication failure dừng request kế tiếp. Empty signals envelope không gọi API.

Phase 2 xử lý mọi source snapshot hợp lệ trong signals.json, kể cả record Phase 1 no_signal/partial/error: context là phép đọc source riêng, không dùng tín hiệu lỗi để suy fact. Upstream status/issues giữ nguyên, không ngầm đổi Phase 1 thành thành công. Model chỉ nhận comment ID và source text, không video topic, metadata tác giả, config hay claim của comment khác.

CLI: `tim extract-context -i signals.json [-o contexts.json] [--model MODEL] [--batch-size 10]`. Model resolution explicit → CONTEXT_MODEL → ANTHROPIC_MODEL → existing default claude-opus-4-7. Output mặc định cạnh input. Exit 0 complete, 2 khi context có partial/error/global issue, 1 input/output lỗi. Không ghi đè input.

Generic Customer Identity/Profile và downstream types phía dưới vẫn là thiết kế; executable Pattern schema ở đầu tài liệu. Ví dụ normalized audience label ở task chỉ là conceptual; implementation Phase 2 giữ nguyên evidence wording làm claim, field assignment là phép DERIVED khi thích hợp. Không thêm free-form label vì quote đúng không chứng minh label đó đúng.

## Downstream design — chưa triển khai

Theo kiến trúc khóa DEC-024–032, Verified Insight/Jobs/Pains/Gains có evidence là nguồn của Priority Need, Content Opportunity hoặc Opportunity Area. Product Opportunity/Possible Value Map là PROPOSED, không validated demand. Chỉ có validation qua Assumption → Experiment → Evidence → Decision; không suy nhu cầu từ solution/config. Đây là định nghĩa thiết kế, không schema executable, router hay generator trong Phase 2.

## Phase 1 — schema đã triển khai, chờ architect review

`signal_models.py` định nghĩa `SignalsEnvelope` với `schema_version="v2.signals.1"`, `generated_at` UTC, model đã resolve, `prompt_version="phase1.extractive.2"` từ Phase 1.1, `derivation_method="source_span_categorization"`, records[] và issues[]. Reader vẫn nhận prompt version `phase1.extractive.1` của artifact cũ. Không phụ thuộc classified.json.

Mỗi record gồm comment_id, source, signals[] và extraction_status (ok/no_signal/partial/error), issues[]. Mỗi signal có category/subcategory, claim, truth_type **chỉ OBSERVED hoặc DERIVED**, evidence_quote, confidence high/medium/low, signal_id, source_record_id, source_snapshot_hash, start/end. Offset nửa mở theo Unicode code point trong source.text gốc. LANGUAGE cũng dùng record có kiểu để giữ cùng provenance, không chỉ chuỗi rời.

Taxonomy thực thi:

| category | subcategory |
|---|---|
| jobs | functional, social, emotional, supporting |
| pains | negative_outcomes, obstacles, risks_fears, costs, frustrations |
| gains | required, expected, desired, unexpected |
| behavior | trigger, current_solution, alternatives, workarounds, decision_criteria, objections |
| language | exact_phrases, emotional_wording, repeated_expressions |

Khác ví dụ conceptual: dùng danh sách signal phẳng có category/subcategory thay các mảng lồng nhau; mảng rỗng nghĩa không tìm thấy signal. Không thêm AudienceContext/CustomerIdentity hoặc CONTEXT category trong Phase 1. Per-comment context thuộc Phase 2; final segmentation thuộc downstream analysis. Generic schema phía dưới vẫn là thiết kế tương lai; không yêu cầu HYPOTHESIS, audience_context_ref, Pattern hoặc Insight để chạy Phase 1.

Phase 1.1: candidate transport chỉ có category, subcategory, evidence_quote, truth_type, confidence. Model không sinh claim. Sau khi quote qua source-span validation, CODE tạo `claim = source.text[start:end]` và giữ exact evidence_quote. Quote bịa/paraphrase không được sửa cho khớp nguồn; field claim do model gửi ngoài contract bị từ chối, không được âm thầm thay bằng quote.

DERIVED biểu diễn phép diễn giải khi gán category/subcategory, không sinh paraphrase tự do. Output signals.json giữ các field cũ, source hashes/spans và version schema; reader vẫn chấp nhận semantic claim của artifact cũ chỉ khác quote về whitespace. LANGUAGE giữ nguyên tuyệt đối cả whitespace của đoạn nguồn. `language/repeated_expressions` chỉ kiểm lặp trong một comment; lặp xuyên comment/corpus thuộc Pattern phase tương lai, không được suy ra trong Phase 1.

Source giữ comment_id, text, author, likes/reply_count nullable, created_at/video_url/platform khi có, metadata gốc và metric_notes. Hash SHA-256 bao phủ source snapshot; source ID lấy từ platform/URL/comment ID. Signal ID xác định bởi snapshot, category/subcategory và span. Model chỉ nhận ID + toàn bộ text, không nhận metadata riêng tư, persona/config hay sản phẩm. Không truncate text.

Giữ raw input ở metadata để trace, không chứng nhận raw metadata là customer fact. Metric thiếu/không được source cung cấp là null; legacy zero không có raw proof là null với lý do, giá trị input vẫn giữ riêng. Không phục hồi thông tin đã bị adapter cũ làm mất. Source time để nguyên giá trị nguồn; generated_at không giả làm thời điểm scrape.

File `signals.json` là artifact riêng. `load_signals_json()` kiểm lại schema/version, source hash/ref và quote spans khi đọc. Không là typed Content Intelligence Packet, chưa đủ điều kiện Writer. Không có clustering, profile, insight, topic, angle hoặc hypothesis generation.

## Phạm vi thiết kế đích (ngoài schema Phase 1 phía trên)

Phần generic dưới đây là hợp đồng thiết kế cho các phase tương lai, không phải toàn bộ schema executable hiện hành. Các nguyên tắc trong DEC-001–010 là ACCEPTED theo yêu cầu; tên field và bố cục dưới đây là PROPOSED để review trước triển khai. Không phụ thuộc Pydantic/JSON Schema/V1. Dùng thống nhất `truth_type ∈ {OBSERVED, DERIVED, HYPOTHESIS, PROPOSED}`.

Ký hiệu: `T[]` là danh sách; `T?` cho phép null; `Ref<T>` gồm ID và version của bản ghi T. Khi đã serialize, ID phải duy nhất trong namespace và ổn định qua export; không đánh lại ID theo bucket/run. Mọi Ref phải phân giải được trong snapshot hoặc manifest nguồn được kiểm chứng.

## Kiểu dùng chung

| Kiểu | Trường bắt buộc về mặt thiết kế |
|---|---|
| RecordEnvelope | id, schema_version, record_version, created_at, producer, upstream_refs[] |
| SourceRef | source_record_id, source_record_version, snapshot_hash |
| TextSpan | source_ref, start, end, exact_text; offset nửa mở theo Unicode code point trong canonical_text |
| Claim | id, statement, truth_type, source_refs[], evidence_refs[], assumption_refs[], scope, limitations[] |
| Derivation | method, input_refs[], producer_version, parameters_or_prompt_version, generated_at |

Mọi domain record có RecordEnvelope. Claim DERIVED bắt buộc có Derivation và ít nhất một đường về source comment. Claim OBSERVED phải có source_ref trực tiếp cùng span hoặc metadata field tương ứng. HYPOTHESIS có thể chưa có nguồn: phải nêu assumption_refs/giả định, lý do thiếu bằng chứng và validation_plan; không được tạo source_ref giả. PROPOSED phải có mục tiêu, rationale và tham chiếu nền tảng nếu được dùng cho nội dung.

`confidence?` chỉ là đánh giá mức chắc chắn của phép suy luận, không là bằng chứng, tỷ lệ thị trường hay quyền nâng truth_type. Không có ngưỡng mặc định trong Phase 0. Ngày giờ dùng timestamp có timezone; không biết dùng null và missing_reason, không tạo ngày/số 0 thay thế.

## SourceRecord

- source_kind: comment; platform; external_comment_id?; source_url?; parent_external_id?.
- captured_at; posted_at?; canonical_text; snapshot_hash; retrieval_context (run/query/dataset reference).
- metrics: likes?, replies?, observed_at, missing_fields[]; mỗi giá trị phải truy được field nguồn.
- author_ref? là định danh hạn chế/ẩn danh, không suy demographic.
- redactions[] mô tả span đã che và chính sách; original_snapshot_ref? chỉ trỏ kho được phép truy cập.

Phải có ít nhất external ID hoặc locator nhập liệu đủ phân biệt nguồn. Thiếu nguồn đối chiếu thì không đủ điều kiện đưa vào packet. canonical_text là snapshot dùng để kiểm quote; thay đổi/redact tạo version mới, không âm thầm sửa bản cũ. Không đẩy raw riêng tư/PII vào Git. Số like chứng minh metadata được quan sát tại thời điểm lấy, không chứng minh quan điểm là đúng.

## Customer Identity V2 — B2C-first

Tên field chuẩn đã được chủ dự án chốt (DEC-020):

```text
audience_segment
context
situation
life_or_business_stage
user_buyer_distinction (optional)
```

`life_or_business_stage` là một field thống nhất, không tách thành hai field riêng. Khi không có dữ liệu phù hợp, giữ null/unknown với lý do theo quy tắc nguồn; không bịa giá trị để điền. `(optional)` là chú thích, không phải một phần tên field `user_buyer_distinction`.

- CustomerIdentity: `audience_segment`, `context`, `situation`; `life_or_business_stage` chỉ khi liên quan tới use case B2C.
- `user_buyer_distinction` (optional): chỉ xuất hiện khi cần phân biệt người dùng và người mua trong use case B2C; kèm use_case_reason và Claim có nguồn cho từng nhận định. Không cần thì bỏ trường này, không tự tạo role assignment.
- Mỗi thuộc tính khẳng định phải có Claim; unknown là thiếu dữ liệu, không phải persona mặc định. Business stage không hàm ý buying committee hay customer ecosystem.
- AudienceContext là view ngữ cảnh của CustomerIdentity, gồm context, situation và các claim về trigger/task/constraints/channel khi có nguồn; không có role_assignments hoặc ecosystem_roles.
- Tên năm field đã ACCEPTED (DEC-020); chi tiết kiểu dữ liệu/validation vẫn PROPOSED (DEC-012); phạm vi B2C-first là ACCEPTED (DEC-019).

## CustomerSignal

- source_ref; spans[]; audience_context_ref; signal_kind; normalized_claim; derivation.
- signal_kind dự kiến: JOB, PAIN, GAIN, CONTEXT, BEHAVIOR, LANGUAGE; đây là vocabulary đề xuất, không ép loại trừ nhau.
- Cardinality: SourceRecord có 0..n CustomerSignal; mỗi signal gắn một source comment và ít nhất một span kiểm được. Signal cần nhiều comment được mô hình thành nhiều signal rồi nhóm ở Pattern.
- Span giữ lời gốc OBSERVED. normalized_claim diễn giải ngữ nghĩa dùng DERIVED hoặc HYPOTHESIS đúng mức; không mặc định toàn bộ signal là OBSERVED.
- Không có mapping tự động `bucket → customer truth`. Nhiều signal có thể dùng cùng span nhưng không được đếm thành nhiều nguồn.

## Pattern — generic design; executable Phase 3 contract ở đầu tài liệu

- signal_refs[]; grouping_claim; derivation; inclusion_rule; exclusion_rule.
- sample_scope; source_refs[]; distinct_comment_count; distinct_author_count?; signal_count.
- counter_signal_refs[]; coverage_limitations[]; support_policy_ref.
- distinct_comment_count = số SourceRecord phân biệt sau dedup; signal_count là đại lượng khác. Không có author identity đủ tin cậy thì distinct_author_count = null.
- Mô tả tính lặp lại cần nhiều source comment khác nhau và tiêu chuẩn support đã review. Một nguồn đơn lẻ không chứng minh recurring pattern; chỉ giữ làm candidate hoặc trường hợp riêng. Không mặc định min_support=3 hay coi score engagement là bằng chứng thị trường.

## Evidence và Insight

Evidence:

- target_claim_id; source_ref; spans[] hoặc metadata_refs[]; relation: SUPPORTS / CONTRADICTS / CONTEXT.
- relevance_claim; validation_status; checked_at; validation_method; limitations[].
- Quote là OBSERVED; nhận định rằng quote hỗ trợ kết luận là DERIVED và cần lý do. Evidence không biến phát biểu chủ quan thành fact khách quan.

Insight:

- claims[]; pattern_refs[]; evidence_refs[]; derivation; scope; counter_evidence_refs[]; limitations[]; review_status.
- Insight DERIVED có evidence hợp lệ và trace tới comment cho từng claim. Insight HYPOTHESIS phải có validation_plan và bị loại khỏi factual claims gửi Writer.
- Insight từ một trường hợp phải ghi rõ scope cá biệt; không buộc chế tạo pattern lặp để điền schema.
- Nếu không tìm thấy phản chứng, ghi search_scope và trạng thái NOT_FOUND/NOT_CHECKED; không tuyên bố không tồn tại phản chứng.

CustomerProfile:

- jobs[], pains[], gains[] là ClaimRef hoặc InsightRef; identity_ref; context_ref; sample_scope; limitations[].
- Có thể chứa giả thuyết được gắn nhãn riêng; view xuất cho Writer chỉ giữ claim đủ điều kiện. Không có phép nhập persona/config trực tiếp thành customer facts.

## Topic, Angle và HumanSelection

Topic: insight_refs[1..n], proposed_claim, audience_context_ref, editorial_goal. proposed_claim dùng PROPOSED, không thêm customer fact.

Angle: topic_ref, insight_refs[1..n], framing, rationale, allowed_claim_refs[], proposed_hook?, proposed_outline?; truth_type = PROPOSED. Hook/outline là đề xuất định hướng sau insight, chưa phải final content; không áp số từ/regex của V1.

HumanSelection: angle_ref, reviewed_input_refs[], decision (APPROVED / REJECTED / NEEDS_REVIEW), selected_by (human identity), selected_at, review_note?. MachineRecommendation là record riêng, không được dùng làm HumanSelection APPROVED. Thay đổi Angle/claim/evidence nền tảng làm lựa chọn cũ stale và cần review lại.

## ContentIntelligencePacket

| Field | Kiểu/điều kiện |
|---|---|
| packet_type | literal ContentIntelligencePacket |
| schema_version, packet_id, packet_version | Định danh hợp đồng và snapshot |
| selection | HumanSelection APPROVED, đúng Angle version |
| audience_context, customer_profile | Snapshot có Claim và nhãn, giới hạn theo scope |
| topic, angle, insights[] | Snapshot các tầng đã duyệt, có liên kết ngược |
| evidence[], sources[] | Snapshot evidence và source excerpt/canonical text đủ kiểm span/metadata; không cần raw riêng tư ngoài phạm vi |
| allowed_customer_claims[] | Claim OBSERVED hoặc DERIVED đủ trace, không bao gồm giả thuyết |
| research_hypotheses[] | Claim HYPOTHESIS riêng, đánh dấu không được dùng làm factual copy |
| allowed_quotes[], allowed_numbers[] | Quote có span; số có unit, scope, timestamp, nguồn hoặc công thức/input refs |
| brand_context | BrandFact[] riêng với source_kind/verification status; không giả làm comment khách |
| editorial_brief | Mục tiêu, kênh, format, CTA đề xuất; không thêm offer fact chưa được xác minh |
| voice_rules, writing_constraints | Nội dung snapshot và version/hash nguồn; không chỉ là đường dẫn ngoài |
| provenance_manifest, validation | Kiểm ref/version/hash, eligibility, stale selection và kết quả kiểm hợp đồng |

Array có thể rỗng nếu không áp dụng, trừ insights, allowed_customer_claims và bằng chứng của chúng phải không rỗng. Contract thiếu trường bắt buộc, ref đứt, quote sai, unknown schema version hoặc selection stale phải bị từ chối; không tự điền từ V1/config. Quy tắc handoff chi tiết ở [04-CONTENT-CONTRACT.md](04-CONTENT-CONTRACT.md).

WriterResult dự kiến: packet_ref, content, truth_type=PROPOSED cho tác phẩm, claim_usage[] (output span → allowed claim/quote/number refs), validation_findings[], status (REVIEW_REQUIRED / REJECTED / READY_FOR_REVIEW). Nhãn PROPOSED của tác phẩm không cho phép bịa factual claim bên trong. Đây không phải lệnh publish.
