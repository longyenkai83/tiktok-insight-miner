# 05 — ROADMAP

Current Phase = Phase 4 — Evidence + Insight Engine

Status = IMPLEMENTED — PENDING ARCHITECT REVIEW

Next Phase = DO NOT START

Phase 4 được cho phép trực tiếp qua DEC-035. Không mở Phase 5. DEC-041 ghi chi tiết implementation chờ review.

| Phase | Phạm vi | Trạng thái |
|---|---|---|
| 0 | Architecture documentation, audit baseline | Đã bàn giao |
| 1 / 1.1 | Source → multi-signals, strict grounding, independent CLI | Đã triển khai |
| 2 / 2.1 | Context candidates, năm field B2C, Strategyzer memory | Đã triển khai |
| 3 | Candidate Pattern Engine, context/wording variants, corpus language, possible contradictions | Đã triển khai, semantic limitations được giữ |
| 4 | Evidence Engine → evidence-backed Insight Candidates, pending human review | CURRENT |
| Sau Phase 4 | Human consequential verification, Priority Need, final segmentation/ranking | DO NOT START |
| Content downstream | Content Opportunity → Topic → Angle → Human Selection → Packet → Reelo Writer | Thiết kế, chưa triển khai |
| Product downstream | Opportunity Area → Possible Value Map → Assumptions → Experiments → Evidence → Decision → Validated Product | Thiết kế, chưa triển khai |
| Orchestration | CONTENT / PRODUCT_DISCOVERY / BOTH goal router và UI | Thiết kế, chưa triển khai |

Phase 2 giữ source text/hash/spans và Phase 1 compatibility. Không đổi legacy run, không cần thay Reelo. Source evidence tồn tại ngay từ Phase 1, không chờ Evidence Engine mới trace.

Candidate context là claim có nguồn của một comment, không là final cluster hay hồ sơ của toàn thị trường. Mỗi phase sau cần phạm vi, tiêu chí nghiệm thu và review riêng; tests/push không tự mở phase.

## Future backlog — chưa được triển khai trong Phase 4

- Incremental source store/state, durable ID dedupe + hash protection, retry FAILED,
  traceable batches; ingestion frequency separate from periodic/manual intelligence.
- Source adapter YouTube and other platforms; no package rename now.
- Typed direct Reelo packet ingestion, retain dedupe/supersession/provenance/conflict
  approval; Drive compatibility/backup only, no brief.md contract.
- Human Governor gates, specialist-agent typed handoffs, productization/distribution;
  no multi-tenancy, full Business OS orchestration or downstream generators now.
- Stronger behavior/commitment/payment/market evidence adapters require reviewed
  provenance and scope; do not unlock validation flags from speech keywords.
