# 08 — PROJECT STATE

Current Phase = Phase 3 — Pattern Engine

Status = IMPLEMENTED — PENDING ARCHITECT REVIEW

Next Phase = DO NOT START

Do not start Phase 4. Wait for architecture review.

## Phạm vi đã thực hiện

- Base `v2-phase-2-customer-context@62b03a26e4c48b971b209d6f55eccdd025ec0ff0`; branch `v2-phase-3-pattern-engine`, authorization DEC-033; implementation DEC-034 chờ review.
- signals.json v2.signals.1 + contexts.json v2.contexts.1 → patterns.json v2.patterns.1. Reuse source/hash/span validators, revalidate artifact compatibility, giữ upstream issues. Không thay extraction Phase 1/2.
- Closed catalog + category/field-bounded semantic relation adapter + deterministic complete-link grouping; global possible-counter-evidence pass; extractive DERIVED labels, context/wording variants, exact language bank và deterministic support với missing coverage.
- Serialization replay kiểm membership/quote/hash/support/labels. Chỉ candidate; không final segmentation, Verified Insight, demand, opportunity, content, topic, angle, Reelo, router hoặc Phase 4.
- CLI độc lập: `tim build-patterns --signals signals.json --contexts contexts.json -o patterns.json [--model MODEL] [--exact-only]`.
- Default legacy runtime behavior changed: **NO**. Không sửa classifier/run, signal/context extraction, dependencies, default configs, bank/selection hoặc Reelo. Runtime mới chỉ qua command/API Pattern riêng.
- Strategyzer foundations tiếp tục là explicit architecture dependency; agents phải đọc đủ 00–10 và STOP/report nếu xung đột accepted decisions/foundations.

## Tests và kiểm chứng

- `python -m pytest tests -q -p no:cacheprovider` -> **225 passed in 1.41s** (Python 3.13.15 / pytest 8.4.2).
- **47 new offline cases**; all 178 tests from the Phase 2 base remain green. No live AI dependency in tests.

- Offline fixtures/mocks: semantic grouping và separation, complete-link chống chain merge, context variants, corpus language, author/comment dedup, metrics null/known zero, provenance/serialization/tamper, invalid members/relations/truth types, API errors/transport scoping, CLI và compatibility.
- Full source snapshots cùng 50 comments đã đối chiếu; không re-extract hoặc scrape. Save/load replay kiểm deterministic artifact.
- Diff runtime chỉ thêm ba modules Pattern và command/parser riêng; Phase 1/2 và default legacy code không đổi. Không private sample/secret vào commit.

## Real-data review — same 50 saved comments

Model semantic: `claude-opus-4-7`; adapter `phase3.relations.3`. Semantic status = complete; 154 accepted relations; không relation rejection mới. Tám `ungrounded_quote` issues của input được giữ riêng theo phase: Phase 1 = 4, Phase 2 = 4. CLI sẽ trả exit 2 để làm rõ upstream issues, dù semantic pass complete.

| Metric | Count |
|---|---:|
| Patterns | 85 |
| Singleton patterns | 64 |
| Patterns with 2+ comments | 21 |
| Patterns with 3+ comments | 10 |
| Patterns with possible contradictions | 15 |
| Patterns with wording variations | 28 |
| Exact language-bank phrases | 17 |
| Exact phrases repeated across comments | 0 |

Top 10 support counts: **7, 5, 4, 4, 4, 4, 3, 3, 3, 3**. Labels, original quotes, contexts, counter-refs và 10 representative patterns nằm trong local review; không copy customer data vào docs/Git. Pattern count có thể lớn hơn comment count vì multi-signal, nhiều category/context fields và singleton candidates. Không có numeric success threshold.

Local artifact:

`D:/Tuan-CoWork/TUAN-insight-miner/output/v2-phase3-worktree/output/phase3-pattern-review/phase3-pattern-review.md`

Cùng folder có patterns.json, metrics.json, semantic response và diagnostic runs. Tất cả thuộc ignored output/. File bàn giao có 10 representative patterns, mỗi pattern ít nhất ba source comments, và manual findings.

## Known issues / cần architect review

- Semantic relations vẫn do model đánh giá: có nhóm context/problem quá rộng và các nhóm nhỏ có thể bị tách do thiếu complete-link pairs. Test provenance không chứng minh grouping đúng.
- Extractive shortest-quote label không thêm facts nhưng có thể quá ngắn, không đại diện hết members; cần đọc variations/full source trước diễn giải.
- Một số upstream spans là advice/promotion/đoạn câu ngắn, không self-report chắc chắn. Giữ nguyên và ghi review; không tự sửa Phase 1/2 hoặc suy author identity.
- Counter-evidence là possible relationship giữa những nguồn/situations khác nhau, chưa xác minh mâu thuẫn thực. Context variants chưa là final segment.
- Author identifiers có thể là aliases; không bảo đảm số người thật. Dedup theo source_record_id, chưa phát hiện repost khác ID. Missing metadata không được khôi phục.
- Semantic adapter giới hạn 200 accepted claims / 180,000 ký tự transport; vượt giới hạn hoặc API lỗi xuất exact baseline có error/exit 2, không silently truncate. Corpus lớn hơn cần review partition/scaling policy.
- Không blocker kỹ thuật để bàn giao review. Những giới hạn chất lượng trên không phải quyết định chấp nhận kiến trúc hoặc quyền mở Phase 4.

STOP. Next Phase = DO NOT START.
