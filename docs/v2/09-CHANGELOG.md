# 09 — CHANGELOG

## 2026-09-15 — Chuẩn hóa tên field Customer Identity

- DEC-020 chốt `audience_segment`, `context`, `situation`, `life_or_business_stage`, `user_buyer_distinction` (optional).
- Đồng bộ tài liệu hiện hành, thay hai field stage riêng bằng một field thống nhất. Không thay runtime, không mở Phase 1.

## 2026-09-15 — Architecture correction: B2C-first

- DEC-019 thay DEC-004: "V2 is B2C-first. Do not introduce B2B complexity unless explicitly approved later."
- Loại logic hệ sinh thái B2B khỏi target, schema, contract, roadmap và tiêu chí nghiệm thu.
- Customer Identity V2 tập trung audience_segment, context, situation, life/business stage khi liên quan; user/buyer chỉ khi use case B2C thực sự cần.
- Giữ lịch sử quyết định cũ dưới trạng thái SUPERSEDED. Mục lịch sử bên dưới không còn xác định phạm vi B2B hiện hành.
- Chỉ thay tài liệu. Giữ Phase 0, không bắt đầu Phase 1, không đổi runtime.

## 2026-09-15 — Phase 0: V2 architecture documentation

- Chuẩn hóa bộ mười tài liệu source-of-truth `00`–`09`; tách baseline CURRENT STATE khỏi target architecture V2.
- Ghi chuỗi Source → Audience / Role / Context → Customer Signals → Pattern → Evidence → Insight → Topic → Angle → Human Selection → Content Intelligence Packet → Reelo Writer → Unified Agent.
- Ghi đủ mười quyết định bắt buộc; thống nhất OBSERVED / DERIVED / HYPOTHESIS / PROPOSED theo claim.
- Đề xuất schema/contract cho multi-signal, Jobs/Pains/Gains + Context, Customer Ecosystem Role, evidence trace, human approval và typed packet.
- Quy định Writer chỉ sáng tạo cách diễn đạt, không tạo customer truth; không nhận legacy selected_angles làm schema V2.
- Cập nhật CLAUDE.md và AGENTS.md: mọi coding agent phải đọc đủ docs/v2 trước sửa code, tuân phase gate.
- Giữ Current Phase = Phase 0; Status = ARCHITECTURE DOCUMENTATION; Next Phase = Phase 1 Signal Extraction; Do not start Phase 1 without review.
- Không sửa runtime, business logic, pipeline, prompt hoặc tests. Kết quả existing tests ghi tại PROJECT-STATE; định danh commit và xuất bản tra bằng Git.

Đây là thay đổi tài liệu, không là release feature V2 hay chấp thuận Phase 1. Bản nháp cũ được sao lưu cục bộ trong thư mục output của dự án trước khi chuẩn hóa; không đưa bản sao đó vào Git.
