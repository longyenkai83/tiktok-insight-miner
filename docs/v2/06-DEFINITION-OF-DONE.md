# 06 — DEFINITION OF DONE

## Phase 3 — điều kiện bàn giao cho architect review

- Signals + compatible contexts tạo patterns.json v2.patterns.1; missing context hợp lệ, orphan không tự tạo pattern.
- Mọi member/quote/path/hash/span/truth type truy về accepted upstream claim; persisted output replay kiểm membership và support.
- Semantic similarity qua closed relation provider; deterministic complete-link grouping; exact-only baseline có nhãn rõ.
- Multi-signal không inflate comment/author counts; missing metrics có null/coverage; không priority score.
- Corpus language bank giữ exact phrases và distinct support; không đổi Phase 1 repeated_expressions.
- Wording/context variations và possible contradictions có refs; phản chứng không tính vào supporting count.
- Chỉ candidate DERIVED patterns, không HYPOTHESIS/PROPOSED/Verified Insight, product/content opportunity, topic, angle, Reelo hoặc final segmentation.
- Offline tests và full suite pass; cùng 50 saved comments được review locally, đủ metrics/top 10/10 representative patterns và kiểm over-merge/over-split/fabrication/context mixing.
- Không commit customer data; cập nhật docs, commit/push đúng branch, không merge main. Default legacy unchanged.
- State = Phase 3 — Pattern Engine / IMPLEMENTED — PENDING ARCHITECT REVIEW / Next Phase = DO NOT START. Không bắt đầu Phase 4.

Các tiêu chí Phase 2/1 bên dưới là phạm vi lịch sử của từng lần bàn giao, không ghi đè authorization Phase 3.

## Phase 2 — điều kiện bàn giao cho architect review

- Official architecture có shared engine và hai mode Content Research/Product Discovery; đủ DEC-024–032 và evidence-first product rules.
- signals.json v2.signals.1 làm input trực tiếp, contexts.json v2.contexts.1 có đúng năm B2C identity fields; zero context hợp lệ.
- Mọi claim có source comment ID/hash/span/quote/confidence/truth type; quote kiểm bằng code, claim tạo từ nguồn. Chỉ OBSERVED/DERIVED.
- Unknown/missing/duplicate result IDs có lỗi rõ; một item lỗi không làm mất item tốt; không fabricated demographics/context.
- Không clustering/final segment/pattern frequency/insight/content/product generation/router; không bắt đầu Phase 3.
- Offline tests cho năm field, multiple/zero/ambiguous, grounding/IDs/truth types, serialization và Phase 1/legacy compatibility; full suite xanh.
- Mẫu 50 comment cùng Phase 1 khi có data/credentials, metrics theo field, local review 10 ví dụ; không commit private data, không đặt pass threshold.
- Cập nhật docs/state, commit/push nhánh Phase 2; IMPLEMENTED — PENDING ARCHITECT REVIEW, Next Phase = DO NOT START.

## Phase 1 — sẵn sàng cho architect review

- Raw Comment/raw_comments.json chạy trực tiếp qua CLI extract-signals và xuất signals.json có version/provenance.
- 0..n signals/comment; đủ Jobs/Pains/Gains/Behavior/Language theo taxonomy đã giao.
- Chỉ OBSERVED/DERIVED; quote và LANGUAGE kiểm nguồn bằng code; claim lỗi không làm mất claim tốt.
- Unknown/missing/duplicate result IDs và input IDs không rõ được xử lý có trạng thái/lỗi.
- Không segmentation, B2B roles, hypothesis, clustering, insight, topic, angle, content hoặc Reelo change.
- Test offline các trường hợp bắt buộc, serialization và legacy classifier; full suite pass, không secret/raw private vào commit.
- Docs/state cập nhật, commit/push nhánh riêng. IMPLEMENTED — PENDING ARCHITECT REVIEW. Next Phase = DO NOT START.

## Phase 0 — nghiệm thu tài liệu (lịch sử)

