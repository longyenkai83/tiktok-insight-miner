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

- Phase 1.1 quality patch trên base `8a63f6fbeff25bb9a24a5c33033ff7bc9e279058`, cùng nhánh Phase 1. Candidate không sinh claim; code tạo claim từ exact source span đã hợp lệ. Không nới grounding.
- Full suite: `python -m pytest tests -q -p no:cacheprovider` → **130 passed in 1.55s**, Python 3.13.15 / pytest 8.4.2 (2026-09-15).
- 40 cases mới so với baseline 90: 39 cho extractor/CLI/provenance/serialization/error handling và 1 regression classifier. Tất cả dùng fixture tổng hợp/mock; không test nào gọi API thật. 90 existing tests vẫn pass.
- Kiểm `extract-signals --help`, diff whitespace, link tài liệu và phạm vi legacy không đổi.

### Mẫu thật trước/sau — 50 comment giống nhau

Before lấy từ artifact Phase 1 gốc; After chạy mới với đúng source snapshots, thứ tự, model đã resolve và batch size 10. Không lấy mẫu khác hoặc chạy lại baseline để thay số cũ. Model generation có thể biến thiên; không coi số accepted là thước đo đúng ngữ nghĩa hay đặt ngưỡng thành công.

| Metric | Before | After |
|---|---:|---:|
| ok | 1 | 42 |
| no_signal | 5 | 4 |
| partial | 44 | 4 |
| error | 0 | 0 |
| claims accepted | 1 | 92 |
| claims rejected | 82 | 4 |

| Rejection code | Before | After |
|---|---:|---:|
| invalid_claim | 82 | 0 |
| ungrounded_quote | 0 | 4 |

Không có issue code khác trong hai lần chạy. Bốn quote lỗi vẫn bị từ chối; không sửa cho qua validator. Rejected counts đếm item có item_index; accepted counts đếm signals đã qua validation.

Artifact riêng tư, không commit:

- Before: `output/phase1-real-review/signals.json` (giữ nguyên).
- After/metrics: `output/phase1-quality-review/signals-after.json`, `metrics.json` cùng thư mục.
- Review 10 comment: `D:/Tuan-CoWork/TUAN-insight-miner/output/v2-phase1-worktree/output/phase1-quality-review/phase1-quality-review.md`.

10 comment được chọn có thứ tự theo status transition, coverage category rồi thứ tự input, phục vụ review định tính; không tuyên bố đại diện thống kê. Report giữ source comment, category/subcategory, exact evidence quote, truth_type và issue codes trước/sau. Repeated expressions chỉ trong một comment; corpus-level repetition thuộc Pattern phase sau.

## Giới hạn cần architect review

- Claim extractive, chưa hỗ trợ paraphrase tự do; category/subcategory có thể DERIVED. Không coi substring check là chứng minh mọi phân loại ngữ nghĩa đều đúng.
- Legacy zero thiếu raw proof chuyển null có ghi chú; không khôi phục được thông tin nguồn đã bị adapter trước đây bỏ mất.
- CLI không retry chọn lọc ID/claim lỗi; artifact giữ partial/error để người vận hành review/rerun. Không tự đổi nhãn hoặc lấp bằng config.
- Artifact có source text/metadata riêng tư: chỉ lưu local, không commit. Bộ fixture test là tổng hợp.

STOP. Wait for architecture review. Next Phase = DO NOT START.
