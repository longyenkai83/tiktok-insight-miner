# 08 — PROJECT STATE

Current Phase = Phase 4 — Evidence + Insight Engine

Status = IMPLEMENTED — PENDING ARCHITECT REVIEW

Next Phase = DO NOT START

Do not start Phase 5. Wait for architecture review.

## Phase 4.1 — state semantics and router memory

Base: v2-phase-4-evidence-insight@960225de80d4dc8c5ee58ebd98679f004ae803ea; same branch.
Authorization/accepted decisions DEC-042–047. Current phase/status/next-phase gate above stay unchanged.

- Schema v2.insights.2 removes evidence_backed; source_grounded means structural provenance,
  evidence_support_present means attached evidence, machine_review_passed means usable automated
  review passed. Emitted Insight Candidates remain pending_human_review; outcome machine_accepted.
- Negative/missing/invalid/not-run reviews give machine_review_passed=false on outcomes. This
  boolean is replay-validated, including deduplicated candidates; reasons remain in review/issues.
- Old v2.insights.1 artifacts are explicitly rejected with a version error; no silent migration.
  Rebuild into a separate file from original patterns and saved model transports. Old files retained.
- Existing guards, model transport, prompts and separate semantic reviewer unchanged. No additional
  multi-reviewer system, acceptance-rate goal, router/scheduler/adapters/state store or Phase 5 runtime.
- Phase 5 Human Approval is the first explicit Human Governor and authoritative semantic gate.
  Machine acceptance never creates Verified Insight; human approval does not prove market/purchase.
- Both routers, normalized adapter fields, unknown/null rules, review evidence rule, incremental
  lifecycle, platform-neutral naming and direct typed Reelo handoff recorded in docs 00–11.
- Default legacy runtime changed: **NO**. Only opt-in Phase 4 artifact/state contract changed.

### Phase 4.1 validation

`python -m pytest tests -q -p no:cacheprovider` → **317 passed in 2.22s**.
20 new offline cases plus updated Phase 4 assertions; all 297 previous tests remain green.
No live API tests. Coverage includes non-promotable flags, outcome review state, support/provenance,
schema roundtrip, old-version rejection and pending-only state; automated review can still be wrong.

Same 50 comments / 85 patterns, replayed through the engine with saved Phase 4 proposals and reviews,
**no new API calls**. Input snapshot/hash, statements, evidence, scope, review decisions and issue codes
match the Phase 4 baseline exactly; only schema/state semantics changed.

| State check | Count |
|---|---:|
| Candidates | 24 |
| machine_accepted | 12 |
| rejected | 12 |
| deduplicated | 0 |
| Emitted pending_human_review | 12 |
| Outcome machine_review_passed true / false | 12 / 12 |
| human_verified=true | 0 |
| market_validated=true | 0 |
| purchase_validated=true | 0 |

Local-only state report:
`D:/Tuan-CoWork/TUAN-insight-miner/output/v2-phase4-worktree/output/phase41-state-check/phase41-state-check.md`.
New insights.json and metrics.json are beside it; all ignored, no customer data committed.
The original Phase 4 review below remains historical, including its old flag names and manual findings.

Known semantic overclaim/causality/context/shallow misses remain; the patch corrects state meaning,
not acceptance quality. They are expected inputs to future human review, not a demand for perfect AI
before Phase 5. Phase 5 still requires explicit authorization; Next Phase = DO NOT START.

## Phase 4 baseline — historical results before schema/state patch

## Phạm vi đã thực hiện

- Base `v2-phase-3-pattern-engine@6b743fd3c21cee57c5cb8b4846d82dfed5582ca0`; branch `v2-phase-4-evidence-insight`. Authorization DEC-035; architecture DEC-036–040, implementation DEC-041 pending review.
- Thêm Evidence models/engine và Insight models/engine/validator; `patterns.json v2.patterns.1 → insights.json v2.insights.1`, CLI build-insights độc lập.
- Revalidate source/hash/refs, code-built evidence/profile links/scope/support/variants/counters, closed pattern-ID transport, deterministic guards, separate semantic review and per-statement-part pattern mapping with code offsets. Output replay validation; conservative dedupe.
- Insight Statement DERIVED, pending_human_review. Historical v2.insights.1 used source_grounded/evidence_backed; superseded by DEC-042; human_verified, market_validated, purchase_validated luôn false. Text kể chuyện mua/hành vi vẫn là customer_speech.
- Không priority score, Content/Product Opportunity, Topic/Angle/hook/script, Value Map, offer, experiment, Reelo integration, ingestion state, YouTube, multi-tenancy hoặc rename legacy package.
- Default legacy runtime behavior changed: **NO**. Phase 1–3 modules/behaviors, dependencies và legacy run giữ nguyên; runtime mới chỉ qua command/API Insight riêng.

## Architecture memory

