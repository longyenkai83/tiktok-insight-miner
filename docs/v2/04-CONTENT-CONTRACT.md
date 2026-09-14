# 04 — CONTENT CONTRACT

## Quy tắc đã chốt và phạm vi đề xuất

Insight → Reelo bắt buộc dùng typed Content Intelligence Packet. Content chỉ được tạo sau Insight; Angle/Topic là các đề xuất biên tập sau Insight, Human Selection nằm sau Angle. Writer được sáng tạo cách diễn đạt, không sáng tạo customer truth. Đây là nguyên tắc ACCEPTED; cấu trúc serialize, lỗi và kết quả cụ thể dưới đây là PROPOSED cho review, chưa được cài vào runtime.

Contract dữ liệu nằm tại [02-DATA-SCHEMA.md](02-DATA-SCHEMA.md); provenance theo [03-EVIDENCE-RULES.md](03-EVIDENCE-RULES.md). Markdown là view cho người đọc, không là schema trao đổi chuẩn. Không coi `selected_angles.json`, brief Markdown hay pack Drive hiện tại là packet V2 chỉ bằng cách đổi tên.

## Hợp đồng qua các tầng

| Bên giao → bên nhận | Điều kiện |
|---|---|
| Source → Audience / Role / Context | Có snapshot, locator, thời điểm; thuộc tính thiếu không tự điền bằng persona |
| Audience / Role / Context → Customer Signals | Customer Identity B2C có nhãn và provenance; user/buyer chỉ khi cần, không dùng giả thuyết như fact |
| Customer Signals → Pattern | 0..n signal/comment; grouping truy được nguồn và không đếm signal thành người |
| Pattern → Evidence | Giữ inclusion/exclusion và scope; xác minh quote/metadata, thu thập cả phản chứng |
| Evidence → Insight | Claim có support đúng nghĩa, derivation, scope và limitations; giả thuyết tách riêng |
| Insight → Topic → Angle | Dùng insight đủ điều kiện; proposal tham chiếu claim, không thêm sự thật mới |
| Angle → Human Selection | Người duyệt đúng phiên bản Angle và nền bằng chứng; máy chỉ gợi ý |
| Human Selection → Packet | APPROVED còn hiệu lực, snapshot đầy đủ, refs phân giải được |
| Packet → Reelo Writer | Kiểm type/version/eligibility trước tạo draft; không fallback sang legacy pack |
| Reelo Writer → Unified Agent | Trả draft, packet_ref, claim_usage và findings; Agent giữ trạng thái review, không tự publish |

Các tầng được dùng evidence/context từ tầng trước qua refs rõ ràng và snapshot đã kiểm, không bắt buộc chỉ nhìn một object liền trước. Cấm đọc nguồn phụ ngầm để bổ sung customer facts.

## Content Intelligence Packet: điều kiện bàn giao

Packet là snapshot bất biến có `packet_type`, `schema_version`, `packet_id`, `packet_version`. Nó mang nội dung đủ để Writer kiểm hiểu độc lập: Topic, Angle, Insight, Evidence, source excerpts, context, profile, human approval, allowed claims/quotes/numbers, brand context riêng và voice/writing rules đã snapshot. Ref ngoài chỉ phục vụ truy xuất nguồn sâu hơn, không thay nội dung bắt buộc.

Mỗi claim phải truy tới source comment; metric và quote không bị cắt âm thầm. Source excerpt phải đủ vùng context để không làm sai nghĩa. Không đóng gói toàn bộ raw riêng tư nếu không cần. Hash/version giúp nhận ra chỉnh sửa, không thay kiểm chứng nội dung nguồn.

Human approval gắn với exact Angle và các input versions. Nếu nội dung bằng chứng, insight, Angle hoặc giới hạn claim thay đổi thì selection cũ không còn đủ; packet mới phải được review lại. Máy không được chuyển `selected_by=auto` sang human hoặc tạo approval mặc định. Lựa chọn legacy chỉ là dữ liệu đầu vào cần đối chiếu, không kế thừa quyền approved V2.

## Writer được và không được làm

Writer được đổi bố cục, nhịp, hook, ví dụ minh họa phi thực chứng được ghi rõ, ẩn dụ và cách giải thích; không bắt buộc copy tối thiểu năm từ hoặc giữ regex V1. Mọi diễn đạt phải giữ nguyên nghĩa, attribution, scope và độ chắc chắn của claim được phép.

Writer không được tạo thêm pain, job, gain, audience segment, user/buyer, động cơ, số liệu, lời khách, case thực tế hoặc kết quả sản phẩm. Không làm câu “một comment phản ánh” thành “khách hàng đều gặp”. Không biến research_hypotheses thành fact bằng cách bỏ nhãn. Giọng thương hiệu và config chỉ điều khiển diễn đạt, không xác thực customer truth.

Brand fact/offer/giá chỉ được dùng nếu có nguồn riêng đã kiểm và được cho phép trong packet; nếu thiếu, trả yêu cầu bổ sung. Không mặc định cấm toàn bộ commercial content theo prompt V1, cũng không tự phát minh offer để điền CTA.

## Từ chối và vòng phản hồi

Các mã lỗi dự kiến: UNSUPPORTED_SCHEMA, BROKEN_PROVENANCE, INVALID_QUOTE, INVALID_NUMBER, UNAPPROVED_SELECTION, STALE_SELECTION, UNSUPPORTED_CLAIM, MISSING_CONTEXT. Một lỗi phải chỉ ra record/claim và lý do; không silently downgrade, lấy persona bù hoặc dùng production V1 làm fallback.

Nếu chỉ sai diễn đạt, Writer sửa trong phạm vi packet rồi kiểm lại. Nếu thiếu customer truth, dừng và trả về research/evidence; không viết để lấp chỗ trống. WriterResult mang claim_usage (span nội dung → claim/quote/number refs), findings và trạng thái chờ review. Không tuyên bố PASS chỉ vì hoàn thành một lượt rewrite, và không tự publish.

Unified Agent trong thiết kế tương lai quản lý run/step state, provenance, lỗi, resume và các human gate. Cơ chế orchestration, retry, storage, transport và giới hạn rewrite vẫn OPEN; không kế thừa mặc định vòng sửa của Reelo/V1. Việc audit đã được duyệt không cấp quyền chạy Agent V2.