- Có đủ mười tài liệu `00`–`09`, link nội bộ hợp lệ, nhiệm vụ mỗi file rõ ràng.
- CURRENT STATE có baseline audit và snapshot commit; không được gọi V1 là target V2.
- Chuỗi kiến trúc đủ và đúng thứ tự theo chỉ thị, bao gồm Human Selection và typed Content Intelligence Packet.
- Truth types dùng đúng OBSERVED / DERIVED / HYPOTHESIS / PROPOSED; áp dụng theo claim, có rule chống nâng nhãn sai.
- DECISIONS nêu đủ mười quyết định bắt buộc; phân biệt quyết định đã chốt và chi tiết schema/triển khai chưa duyệt.
- Customer Profile Jobs/Pains/Gains + Context, multi-signal/comment và Customer Identity B2C-first được phản ánh xuyên schema/contract; không có logic hệ sinh thái B2B.
- Insight DERIVED truy được về source comment; nguồn thiếu/giả thuyết không được dùng làm observed truth.
- CLAUDE.md và AGENTS.md bắt buộc mọi coding agent đọc đủ docs/v2 trước sửa code; chỉ dẫn V1 cũ được ghi rõ CURRENT STATE.
- PROJECT-STATE giữ Phase 0 / ARCHITECTURE DOCUMENTATION / Next Phase 1 Signal Extraction / Do not start Phase 1 without review.
- Chạy existing tests; báo đúng kết quả, không gọi đó là kiểm chứng V2 đã triển khai.
- Diff chỉ gồm tài liệu/chỉ dẫn agent; không sửa code, prompt, runtime config, dependencies, fixtures hay tests.
- Commit và push nhánh tài liệu; báo branch, commit hash, files, tests và runtime behavior changed YES/NO. STOP.

Hoàn tất bàn giao Phase 0 không tự chuyển phase. Review của chủ dự án để mở Phase 1 vẫn phải được ghi nhận riêng.

## Tiêu chí tương lai — PROPOSED, chưa thực hiện

| Phần | Các trường hợp phải chứng minh khi triển khai được duyệt |
|---|---|
| Source/Signal | Nhiều signal/comment, zero signals, Unicode quote spans, missing metrics, dedup, lineage qua export, không ép bucket |
| Context/Profile | audience_segment/context/situation có nguồn hoặc unknown; `life_or_business_stage` chỉ khi liên quan; `user_buyer_distinction` (optional) chỉ khi use case B2C cần; persona/meta-pain chỉ là giả định; Jobs/Pains/Gains có refs |
| Pattern | Count nguồn phân biệt, không count signal thành người, scope mẫu và phản chứng, không suy market % từ like |
| Insight/Evidence | Mỗi DERIVED claim trace nguồn; quote/metric lệch bị chặn; single-case không thành recurring fact; hypothesis giữ riêng |
| Topic/Angle | Bắt đầu từ insight, không thêm customer fact; wording linh hoạt không cần regex/đếm từ V1 |
| Selection | Người duyệt thật, version chính xác, auto recommendation không APPROVED, stale approval bị chặn |
| Packet | Version/type/ref/hash đầy đủ; tự đủ; unknown version/broken trace bị từ chối; legacy selected_angles không được nhận ngầm |
| Writer | Claim usage kiểm được; giữ attribution/scope; không bịa số/quote/case; thiếu truth trả về research |
| Unified Agent | Human gates, failure/resume lineage, không tự điền approval hoặc publish, không bỏ lỗi vì hết lượt rewrite |

Mỗi phase cần tests kiểm hành vi thật và trường hợp lỗi, cùng regression phù hợp phạm vi. Tiêu chí này không yêu cầu viết test V2 trong Phase 0 và không phê duyệt thiết kế implementation cụ thể.

## Bằng chứng bàn giao

Kết quả test thực tế được ghi tại [08-PROJECT-STATE.md](08-PROJECT-STATE.md). Git diff/commit là nguồn xác nhận file nào thay đổi; remote branch SHA phải khớp commit đã báo sau push. Không đưa hash của chính commit vào nội dung trước khi tạo commit.
