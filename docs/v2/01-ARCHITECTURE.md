# 01 — ARCHITECTURE

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

Normalized Evidence giữ source snapshot, metadata, hash và text để kiểm provenance; không biến lời tự nhận thành fact ngoài đời. Signal Extraction giữ nhiều Jobs/Pains/Gains/Behavior/Language signals trên một comment. Customer Context bổ sung candidates theo đúng năm field đã chốt, vẫn ở cấp comment. Pattern Engine mới chịu trách nhiệm clustering, final segments và tần suất xuyên corpus (Phase 3, chưa bắt đầu).

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

Audit baseline mô tả legacy, không chứng nhận kiến trúc mới đã chạy. Kiến trúc tuyến tính cũ DEC-011 được thay bởi DEC-024/025 theo yêu cầu trực tiếp; giữ lịch sử trong DECISIONS/CHANGELOG. Phase 1 chạy độc lập; Phase 2 chỉ thêm context. Mọi tầng sau đó cần phạm vi review riêng.
