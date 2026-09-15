# 10 — STRATEGYZER FOUNDATIONS

Strategyzer foundations là **explicit architecture dependency** của V2. Đây là bản ghi nhớ vận hành từ các nền tảng đã được chủ dự án cung cấp và phê duyệt trong yêu cầu Phase 2.1; không phải bản chép hoặc trích nguyên văn toàn bộ knowledge base 14 bài học.

## Phân biệt nguồn, quyết định và quy tắc triển khai

| Nhãn | Ý nghĩa và thẩm quyền |
|---|---|
| SOURCE PRINCIPLE | Nguyên tắc nền tảng từ bản tóm tắt đã duyệt; không tự quy định schema, model hay thuật toán. |
| V2 DECISION | Cách dự án áp dụng nguyên tắc, đã được chủ dự án chốt; đối chiếu [07-DECISIONS.md](07-DECISIONS.md). |
| DERIVED IMPLEMENTATION RULE | Hệ quả vận hành suy ra từ nguyên tắc/quyết định; không giả làm nguyên văn nguồn hoặc quyền triển khai phase mới. |

Ba nhãn trên phân loại **căn cứ kiến trúc**, không thay thế truth types của customer claims: OBSERVED / DERIVED / HYPOTHESIS / PROPOSED.

## Customer Profile và bằng chứng

| SOURCE PRINCIPLE | V2 DECISION | DERIVED IMPLEMENTATION RULE |
|---|---|---|
| Hiểu Jobs / Pains / Gains của khách độc lập với giải pháp của mình. | Customer Profile = Jobs / Pains / Gains + Context (DEC-003); V2 B2C-first (DEC-019/031). | Không suy ngược pain/job/gain từ sản phẩm muốn bán; không thêm logic B2B. |
| Hiểu biết ban đầu về khách là giả định cho đến khi có bằng chứng hỗ trợ. | Persona/meta-pain/config không tự thành observed customer truth (DEC-006). | Giữ rõ nguồn và mức bằng chứng; không dùng config để lấp trường unknown. Phase 1/2 chỉ xuất OBSERVED/DERIVED, không tự sinh HYPOTHESIS. |
| AI hỗ trợ nghiên cứu, không thay bằng chứng khách hàng và phán đoán con người. | AI must not invent customer demand (DEC-026). | Quote/source/span/hash phải kiểm bằng code; nhãn ngữ nghĩa vẫn cần human review, confidence không xác thực nhu cầu. |
| Comment/phỏng vấn là bằng chứng về điều khách nói hoặc thuật lại trải nghiệm, không tự chứng minh hành vi mua. | Demand validation cần experiment/evidence/decision (DEC-029). | Ghi đúng attribution và phạm vi: “khách nói muốn” không được đổi thành “khách sẽ mua”. |

**SOURCE PRINCIPLE — mức bằng chứng cần mạnh dần:** speech → behavior → commitment/payment → real market. Đây là hướng tăng sức thuyết phục, không phải điểm số tự động hay bảo đảm thành công. Lời tự thuật về hành vi vẫn cần phân biệt với hành vi thực sự quan sát được.

**DERIVED IMPLEMENTATION RULE:** ghi loại bằng chứng, điều đã quan sát, giả định đang kiểm và giới hạn của phép thử. Một payment/commitment không tự chứng minh toàn thị trường hoặc mọi giả định đã đúng; quyết định phải gắn với evidence và phạm vi experiment. Chưa triển khai experiment engine trong Phase 2.

## Value Proposition Canvas

**SOURCE PRINCIPLE:** đối chiếu hai phía, không trộn giải pháp vào mô tả khách:

```text
Customer Profile                      Value Map
Jobs / Pains / Gains          ↔        Products & Services
                                      Pain Relievers
                                      Gain Creators
```

**V2 DECISION:** Customer Profile được đặt trong Context; Possible Value Map là đề xuất, chưa phải validated demand (DEC-027/028). Product có thể miễn phí hoặc trả phí: tool, checklist, template, calculator, lead magnet, workshop, service, feature, resource hoặc commercial product (DEC-030).

**DERIVED IMPLEMENTATION RULE:** mỗi pain reliever/gain creator phải chỉ rõ Job/Pain/Gain có bằng chứng mà nó định đáp ứng. Không gọi việc điền xong canvas là xác nhận fit hoặc demand.

## Product Discovery — chuỗi vận hành V2

**V2 DECISION** — áp dụng nền tảng vào chuỗi evidence-first đã duyệt:

```text
Customer Evidence → Jobs/Pains/Gains → Pattern → Verified Insight → Priority Need
→ Product Opportunity → Possible Value Map → Assumptions → Experiments
→ Evidence → Decision → Validated Product
```

Product Opportunity là **PROPOSED**, không phải validated demand. Chuỗi này mô tả nguyên tắc vận hành; `Opportunity Area` trong [01-ARCHITECTURE.md](01-ARCHITECTURE.md) là bước xác định vùng cơ hội trước Possible Value Map, không tạo một đường bỏ qua evidence. Tên “Verified” hoặc “Validated” không tự cấp trạng thái xác thực.

**DERIVED IMPLEMENTATION RULE:** mỗi Product Opportunity phải trace về evidence-backed Jobs/Pains/Gains/Verified Insight. Candidate chỉ thành validated qua Assumption → Experiment → Evidence → Decision; lưu căn cứ quyết định, không tự nâng PROPOSED thành OBSERVED. Không sinh Product Opportunity/Value Map/experiment trong patch này.

## Content và Value Scene

**SOURCE PRINCIPLE — Value Scene:** Need moment → Current struggle → Desired future. Dùng để hiểu lúc nhu cầu xuất hiện, khó khăn hiện tại và tương lai khách mong muốn.

**V2 DECISION:** sáng tạo nội dung bắt đầu sau customer intelligence; Content Research và Product Discovery dùng chung lõi có bằng chứng (DEC-007/024/025). Writer sáng tạo cách diễn đạt, không sáng tạo customer truth (DEC-010).

**DERIVED IMPLEMENTATION RULE:** mọi Content Angle phải trace ngược qua Topic/Verified Insight tới evidence; giữ Human Selection và typed Content Intelligence Packet. Value Scene không phải lý do tự bịa tình huống, động cơ hay mong muốn còn thiếu, và không thêm field vào schema Phase 2.

## Cách dùng và phase gate

Trước thay đổi architecture/product logic, đọc đủ `docs/v2/00`–`10`, đối chiếu quyết định, bằng chứng và phạm vi được phép. Nếu implementation mâu thuẫn accepted decisions hoặc Strategyzer foundations: **STOP and report**; không âm thầm diễn giải lại nền tảng để hợp thức hóa code.

Current Phase = Phase 2 — Customer Context. Status = IMPLEMENTED — PENDING ARCHITECT REVIEW. Next Phase = DO NOT START. Đây là memory patch chỉ tài liệu; không đổi extraction behavior, không mở Phase 3.
