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

Theo architecture correction trực tiếp của chủ dự án, quyết định này supersedes DEC-004. Customer Identity V2 tập trung `audience_segment`, `context`, `situation`, life/business stage khi liên quan và user/buyer distinction chỉ khi use case B2C thực sự cần.

Loại khỏi target: economic buyer, decision committee, channel partner, recommender, saboteur và mọi B2B-specific customer ecosystem logic. Từ Role trong DEC-011 chỉ còn phạm vi user/buyer tùy chọn của B2C; không phải taxonomy vai trò tổ chức. Không bổ sung schema hoặc roadmap B2B khi chưa được phê duyệt rõ ràng. Phase 0 và các quy tắc bằng chứng không đổi.

## Chưa quyết định — không được coi là quyền triển khai

| ID | Trạng thái | Nội dung cần review |
|---|---|---|
| DEC-012 | PROPOSED | Field schema Customer Identity B2C, enum signals, nullable fields, định dạng snapshot/offset, lỗi contract và WriterResult trong 02–04 |
| DEC-016 | OPEN | Model/prompt/SDK, thuật toán clustering/ranking, ngưỡng support, sampling/dedup policy |
| DEC-017 | OPEN | Storage, transport Reelo, UI/CLI, orchestrator, retry/rewrite, adapter/migration legacy |
| DEC-018 | PROPOSED | Cách chia Phase 2–9 và tiêu chí tương lai; cần review từng phase |

Không quyết định kế thừa auto-top, regex checkbox/hook V1, số từ hook, score likes, default model, thư mục Drive, production.py fallback hoặc gộp exporter. Chúng là hiện trạng/khả năng cân nhắc, không là kiến trúc đích đã được chấp thuận.

## Quy trình thay quyết định

Ghi ID mới hoặc supersedes ID cũ, lý do, bằng chứng, ảnh hưởng contract/migration, phạm vi được duyệt và ngày/người review. Không sửa lịch sử để biến proposal thành accepted. Cập nhật PROJECT-STATE và CHANGELOG khi có review mở phase; commit/push tài liệu không tự mở Phase 1.
