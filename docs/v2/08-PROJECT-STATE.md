# 08 — PROJECT STATE

Current Phase = Phase 0

Status = ARCHITECTURE DOCUMENTATION

Next Phase = Phase 1 Signal Extraction

Do not start Phase 1 without review.

## Trạng thái thực tế

- Audit CURRENT STATE đã được chủ dự án chấp nhận; baseline và hash ở [00-PROJECT-OS.md](00-PROJECT-OS.md).
- Bộ source-of-truth V2 `00`–`09` được chuẩn hóa cho review, cùng quy tắc đọc docs trong CLAUDE.md/AGENTS.md.
- Architecture correction đã được ghi nhận: V2 B2C-first, DEC-019 thay DEC-004; loại logic hệ sinh thái B2B khỏi target. Customer Identity dùng audience_segment/context/situation, life/business stage khi liên quan; user/buyer chỉ khi cần cho B2C. Chi tiết schema/implementation còn PROPOSED/OPEN.
- V2 Signal Extraction, Pattern, Evidence/Insight, typed packet, Writer integration và Unified Agent: **NOT IMPLEMENTED trong lần thay đổi này**.
- Runtime behavior changed: **NO**. Không sửa business logic, pipeline, prompt, runtime config hoặc tests.
- Chưa có review cho phép bắt đầu Phase 1. Sau bàn giao phải STOP.

## Kiểm chứng bàn giao

Architecture correction chỉ sửa tài liệu; kiểm link và diff, không đổi runtime. Kết quả test dưới đây thuộc lần bàn giao Phase 0 trước correction, không phải lần chạy mới.

- Lệnh: `python -m pytest tests -q -p no:cacheprovider --basetemp output/v2-phase0-pytest-temp`.
- Kết quả ngày 2026-09-15: **90 passed in 0.52s**, Python 3.13.15, pytest 8.4.2.

Existing tests chỉ kiểm regression hiện có, không chứng minh các invariant V2 đã được triển khai. Kiểm phạm vi diff chỉ gồm mười file chuẩn và hai chỉ dẫn root. Branch/commit/push được xác nhận bằng Git và báo trong kết quả bàn giao; không giả lập hash trong tài liệu.

## Việc tiếp theo được phép

Chủ dự án review bộ docs/v2. Chỉ sau khi có quyết định cho phép mới cập nhật state và chuẩn bị Phase 1 Signal Extraction theo gate ở [05-ROADMAP.md](05-ROADMAP.md). Không tạo module, schema executable, prompt, adapter, migration hay thay đổi pipeline để “chuẩn bị sẵn” trong Phase 0.

## Câu hỏi mở

Schema chi tiết, nguồn fixture, chính sách scope/dedup/support, lựa chọn model, storage/transport và UI chưa chốt; xem DEC-012/016/017/018. Đây là việc review tương lai, không cản bàn giao bộ tài liệu Phase 0.
