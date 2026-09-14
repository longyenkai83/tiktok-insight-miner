# 09 — CHANGELOG

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
