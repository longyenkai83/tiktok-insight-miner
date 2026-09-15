# 05 — ROADMAP

Current Phase = Phase 1 — Signal Extraction

Status = IMPLEMENTED — PENDING ARCHITECT REVIEW

Next Phase = DO NOT START

Do not start Phase 2. Wait for architecture review.

Phase 1 Signal Extraction được chủ dự án cho phép qua DEC-021; hiện đã triển khai và chờ architect review. Tên Phase 1 theo chỉ thị chủ dự án; cách chia Phase 2 trở đi dưới đây là PROPOSED, không phải cam kết triển khai được duyệt. Thứ tự phase triển khai không thay đổi thứ tự dữ liệu trong [01-ARCHITECTURE.md](01-ARCHITECTURE.md).

| Phase | Phạm vi dự kiến | Điều kiện đầu ra cho review | Trạng thái |
|---|---|---|---|
| 0 — Architecture Documentation | Mười tài liệu, chỉ dẫn agent, existing tests, commit/push tài liệu | Đủ nguyên tắc, schema/contract dự kiến, runtime không đổi | COMPLETED |
| 1 — Signal Extraction | Raw source/provenance, nhiều Jobs/Pains/Gains/Behavior/Language signals; không infer audience/context | Quote/ID validation, nhiều/zero signals, status/issues | IMPLEMENTED — PENDING ARCHITECT REVIEW |
| 2 — Audience / Role / Context | Customer Identity B2C: audience_segment, context, situation, `life_or_business_stage` khi liên quan; view Jobs/Pains/Gains | Phân biệt self-report/suy luận/giả thuyết; `user_buyer_distinction` (optional) chỉ khi cần, không có ecosystem B2B | PROPOSED — NOT STARTED |
| 3 — Pattern | Nhóm signals có scope, dedup và support policy đã review | Đếm nguồn phân biệt, giải thích grouping, giữ ngoại lệ | PROPOSED — NOT STARTED |
| 4 — Evidence / Insight | Tổng hợp evidence, phản chứng và insight có truy vết | Claim-level truth types, không có insight DERIVED mất source | PROPOSED — NOT STARTED |
| 5 — Topic | Tổ chức insight đủ điều kiện thành chủ đề biên tập | Không tạo customer truth mới, chưa tạo final content | PROPOSED — NOT STARTED |
| 6 — Angle / Human Selection | Đề xuất góc và người duyệt phiên bản | Máy không giả human approval; thay input làm stale selection | PROPOSED — NOT STARTED |
| 7 — Content Intelligence Packet | Typed contract, snapshot, kiểm provenance và eligibility | Packet hợp lệ/không hợp lệ được nhận/từ chối đúng | PROPOSED — NOT STARTED |
| 8 — Reelo Writer | Đọc packet, tạo draft, claim_usage và feedback | Không bịa truth, không bypass contract bằng legacy path | PROPOSED — NOT STARTED |
| 9 — Unified Agent | Điều phối toàn chuỗi và human gates | Resume/error trace, không vượt approval, không tự publish | PROPOSED — NOT STARTED |

## Gate Phase 1 — đã được chủ dự án mở bằng yêu cầu trực tiếp

Gate này đã được đáp ứng bởi yêu cầu trực tiếp Phase 1, được ghi tại DEC-021. Phạm vi chỉ Source/Signals, fixture tổng hợp cho test, bảo toàn legacy và hậu kiểm nguồn; Audience/Context để Phase 2. Không lấy việc merge/push hoặc existing tests xanh làm chấp thuận phase kế tiếp.

Phase 1 chưa cần triển khai Pattern/Insight/Writer. Nhưng phải lưu provenance ngay từ đầu; không trì hoãn source IDs/spans tới Phase 4. Theo phạm vi Phase 1 đã chốt, không sinh Context hoặc HYPOTHESIS; chỉ giữ metadata nguồn khi có. Segmentation để Phase 2.

## Các quyết định chưa chốt

Phase 1 đã có model resolution, SDK call, batch size, prompt, taxonomy và CLI độc lập như mô tả tại 02/03 và phía dưới. Score/clustering, min_support, storage cho các tầng sau, UI, transport Reelo, adapter legacy và migration vẫn chưa chốt. Không gộp exporter, đổi suggester hoặc dùng production.py làm Writer tạm; các việc đó cần phạm vi review riêng.

Mỗi phase sau có review đầu vào, nghiệm thu và quyết định tiếp tục riêng. Không tự chạy phase kế tiếp sau khi hoàn thành phase trước. Phase 0 dừng sau tài liệu, test hiện có, commit, push và báo cáo kết quả.

Phase 1 dùng lệnh riêng `tim extract-signals -i raw_comments.json [-o signals.json] [--model MODEL] [--batch-size 10]`. Model: explicit → SIGNAL_MODEL → ANTHROPIC_MODEL → claude-opus-4-7 (default hiện có). Không đổi default `run`. Gate tiếp theo: DO NOT START; chờ architect review, không mở Phase 2.
