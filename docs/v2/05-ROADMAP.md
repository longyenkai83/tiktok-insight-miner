# 05 — ROADMAP

Current Phase = Phase 3 — Pattern Engine

Status = IMPLEMENTED — PENDING ARCHITECT REVIEW

Next Phase = DO NOT START

Phase 3 được cho phép trực tiếp qua DEC-033. Không mở Phase 4. Chi tiết implementation DEC-034 chờ review.

| Phase | Phạm vi | Trạng thái |
|---|---|---|
| 0 | Architecture documentation, audit baseline | Đã bàn giao |
| 1 / 1.1 | Source → multi-signals, strict grounding, independent CLI | Đã triển khai |
| 2 / 2.1 | Context candidates, năm field B2C, Strategyzer memory | Đã triển khai |
| 3 | Candidate Pattern Engine, context/wording variants, corpus language, possible contradictions | CURRENT — PENDING ARCHITECT REVIEW |
| Sau Phase 3 | Evidence Engine → Verified Insight → Priority Need; final segmentation downstream | DO NOT START |
| Content downstream | Content Opportunity → Topic → Angle → Human Selection → Packet → Reelo Writer | Thiết kế, chưa triển khai |
| Product downstream | Opportunity Area → Possible Value Map → Assumptions → Experiments → Evidence → Decision → Validated Product | Thiết kế, chưa triển khai |
| Orchestration | CONTENT / PRODUCT_DISCOVERY / BOTH goal router và UI | Thiết kế, chưa triển khai |

Phase 2 giữ source text/hash/spans và Phase 1 compatibility. Không đổi legacy run, không cần thay Reelo. Source evidence tồn tại ngay từ Phase 1, không chờ Evidence Engine mới trace.

Candidate context là claim có nguồn của một comment, không là final cluster hay hồ sơ của toàn thị trường. Mỗi phase sau cần phạm vi, tiêu chí nghiệm thu và review riêng; tests/push không tự mở phase.
