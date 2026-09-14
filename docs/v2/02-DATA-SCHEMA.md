# 02 — DATA SCHEMA

## Phạm vi

Đây là hợp đồng thiết kế, không phải schema executable đã triển khai. Các nguyên tắc trong DEC-001–010 là ACCEPTED theo yêu cầu; tên field và bố cục dưới đây là PROPOSED để review trước triển khai. Không phụ thuộc Pydantic/JSON Schema/V1. Dùng thống nhất `truth_type ∈ {OBSERVED, DERIVED, HYPOTHESIS, PROPOSED}`.

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

- CustomerIdentity: `audience_segment`, `context`, `situation`; `life_stage?`, `business_stage?` chỉ khi liên quan tới use case B2C.
- `user_buyer_distinction?`: chỉ xuất hiện khi cần phân biệt người dùng và người mua trong use case B2C; kèm use_case_reason và Claim có nguồn cho từng nhận định. Không cần thì bỏ trường này, không tự tạo role assignment.
- Mỗi thuộc tính khẳng định phải có Claim; unknown là thiếu dữ liệu, không phải persona mặc định. Business stage không hàm ý buying committee hay customer ecosystem.
- AudienceContext là view ngữ cảnh của CustomerIdentity, gồm context, situation và các claim về trigger/task/constraints/channel khi có nguồn; không có role_assignments hoặc ecosystem_roles.
- Chi tiết field vẫn PROPOSED (DEC-012); phạm vi B2C-first là ACCEPTED (DEC-019).

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
