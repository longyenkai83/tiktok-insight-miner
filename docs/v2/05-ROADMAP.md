# 05 — ROADMAP

Current Phase = Phase 0

Status = ARCHITECTURE DOCUMENTATION

Next Phase = Phase 1 Signal Extraction

Do not start Phase 1 without review.

Phase 0 là phạm vi hiện tại. Tên Phase 1 theo chỉ thị chủ dự án; cách chia Phase 2 trở đi dưới đây là PROPOSED, không phải cam kết triển khai được duyệt. Thứ tự phase triển khai không thay đổi thứ tự dữ liệu trong [01-ARCHITECTURE.md](01-ARCHITECTURE.md).

| Phase | Phạm vi dự kiến | Điều kiện đầu ra cho review | Trạng thái |
|---|---|---|---|
| 0 — Architecture Documentation | Mười tài liệu, chỉ dẫn agent, existing tests, commit/push tài liệu | Đủ nguyên tắc, schema/contract dự kiến, runtime không đổi | CURRENT |
| 1 — Signal Extraction | Source/provenance tối thiểu, context đầu vào có nhãn, tách nhiều signals/comment | Quote trace, nhiều signal/không signal, unknown context và lỗi có kiểm chứng | NOT STARTED |
| 2 — Audience / Role / Context | Customer Identity B2C: audience_segment, context, situation, `life_or_business_stage` khi liên quan; view Jobs/Pains/Gains | Phân biệt self-report/suy luận/giả thuyết; `user_buyer_distinction` (optional) chỉ khi cần, không có ecosystem B2B | PROPOSED — NOT STARTED |
| 3 — Pattern | Nhóm signals có scope, dedup và support policy đã review | Đếm nguồn phân biệt, giải thích grouping, giữ ngoại lệ | PROPOSED — NOT STARTED |
| 4 — Evidence / Insight | Tổng hợp evidence, phản chứng và insight có truy vết | Claim-level truth types, không có insight DERIVED mất source | PROPOSED — NOT STARTED |
| 5 — Topic | Tổ chức insight đủ điều kiện thành chủ đề biên tập | Không tạo customer truth mới, chưa tạo final content | PROPOSED — NOT STARTED |
| 6 — Angle / Human Selection | Đề xuất góc và người duyệt phiên bản | Máy không giả human approval; thay input làm stale selection | PROPOSED — NOT STARTED |
| 7 — Content Intelligence Packet | Typed contract, snapshot, kiểm provenance và eligibility | Packet hợp lệ/không hợp lệ được nhận/từ chối đúng | PROPOSED — NOT STARTED |
| 8 — Reelo Writer | Đọc packet, tạo draft, claim_usage và feedback | Không bịa truth, không bypass contract bằng legacy path | PROPOSED — NOT STARTED |
| 9 — Unified Agent | Điều phối toàn chuỗi và human gates | Resume/error trace, không vượt approval, không tự publish | PROPOSED — NOT STARTED |

## Gate mở Phase 1

Chủ dự án review bộ tài liệu Phase 0 và cho phép bắt đầu Phase 1 rõ ràng. Trước khi code: chốt schema/phạm vi tối thiểu của Source, Context và CustomerSignal; nguồn fixture được phép; hành vi khi thiếu nguồn; kế hoạch bảo toàn V1 và nghiệm thu. Ghi kết quả review vào DECISIONS và PROJECT-STATE. Không lấy việc merge/push docs hoặc existing tests xanh làm chấp thuận Phase 1.

Phase 1 chưa cần triển khai Pattern/Insight/Writer. Nhưng phải lưu provenance ngay từ đầu; không trì hoãn source IDs/spans tới Phase 4. Context thiếu được biểu diễn unknown/HYPOTHESIS, không tự tạo facts để signal extractor chạy.

## Các quyết định chưa chốt

Model, SDK, batch size, prompt, taxonomy chi tiết, score/clustering, min_support, file/database, UI/CLI, transport Reelo, adapter legacy và migration chưa được chọn. Không giả định thêm `tim signals`, gộp exporter, đổi suggester, hoặc dùng production.py làm Writer tạm. Các việc đó cần thiết kế và phạm vi review riêng.

Mỗi phase sau có review đầu vào, nghiệm thu và quyết định tiếp tục riêng. Không tự chạy phase kế tiếp sau khi hoàn thành phase trước. Phase 0 dừng sau tài liệu, test hiện có, commit, push và báo cáo kết quả.
