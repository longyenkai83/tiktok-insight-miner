# 07 — DECISIONS

Ngày ghi nhận: 2026-09-15. ACCEPTED là quyết định thiết kế theo chỉ thị trực tiếp của chủ dự án, không có nghĩa đã triển khai. PROPOSED/OPEN dưới đây là trạng thái quyết định, khác với truth_type của customer claim.

## Quyết định nền tảng — ACCEPTED, trừ mục đã SUPERSEDED

| ID | Quyết định | Lý do và hệ quả thiết kế |
|---|---|---|
| DEC-001 | **7-bucket classification không còn là backbone V2.** | Bucket đơn không biểu diễn đầy đủ tiếng nói khách; V2 đặt Customer Signals và evidence làm nền. V1 hiện vẫn giữ nguyên runtime. |
| DEC-002 | **Một comment có thể có nhiều customer signals.** | Jobs, pains, gains và context có thể đồng hiện; cho phép 0..n signals, đếm source khác đếm signal. |
| DEC-003 | **Customer Profile dùng Jobs / Pains / Gains + Context.** | Profile là tổng hợp có provenance, không phải persona được điền sẵn rồi coi là fact. |
| DEC-004 | **SUPERSEDED bởi DEC-019.** | Quyết định cũ về hỗ trợ B2B Customer Ecosystem Role bị rút khỏi target V2 theo architecture correction của chủ dự án; chỉ giữ dấu vết lịch sử. |
| DEC-005 | **Mọi derived insight phải trace về source comment.** | Claim DERIVED phải phân giải qua evidence/source snapshot; summary AI hoặc config không thay comment. |
| DEC-006 | **Meta-pain/persona/config không được tự biến thành observed customer truth.** | Chỉ là giả định hoặc định hướng có nhãn cho đến khi có bằng chứng thích hợp; confidence và approval không nâng nhãn. |
| DEC-007 | **Content chỉ được tạo sau insight layer.** | Topic/Angle dựa trên insight đủ điều kiện; không có đường tắt raw/config → Writer trong target V2. |
| DEC-008 | **Insight → Reelo phải dùng typed Content Intelligence Packet.** | Packet có version, evidence và human approval; Markdown pack tự do không đủ bảo toàn contract. |
| DEC-009 | **selected_angles hiện tại là legacy naming và không được dùng làm schema chuẩn V2.** | Audit cho thấy đó là selected comment records. Adapter nếu có cần mapping và review riêng; đổi tên không tạo semantics V2. |
| DEC-010 | **Writer được sáng tạo cách diễn đạt, không được sáng tạo customer truth.** | Giữ claim/quote/số liệu/scope/attribution; không có ngoại lệ cho phần trăm “tu từ” hoặc case bịa. |

## Ràng buộc bổ sung — ACCEPTED theo phạm vi yêu cầu

- DEC-011: Chuỗi đích là Source → Audience / Role / Context → Customer Signals → Pattern → Evidence → Insight → Topic → Angle → Human Selection → Content Intelligence Packet → Reelo Writer → Unified Agent. Audit chỉ là CURRENT STATE.
- DEC-013: Truth types bắt buộc OBSERVED, DERIVED, HYPOTHESIS, PROPOSED. Nhãn ở mức claim; approval nghiệp vụ không làm thay nhãn bằng chứng.
- DEC-014: Giữ Phase 0 / ARCHITECTURE DOCUMENTATION. Không sửa business logic, refactor pipeline hay bắt đầu Phase 1 khi chưa review. Chỉ tài liệu, chỉ dẫn agent, existing tests, commit và push trong lần bàn giao này.
- DEC-015: Human Selection là gate thực sự trong kiến trúc đích. Máy có thể gợi ý, không tự ghi lựa chọn máy thành người duyệt. Cơ chế lưu danh tính/approval/version là chi tiết cần review.

## DEC-019 — B2C-first — ACCEPTED

**"V2 is B2C-first. Do not introduce B2B complexity unless explicitly approved later."**

Theo architecture correction trực tiếp của chủ dự án, quyết định này supersedes DEC-004. Customer Identity V2 tập trung `audience_segment`, `context`, `situation`, `life_or_business_stage` khi liên quan và `user_buyer_distinction` (optional) chỉ khi use case B2C thực sự cần.