- [11-BUSINESS-OS-NORTH-STAR.md](11-BUSINESS-OS-NORTH-STAR.md): Customer Intelligence là lớp đầu của AI-native Business OS; agents execute, evidence informs, human Governor approves consequential decisions.
- Productization/distribution, reusable core/configurable layers, portable platform-neutral typed contracts/provenance/state/IDs là target; không triển khai multi-tenancy.
- Multi-source adapters → Normalized Evidence → shared engine. Continuous/daily ingestion tách khỏi periodic/manual analysis; future source store idempotent/durable-ID-first/hash-protected, status và batch trace, retry FAILED. YouTube là backlog.
- Direct typed Reelo packet/API hoặc structured handoff là target, Drive chỉ legacy compatibility/backup; giữ Topic/Angle/Human Selection, dedupe/supersession/provenance/conflict approval. Chưa tích hợp runtime.
- Strategyzer và Business OS north star là architecture dependencies. AGENTS/CLAUDE yêu cầu đọc đủ 00–11 và STOP/report nếu conflict; Human Governor không phải gate cho từng thao tác cơ học ít rủi ro.

## Tests

`python -m pytest tests -q -p no:cacheprovider` → **297 passed in 2.17s** (Python 3.13.15 / pytest 8.4.2).

**72 new offline cases**, toàn bộ 225 tests từ base vẫn xanh. Bao gồm single/cross-pattern, closed IDs, source/metric/tamper, scope, negative demographics/numbers/solutions/truth flags, counter/variation preservation, semantic review failures, part support mapping, dedupe, API/CLI và compatibility. Không live AI dependency trong tests.

## Real-data review — same 50 saved comments

Model `claude-opus-4-7`, transport `phase4.synthesis_review.2`. Input 85 patterns nguyên trạng từ Phase 3; source snapshots không đổi. Semantic synthesis/review completed; CLI exit 2 vì có rejection/upstream issues.

| Metric | Count |
|---|---:|
| Patterns input | 85 |
| Candidates proposed | 24 |
| Insight candidates accepted by machine checks | 12 |
| Single-pattern insights | 0 |
| Cross-pattern insights | 12 |
| With possible contradictions | 8 |
| With cited narrow-context fields | 12 |
| Rejected candidates | 12 |
| Deduplicated candidates | 0 |

New issue counts: impossible_relationship=8; invalid_review_support=1; semantic_overclaim=1; invalid_part_support=1; unsupported_demographic=1. Upstream ungrounded_quote=8 (Phase 1=4, Phase 2=4).

Narrow-context count chỉ nói có context field được dẫn, không chứng nhận final segment hoặc statement đã giữ scope hoàn hảo. Cả 12 candidates có across_corpus scope, không có comment chung cho toàn bộ selected pattern set. Không suy cùng người/cùng causal sequence từ tổng số nguồn. Không có numeric pass threshold; single-pattern support được kiểm offline, không bịa ví dụ thật.

Local-only artifact:

`D:/Tuan-CoWork/TUAN-insight-miner/output/v2-phase4-worktree/output/phase4-insight-review/phase4-insight-review.md`

Gồm 10 representative candidates có ít nhất ba source comments, 3–5 exact quotes mỗi candidate, links/scope/summary/variants/counters/kind/limits/flags, statement-part refs và manual findings. Hai accepted cases hẹp hơn được ghi bổ sung. Cùng folder có insights.json, metrics.json và model transports. Tất cả ignored; không commit private data.

## Known issues / architect review bắt buộc

- **Manual inspection phát hiện OVERCLAIM, FALSE CAUSALITY và CONTEXT LEAK vẫn qua semantic reviewer.** Ví dụ ở mức loại lỗi: suy động cơ tự bảo vệ/đặc điểm bẩm sinh; ghép trải nghiệm khác người thành cohort; coi lời nhắm audience trong promotion/advice là self-report. Không coi machine acceptance/attached support/machine review là semantic guarantee hoặc customer truth đã duyệt.
- Một số statements còn SHALLOW hoặc dùng từ phổ quát/mức độ mạnh hơn evidence. Per-part mappings kiểm ID/range/coverage, không tự chứng minh entailment. Grounding và máy review không thay human judgment.
- Tám relationship mismatch bị chặn; model có thể chọn relation label không khớp các category/path thực sự được chọn. Code không tự đổi label để salvage. Guards EN/VI có thể over-reject hoặc bỏ sót cách diễn đạt khác; số liệu trong generated prose bị chặn bảo thủ dù nguồn có số.
- Deterministic dedupe chỉ xử lý normalized near-identical wording + same support/type. Paraphrase cùng ý nhưng khác wording/support có thể còn trùng; không merge chỉ vì giống keywords.
- Scope/support kế thừa hạn chế Phase 3 và nguồn: aliases không chứng minh số người thật; repost khác ID chưa dedup; thiếu metric là unknown. Counter-evidence là possible relation, không proof đối phương sai.
- EvidenceKind enum chuẩn bị future evidence nhưng runtime hiện chỉ customer_speech; flags human/market/purchase chưa thể bật bằng tự thuật hoặc model approval.
- Limits: 200 patterns, 300,000 characters/request, review batches six; vượt giới hạn/API/truncation lỗi hiện rõ, không truncate ngầm. Không triển khai scaling/ingestion ở đây.

Không blocker kỹ thuật cho bàn giao nhánh review. Các lỗi chất lượng ngữ nghĩa nêu trên cần kiến trúc sư đánh giá trước khi chấp nhận hoặc mở phase tiếp theo.

STOP. Next Phase = DO NOT START.
