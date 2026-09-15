# 06 — DEFINITION OF DONE

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