Loại khỏi target: economic buyer, decision committee, channel partner, recommender, saboteur và mọi B2B-specific customer ecosystem logic. Từ Role trong DEC-011 chỉ còn phạm vi `user_buyer_distinction` (optional) tùy chọn của B2C; không phải taxonomy vai trò tổ chức. Không bổ sung schema hoặc roadmap B2B khi chưa được phê duyệt rõ ràng. Phase 0 và các quy tắc bằng chứng không đổi.

## DEC-020 — Customer Identity field names — ACCEPTED

Theo xác nhận trực tiếp của chủ dự án, tên field chuẩn là `audience_segment`, `context`, `situation`, `life_or_business_stage`, `user_buyer_distinction` (optional). Dùng một field `life_or_business_stage` thống nhất. Đây là cập nhật tên field trong DEC-012/019; kiểu dữ liệu và validation chi tiết vẫn cần review. Không mở Phase 1.

## DEC-021 — Cho phép Phase 1 độc lập — ACCEPTED

Yêu cầu trực tiếp “PHASE 1 — SIGNAL EXTRACTION” của chủ dự án chỉ định base `v2-phase-0@dd5c945`, branch `v2-phase-1-signal-extraction` và phạm vi raw Comment → multi-signal customer evidence. Đây là authorization mở Phase 1, thay giới hạn tài liệu-only của DEC-014; không phải tự mở phase từ test/push. Chỉ OBSERVED/DERIVED trong Phase 1; không HYPOTHESIS/PROPOSED, không Audience/context segmentation (Phase 2), không các tầng sau. Model resolution riêng, CLI riêng và legacy default giữ nguyên.

## DEC-022 — Hình thức schema Phase 1 — IMPLEMENTED, PENDING ARCHITECT REVIEW

Flat typed signal list; LANGUAGE cũng mang claim/quote/provenance. Hậu kiểm từng item sau structured JSON, lưu source hash/spans. Claim extractive giữ lời quote để không chấp nhận paraphrase thêm facts chỉ vì quote có thật; DERIVED là interpretation khi categorization. Đây là lựa chọn implementation bảo thủ cần review, không tuyên bố kiến trúc sư đã duyệt chi tiết. Giới hạn và khác ví dụ conceptual ghi tại 02/03. Không mở Phase 2.

## DEC-023 — Phase 1.1 transport không sinh claim — ACCEPTED scope, pending architect review

Theo yêu cầu trực tiếp Phase 1.1, candidate chỉ trả category/subcategory/evidence_quote/truth_type/confidence. Code tạo final claim từ exact validated source span; không chữa quote sai hoặc nhận paraphrase. Giữ source spans/hashes, OBSERVED/DERIVED, status/issues, multi/zero-signal và legacy compatibility. Thay phần model-generated claim trong implementation DEC-022; không thay quy tắc grounding. Chạy lại đúng mẫu 50 source snapshot và review định tính cục bộ, không đặt ngưỡng thành công số học. repeated_expressions chỉ là lặp trong một comment; corpus repetition để Pattern phase. Không mở Phase 2.

## Chưa quyết định — không được coi là quyền triển khai

| ID | Trạng thái | Nội dung cần review |
|---|---|---|
| DEC-012 | PROPOSED | Kiểu dữ liệu/validation Customer Identity B2C (tên field đã chốt tại DEC-020), enum signals, nullable fields, định dạng snapshot/offset, lỗi contract và WriterResult trong 02–04 |
| DEC-016 | OPEN | Model/prompt/SDK, thuật toán clustering/ranking, ngưỡng support, sampling/dedup policy |
| DEC-017 | OPEN | Storage, transport Reelo, UI/CLI, orchestrator, retry/rewrite, adapter/migration legacy |
| DEC-018 | PROPOSED | Cách chia Phase 2–9 và tiêu chí tương lai; cần review từng phase |

Không quyết định kế thừa auto-top, regex checkbox/hook V1, số từ hook, score likes, default model, thư mục Drive, production.py fallback hoặc gộp exporter. Chúng là hiện trạng/khả năng cân nhắc, không là kiến trúc đích đã được chấp thuận.

## Quy trình thay quyết định

Ghi ID mới hoặc supersedes ID cũ, lý do, bằng chứng, ảnh hưởng contract/migration, phạm vi được duyệt và ngày/người review. Không sửa lịch sử để biến proposal thành accepted. Cập nhật PROJECT-STATE và CHANGELOG khi có review mở phase; commit/push tài liệu không tự mở Phase 1.
