# 02 — DATA SCHEMA

## Phase 1 — schema đã triển khai, chờ architect review

`signal_models.py` định nghĩa `SignalsEnvelope` với `schema_version="v2.signals.1"`, `generated_at` UTC, model đã resolve, `prompt_version="phase1.extractive.1"`, `derivation_method="source_span_categorization"`, records[] và issues[]. Không phụ thuộc classified.json.

Mỗi record gồm comment_id, source, signals[] và extraction_status (ok/no_signal/partial/error), issues[]. Mỗi signal có category/subcategory, claim, truth_type **chỉ OBSERVED hoặc DERIVED**, evidence_quote, confidence high/medium/low, signal_id, source_record_id, source_snapshot_hash, start/end. Offset nửa mở theo Unicode code point trong source.text gốc. LANGUAGE cũng dùng record có kiểu để giữ cùng provenance, không chỉ chuỗi rời.

Taxonomy thực thi:

| category | subcategory |
|---|---|
| jobs | functional, social, emotional, supporting |
| pains | negative_outcomes, obstacles, risks_fears, costs, frustrations |
| gains | required, expected, desired, unexpected |
| behavior | trigger, current_solution, alternatives, workarounds, decision_criteria, objections |
| language | exact_phrases, emotional_wording, repeated_expressions |

Khác ví dụ conceptual: dùng danh sách signal phẳng có category/subcategory thay các mảng lồng nhau; mảng rỗng nghĩa không tìm thấy signal. Không thêm AudienceContext/CustomerIdentity hoặc CONTEXT category trong Phase 1. Segmentation thuộc Phase 2. Generic schema phía dưới vẫn là thiết kế tương lai; không yêu cầu HYPOTHESIS, audience_context_ref, Pattern hoặc Insight để chạy Phase 1.

Lựa chọn triển khai bảo thủ, chờ review: claim giữ cùng lời nguồn với evidence_quote (cho phép chuẩn hóa whitespace ở semantic claim). DERIVED biểu diễn phép diễn giải khi gán category/subcategory, không sinh paraphrase tự do. Ví dụ claim được viết lại trong yêu cầu conceptual sẽ bị từ chối nếu thêm/đổi lời nguồn; không tự thay claim lỗi thành claim hợp lệ. Đây là giới hạn có chủ đích để quote hợp lệ không che một kết luận bịa demographics/motivation/context. LANGUAGE giữ nguyên tuyệt đối cả whitespace của đoạn nguồn.

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

## Pattern

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
