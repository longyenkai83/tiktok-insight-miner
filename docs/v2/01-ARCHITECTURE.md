# 01 — ARCHITECTURE

## Phase 3 — implemented, pending architect review

`signals.json + contexts.json → closed claim catalog → similarity relations → deterministic complete-link groups → patterns.json`.
Independent `build-patterns` CLI; không nối vào legacy run, classifier, Reelo hoặc hai downstream modes.

- Revalidate hai schema, hash của input signals và join comment_id/source_hash. Thiếu context record vẫn dùng signal; context orphan ghi issue và bỏ khỏi catalog.
- Candidate grouping dùng exact whitespace-normalized evidence equality và semantic relations qua interface `RelationProvider`. Adapter Anthropic chỉ so sánh claim IDs có thật, không tạo members/quotes/metrics. Không dùng embedding/dependency mới.
- Code complete-link theo thứ tự evidence ID ổn định: chỉ thêm member nếu tương thích với **mọi** member đang có, chặn merge bằng chuỗi A–B–C khi A–C chưa có support. Không gộp khác category; context phải cùng field. Subcategory mixed giữ mọi upstream path.
- Semantic relations `same_meaning`, `variation`, `contradiction` là DERIVED. Relation lỗi/unknown/self/duplicate/cross-category bị loại có issue. Contradiction không làm mất pattern; counter-ref không được tính vào support của pattern bị phản bác.
- Stage labeling bảo thủ: quote ngắn nhất trong group làm representative label, normalized_meaning chỉ chuẩn hóa whitespace. Cả hai dùng DERIVED, không tự gọi đó là phát biểu bao quát toàn group. Giữ mọi wording variant và context distribution nguyên văn; không sinh free-form customer fact.
- Singletons vẫn là candidate. Pattern không phải Insight; không importance score, Verified Insight, opportunity, topic, angle, content, experiment hoặc final segment.

Semantic adapter chia similarity requests theo category/context field; một pass riêng trên toàn catalog tìm contradiction. Transport dùng short IDs và enum scoped theo request, code chỉ map exact ID hợp lệ. Giới hạn toàn catalog: tối đa 200 accepted claims và 180,000 ký tự payload, không truncate. Vượt giới hạn/API lỗi trả exact baseline với semantic_status=error và exit 2; không giả là semantic success. `--exact-only` không gọi AI và ghi NOT_CHECKED cho phản chứng. Đây là giới hạn Phase 3 cần review cho corpus lớn.

## CURRENT STATE — chỉ mô tả baseline đã audit

Theo baseline định danh tại [00-PROJECT-OS.md](00-PROJECT-OS.md):

- Miner dùng classifier bảy bucket; dữ liệu classified rẽ sang report/brief/strategy và bank/selection. Strategy hiện không cấp insight có kiểu cho bank/selection.
- `selected_angles.json` thực tế chứa record comment được chọn, không phải hợp đồng Angle V2.
- Hai đường xuất pack Markdown khác nhau; có mất/truncate trường và pha trộn config. Bridge sang Reelo hiện qua file/Drive, chưa có typed Content Intelligence Packet.
- `strict_grounding` hiện chủ yếu ràng buộc prompt, chưa bảo đảm quote/likes đối chiếu nguồn. Một số tầng dùng persona/meta-pain/config thiếu phân biệt truth type.
- Reelo có các skill viết và kiểm nội dung; quy tắc chống bịa và rubric số liệu còn mâu thuẫn. Không có cơ sở để coi mọi đầu ra hiện tại là đã qua cổng bằng chứng V2.

Đây là gap cần thiết kế giải quyết trong tương lai, không phải lỗi được phép sửa ở Phase 0. Tài liệu không chứng nhận hành vi production ngoài snapshot audit.

## TARGET — locked architecture, DEC-024–032

