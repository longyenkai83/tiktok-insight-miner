# 08 — PROJECT STATE

Current Phase = Phase 1 — Signal Extraction

Status = IMPLEMENTED — PENDING ARCHITECT REVIEW

Next Phase = DO NOT START

Do not start Phase 2. Wait for architecture review.

## Phạm vi đã thực hiện

- Base `v2-phase-0@dd5c945`; branch `v2-phase-1-signal-extraction`; được cho phép bằng yêu cầu trực tiếp của chủ dự án (DEC-021).
- signal_models.py + signal_extractor.py: raw Comment → typed multi-signal artifact, quote/ID hậu kiểm, source snapshot/provenance, per-item rejection, status/issues và model resolution riêng.
- CLI `tim extract-signals -i path/to/raw_comments.json [-o path/to/signals.json] [--model MODEL] [--batch-size 10]`. Mặc định signals.json nằm cạnh input. Exit 0 khi complete, exit 2 khi artifact có partial/error/global issue; input/output lỗi exit 1. Không ghi đè chính raw input.
- Default legacy runtime behavior changed: **NO**. Legacy classifier, run, bank/selection, report/brief, selected_angles và Reelo không đổi. Chỉ có execution path opt-in mới.
- Audience/context segmentation, Pattern, Insight, Topic, Angle, Packet, Writer integration, Unified Agent: **NOT IMPLEMENTED** trong Phase 1. Không mở Phase 2.

## Kiểm chứng

- Full suite: `python -m pytest tests -q -p no:cacheprovider` → **127 passed in 1.21s**, Python 3.13.15 / pytest 8.4.2 (2026-09-15).
- 37 test cases mới: 36 cho extractor/CLI/provenance/serialization/error handling và 1 regression classifier. Tất cả dùng fixture tổng hợp/mock; không test nào gọi API thật. 90 existing tests vẫn pass.
- Kiểm `extract-signals --help`, diff whitespace, link tài liệu và phạm vi legacy không đổi.

- Mẫu thật cục bộ: **50 processed; ok=1, no_signal=5, partial=44, error=0; 82 claims rejected**.
- Artifact không commit: `D:/Tuan-CoWork/TUAN-insight-miner/output/v2-phase1-worktree/output/phase1-real-review/signals.json`.
- Tỷ lệ partial cao cần architect review; không tự sửa claim bị loại thành accepted và không coi kết quả này là duyệt chất lượng extraction.

## Giới hạn cần architect review

- Claim extractive, chưa hỗ trợ paraphrase tự do; category/subcategory có thể DERIVED. Không coi substring check là chứng minh mọi phân loại ngữ nghĩa đều đúng.
- Legacy zero thiếu raw proof chuyển null có ghi chú; không khôi phục được thông tin nguồn đã bị adapter trước đây bỏ mất.
- CLI không retry chọn lọc ID/claim lỗi; artifact giữ partial/error để người vận hành review/rerun. Không tự đổi nhãn hoặc lấp bằng config.
- Artifact có source text/metadata riêng tư: chỉ lưu local, không commit. Bộ fixture test là tổng hợp.

STOP. Wait for architecture review. Next Phase = DO NOT START.
