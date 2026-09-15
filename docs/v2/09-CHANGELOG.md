# 09 — CHANGELOG

## 2026-09-15 — Phase 1.1 Signal Extraction Quality Patch

- Bỏ model-generated claim khỏi candidate transport; code tạo claim nguyên văn sau source-span validation.
- Giữ validation quote/ID, source hash/span, truth types, multi/zero-signal và legacy default. Không sửa quote không hợp lệ để tăng acceptance.
- Output schema vẫn v2.signals.1; prompt version phase1.extractive.2; reader đọc được artifact phase1.extractive.1.
- Full suite: 130 passed. Thêm test transport không có claim, exact code-generated claim, artifact cũ và không suy repetition xuyên comment.
- Chạy lại cùng 50 source snapshots/model/thứ tự; metrics trước/sau và artifact 10 comment cục bộ ghi tại PROJECT-STATE. Không commit dữ liệu khách hàng.
- Giữ Phase 1 — PENDING ARCHITECT REVIEW. Không đặt ngưỡng thành công, không mở Phase 2.

## 2026-09-15 — Phase 1 Signal Extraction, pending architect review

- Thêm V2 models/extractor và CLI opt-in extract-signals, không cần classified.json.
- Typed Jobs/Pains/Gains/Behavior/Language, claim-level OBSERVED/DERIVED, exact evidence spans, source hashes, nullable metrics và extraction status/issues.
- Code hậu kiểm quote/claim/ID, giữ valid claims khi item lỗi; structured JSON không thay validation.
- Test offline fixture tổng hợp và regression classifier cũ; kết quả full suite/mẫu 50 comment tại PROJECT-STATE.
- Cập nhật phase gate, schema, evidence rules và DEC-021/022; user authorization cho Phase 1 không mở Phase 2.
- Không đổi legacy default runtime, không thay Reelo hoặc triển khai tầng tiếp theo.

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
