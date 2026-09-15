# 04 — CONTENT CONTRACT

## Phase 5 — implemented downstream eligibility boundary, no generation

Future Content Research must first pass require_verified(verified_envelope, current_reviews).
Phase 4 candidates, bare human_verified=true objects, stale/revoked projections and altered
evidence cannot enter. The caller obtains the current ledger from trusted authoritative storage.
Verified Insight still requires downstream Content Opportunity → Topic → Angle → Human Selection
→ typed Content Intelligence Packet before Reelo. Human Insight approval does not replace
Angle selection or validate market/purchase behavior. No packet/Writer integration here.

Future Customer Profile updates may PROPOSE add / merge / supersede / archive; human approval
is required for supersession. Preserve legacy Reelo's useful dedupe/provenance/conflict behavior,
but do not implement living profile merge or direct Reelo ingestion in Phase 5.

## Phase 4.1 — future Human Governor prerequisite

The shared engine emits Insight Candidates. Phase 5 Human Approval must first produce a
human-verified insight before Content Research/Topic/Angle/Human Selection/typed packet.
Machine acceptance cannot replace this semantic gate or the later Angle selection gate.
See Source/Downstream Router paths in [11](11-BUSINESS-OS-NORTH-STAR.md). No handoff runtime here.

## Phase 4 architecture memory — future direct transport

DEC-039 selects typed direct Reelo ingestion/API or equivalent structured handoff.
Drive remains legacy compatibility/backup, not the primary V2 bridge. Retain this
contract's Topic/Angle/Human Selection and allowed-claim gates, dedupe/supersession/
provenance and human approval for replacing contradictory customer knowledge.
No Reelo integration is implemented in Phase 4; insights.json is not itself a Content
Intelligence Packet and pending_human_review candidates are not Writer-ready facts.

## Quy tắc đã chốt và phạm vi đề xuất

Insight → Reelo bắt buộc dùng typed Content Intelligence Packet. Content chỉ được tạo sau Insight; Angle/Topic là các đề xuất biên tập sau Insight, Human Selection nằm sau Angle. Writer được sáng tạo cách diễn đạt, không sáng tạo customer truth. Đây là nguyên tắc ACCEPTED; cấu trúc serialize, lỗi và kết quả cụ thể dưới đây là PROPOSED cho review, chưa được cài vào runtime.

Contract dữ liệu nằm tại [02-DATA-SCHEMA.md](02-DATA-SCHEMA.md); provenance theo [03-EVIDENCE-RULES.md](03-EVIDENCE-RULES.md). Markdown là view cho người đọc, không là schema trao đổi chuẩn. Không coi `selected_angles.json`, brief Markdown hay pack Drive hiện tại là packet V2 chỉ bằng cách đổi tên.

## Vị trí trong kiến trúc hai mode

Theo DEC-024/025, shared engine chạy Source → Normalized Evidence → Signal Extraction → Customer Context → Pattern Engine → Evidence Engine → Insight Candidate → Phase 5 Human Approval → Verified Insight. Content contract áp dụng cho nhánh Verified Insight → Content Opportunity → Topic → Angle → Human Selection → Packet → Reelo Writer.

Product Discovery dùng cùng evidence-backed engine nhưng có chuỗi Opportunity Area/Value Map/Assumptions/Experiments/Evidence/Decision riêng. Không dùng Writer hoặc human content selection để xác nhận product demand. Chi tiết ở 01/07; cả hai downstream mode chưa triển khai trong Phase 2.

## Content Intelligence Packet: điều kiện bàn giao

Packet là snapshot bất biến có `packet_type`, `schema_version`, `packet_id`, `packet_version`. Nó mang nội dung đủ để Writer kiểm hiểu độc lập: Topic, Angle, Insight, Evidence, source excerpts, context, profile, human approval, allowed claims/quotes/numbers, brand context riêng và voice/writing rules đã snapshot. Ref ngoài chỉ phục vụ truy xuất nguồn sâu hơn, không thay nội dung bắt buộc.

Mỗi claim phải truy tới source comment; metric và quote không bị cắt âm thầm. Source excerpt phải đủ vùng context để không làm sai nghĩa. Không đóng gói toàn bộ raw riêng tư nếu không cần. Hash/version giúp nhận ra chỉnh sửa, không thay kiểm chứng nội dung nguồn.

Human approval gắn với exact Angle và các input versions. Nếu nội dung bằng chứng, insight, Angle hoặc giới hạn claim thay đổi thì selection cũ không còn đủ; packet mới phải được review lại. Máy không được chuyển `selected_by=auto` sang human hoặc tạo approval mặc định. Lựa chọn legacy chỉ là dữ liệu đầu vào cần đối chiếu, không kế thừa quyền approved V2.

## Writer được và không được làm

Writer được đổi bố cục, nhịp, hook, ví dụ minh họa phi thực chứng được ghi rõ, ẩn dụ và cách giải thích; không bắt buộc copy tối thiểu năm từ hoặc giữ regex V1. Mọi diễn đạt phải giữ nguyên nghĩa, attribution, scope và độ chắc chắn của claim được phép.

Writer không được tạo thêm pain, job, gain, audience segment, `user_buyer_distinction` (optional), động cơ, số liệu, lời khách, case thực tế hoặc kết quả sản phẩm. Không làm câu “một comment phản ánh” thành “khách hàng đều gặp”. Không biến research_hypotheses thành fact bằng cách bỏ nhãn. Giọng thương hiệu và config chỉ điều khiển diễn đạt, không xác thực customer truth.

Brand fact/offer/giá chỉ được dùng nếu có nguồn riêng đã kiểm và được cho phép trong packet; nếu thiếu, trả yêu cầu bổ sung. Không mặc định cấm toàn bộ commercial content theo prompt V1, cũng không tự phát minh offer để điền CTA.

## Từ chối và vòng phản hồi

Các mã lỗi dự kiến: UNSUPPORTED_SCHEMA, BROKEN_PROVENANCE, INVALID_QUOTE, INVALID_NUMBER, UNAPPROVED_SELECTION, STALE_SELECTION, UNSUPPORTED_CLAIM, MISSING_CONTEXT. Một lỗi phải chỉ ra record/claim và lý do; không silently downgrade, lấy persona bù hoặc dùng production V1 làm fallback.

Nếu chỉ sai diễn đạt, Writer sửa trong phạm vi packet rồi kiểm lại. Nếu thiếu customer truth, dừng và trả về research/evidence; không viết để lấp chỗ trống. WriterResult mang claim_usage (span nội dung → claim/quote/number refs), findings và trạng thái chờ review. Không tuyên bố PASS chỉ vì hoàn thành một lượt rewrite, và không tự publish.

Unified Agent trong thiết kế tương lai quản lý run/step state, provenance, lỗi, resume và các human gate. Cơ chế orchestration, retry, storage, transport và giới hạn rewrite vẫn OPEN; không kế thừa mặc định vòng sửa của Reelo/V1. Việc audit đã được duyệt không cấp quyền chạy Agent V2.
