# 08 — PROJECT STATE

Current Phase = Phase 2 — Customer Context

Status = IMPLEMENTED — PENDING ARCHITECT REVIEW

Next Phase = DO NOT START

Do not start Phase 3. Wait for architecture review.

## Phạm vi đã thực hiện

- Phase 2.1 documentation memory patch trên base `20736d0ed9bd3b09e81ac67c70d2fee01e9303b0`: [Strategyzer foundations](10-STRATEGYZER-FOUNDATIONS.md) nay là **explicit architecture dependency**. Agent phải đọc `00`–`10` trước architecture/product-logic changes và STOP/report nếu có xung đột. Patch chỉ sửa tài liệu, không đổi runtime hoặc Phase 2 extraction behavior; không mở Phase 3.

- Base branch v2-phase-1-signal-extraction, commit 241fa436b962341df60034a105f6878fd7fa03ac. Branch bàn giao: v2-phase-2-customer-context. Authorization trực tiếp ghi tại DEC-032.
- Kiến trúc shared Customer Intelligence Engine + Content Research / Product Discovery và DEC-024–032 đã cập nhật trước implementation. Router/UI/mode execution vẫn chỉ là tài liệu, chưa triển khai.
- customer_context_models.py + customer_context_extractor.py: signals.json v2.signals.1 → contexts.json v2.contexts.1, đúng năm field B2C, zero/multiple per-comment candidates, OBSERVED/DERIVED, code-generated exact claim, source/hash/span/issue trace.
- Dùng chung quote_span, source hash model, truth type/issue structure và validate_source_span với Phase 1. Input Phase 1 revalidate trước API; giữ upstream status/issues, không sửa signals.json.
- CLI độc lập: `tim extract-context -i signals.json -o contexts.json [--model MODEL] [--batch-size 10]`. Bỏ -o thì xuất cạnh input. Exit 0 complete, 2 khi context có partial/error/global issue; 1 khi lỗi input/output. Không ghi đè input.
- Default legacy runtime behavior changed: **NO**. Phase 1, classifier/run, bank/selection, strategy/Reelo và legacy outputs giữ nguyên hành vi. Không clustering/final segment/frequency/insight/content/product generation/Value Map/experiment/router.

## Tests và kiểm chứng

- Phase 2.1 docs-only regression: `python -m pytest tests -q -p no:cacheprovider` → **178 passed in 1.18s**. Diff chỉ có tài liệu Markdown; runtime code và Phase 2 extraction behavior không đổi.

- `python -m pytest tests -q -p no:cacheprovider` → **178 passed in 1.42s**, Python 3.13.15 / pytest 8.4.2.
- 48 offline cases mới cho năm field, multi/zero/ambiguous, unsupported demographics/quotes/IDs/truth types/B2B fields, serialization/hash/spans, API errors, CLI và Phase 1 compatibility. Toàn bộ 130 tests từ base vẫn pass; không live API trong test suite.
- Kiểm source snapshot equality, exact accepted claims, local-only artifact 10 ví dụ và diff/docs links. Không đưa secret hoặc private sample vào commit.

## Real-data review — cùng 50 source comments của Phase 1.1

Input là signals-after.json đã lưu từ Phase 1.1, giữ đúng 50 source snapshot/thứ tự. Dùng cùng resolved model, batch size 10; không lấy comment mới, không gọi lại signal extraction.

Processed **50**; **ok=28, no_context=19, partial=3, error=0**. **47 accepted claims, 4 rejected claims**.

| Field | Accepted | Rejected |
|---|---:|---:|
| audience_segment | 8 | 1 |
| context | 4 | 0 |
| situation | 28 | 3 |
| life_or_business_stage | 7 | 0 |
| user_buyer_distinction | 0 | 0 |

Rejection code: ungrounded_quote=4. Unassigned rejected=0. Unknown context không bị ép điền, user_buyer_distinction rỗng khi không có bằng chứng phù hợp. Không đặt numeric pass threshold; số accepted không chứng minh field assignment đúng ngữ nghĩa.

Artifact chỉ lưu cục bộ, không commit:

`D:/Tuan-CoWork/TUAN-insight-miner/output/v2-phase2-worktree/output/phase2-context-review/phase2-context-review.md`

Cùng thư mục có contexts.json và metrics.json. Report chứa 10 ví dụ, source comment, field, exact quote, truth type và accepted/rejected reason. Chọn theo status/field coverage rồi input order cho review định tính, không tuyên bố đại diện thống kê.

## Giới hạn / việc cần review

- Context field assignment vẫn là candidate per comment. Grounding bảo đảm quote/claim/source khớp, không tự chứng minh semantic entailment, self-report hay sarcasm được model hiểu đúng.
- Claim giữ nguyên source wording; ví dụ normalized audience label ở specification chưa được tạo bằng paraphrase. Không có final segment/corpus classification.
- Phase 1 partial/error được giữ làm upstream provenance; Phase 2 có thể đọc source hợp lệ của record đó, không biến lỗi upstream thành thành công.
- Source raw metadata/missing metrics giữ nguyên từ Phase 1; không phục hồi dữ liệu adapter cũ đã mất. Không selective retry claim lỗi.

STOP. Next Phase = DO NOT START. Không bắt đầu Phase 3.
