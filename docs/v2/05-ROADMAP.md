# 05 — ROADMAP

Current Phase = Phase 2 — Customer Context

Status = IMPLEMENTED — PENDING ARCHITECT REVIEW

Next Phase = DO NOT START

Phase 2 được cho phép trực tiếp qua DEC-032. Không mở Phase 3.

| Phase | Phạm vi | Trạng thái |
|---|---|---|
| 0 | Architecture documentation, audit baseline | Đã bàn giao |
| 1 / 1.1 | Source → multi-signals, strict grounding, independent CLI | Đã triển khai |
| 2 | signals.json → context candidates từng comment, đúng năm field B2C | CURRENT |
| 3 | Pattern Engine, clustering, final segments, corpus repetition | DO NOT START |
| Sau Phase 3 | Evidence Engine → Verified Insight → Priority Need | Thiết kế, chưa triển khai |
| Content downstream | Content Opportunity → Topic → Angle → Human Selection → Packet → Reelo Writer | Thiết kế, chưa triển khai |
| Product downstream | Opportunity Area → Possible Value Map → Assumptions → Experiments → Evidence → Decision → Validated Product | Thiết kế, chưa triển khai |
| Orchestration | CONTENT / PRODUCT_DISCOVERY / BOTH goal router và UI | Thiết kế, chưa triển khai |

Phase 2 giữ source text/hash/spans và Phase 1 compatibility. Không đổi legacy run, không cần thay Reelo. Source evidence tồn tại ngay từ Phase 1, không chờ Evidence Engine mới trace.

Candidate context là claim có nguồn của một comment, không là final cluster hay hồ sơ của toàn thị trường. Mỗi phase sau cần phạm vi, tiêu chí nghiệm thu và review riêng; tests/push không tự mở phase.