```text
Shared Customer Intelligence Engine:
Source → Normalized Evidence → Signal Extraction → Customer Context
→ Pattern Engine → Evidence Engine → Verified Insight → Priority Need

A. CONTENT RESEARCH MODE:
Verified Insight → Content Opportunity → Topic → Angle → Human Selection
→ Content Intelligence Packet → Reelo Writer

B. PRODUCT DISCOVERY MODE:
Verified Insight → Priority Need → Opportunity Area → Possible Value Map
  (Products & Services / Pain Relievers / Gain Creators)
→ Assumptions → Experiments → Evidence → Decision → Validated Product
```

## Lõi dùng chung

Normalized Evidence giữ source snapshot, metadata, hash và text để kiểm provenance; không biến lời tự nhận thành fact ngoài đời. Signal Extraction giữ nhiều Jobs/Pains/Gains/Behavior/Language signals trên một comment. Customer Context bổ sung candidates theo đúng năm field đã chốt, vẫn ở cấp comment. Pattern Engine mới chịu trách nhiệm clustering và tần suất xuyên corpus (Phase 3); giữ context variants, final segmentation thuộc downstream analysis.

Evidence Engine giữ support/phản chứng/scope để đi tới Verified Insight. Verified không có nghĩa model tự cho confidence cao là đúng. Priority Need phải xuất phát từ Jobs/Pains/Gains/Verified Insights có evidence, không từ offer/config tự suy nhu cầu. Chi tiết ranking và tiêu chí verification là thiết kế phase sau, chưa thực thi.

## Hai mode downstream

Content Research: Content Opportunity dẫn tới Topic/Angle, Human Selection và typed Content Intelligence Packet cho Reelo Writer. Writer sáng tạo diễn đạt, không tạo customer truth. Không dùng legacy selected_angles làm schema V2.

Product Discovery: Opportunity Area và Possible Value Map là đề xuất (PROPOSED), không phải validated demand. Value Map có Products & Services, Pain Relievers, Gain Creators. Mọi candidate cần Assumption → Experiment → Evidence → Decision trước khi gọi Validated Product. Evidence thí nghiệm giữ provenance riêng, không biến proposal thành lời khách quan sát được. Không coi phê duyệt một ý tưởng là bằng chứng nhu cầu.

Product bao gồm miễn phí hoặc trả phí: tool, checklist, template, calculator, lead magnet, workshop, service, feature, resource hoặc commercial product. V2 B2C-first; không B2B stakeholder graph/buying committee.

Project goal có thể là CONTENT / PRODUCT_DISCOVERY / BOTH trong tương lai. Router/UI/unified agent chỉ là kiến trúc tài liệu, không được cài trong Phase 2.

## Phạm vi Phase 2

`signals.json (v2.signals.1) → contexts.json (v2.contexts.1)`, độc lập CLI. Customer Identity chỉ có audience_segment, context, situation, life_or_business_stage, user_buyer_distinction (optional). Không có final segment/corpus clustering. Cùng source có thể có zero/multiple context candidates. Unknown hợp lệ, không infer identity từ topic video hoặc metadata tác giả.

Reuse source snapshot/hash, source-span validation, truth type OBSERVED/DERIVED và issues của Phase 1. Model trả field/evidence_quote/truth_type/confidence theo comment ID; code tạo claim từ exact validated source span. Không paraphrase demographics, không sinh HYPOTHESIS/PROPOSED, content hay product opportunity trong Phase 2.

## Phân biệt CURRENT STATE và thiết kế đích

Audit baseline mô tả legacy, không chứng nhận kiến trúc mới đã chạy. Kiến trúc tuyến tính cũ DEC-011 được thay bởi DEC-024/025 theo yêu cầu trực tiếp; giữ lịch sử trong DECISIONS/CHANGELOG. Phase 1 chạy độc lập; Phase 2 chỉ thêm context. Phase 3 thêm Pattern Engine độc lập; các tầng sau Pattern vẫn cần phạm vi review riêng.
