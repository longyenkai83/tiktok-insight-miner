# 03 — EVIDENCE RULES

## Phân biệt điều quan sát và điều kết luận

OBSERVED chỉ có nghĩa hệ thống ghi nhận được lời nói hoặc metadata từ nguồn. Nếu khách nói “sản phẩm X gây Y”, chỉ được trình bày đó là lời khách phản ánh; chưa thể khẳng định X thực sự gây Y. Chuẩn hóa ý nghĩa, phân biệt user/buyer khi cần hoặc suy nguyên nhân là DERIVED/HYPOTHESIS tùy bằng chứng.

DERIVED phải có phương pháp, input refs, scope và giới hạn. HYPOTHESIS phải nêu điều chưa biết, giả định và kế hoạch kiểm chứng. PROPOSED là lựa chọn hành động/biên tập, không là bằng chứng.

Không tự nâng truth_type vì model confidence cao, nhiều lần model trả cùng câu, nhiều like, người dùng tick duyệt, persona trông hợp lý hoặc config được chủ dự án viết. Bằng chứng mới tạo version đánh giá mới, giữ lịch sử; không sửa quá khứ để hợp thức hóa kết luận.

## Truy vết bắt buộc

Mỗi claim khách hàng DERIVED trong Insight phải đi được tới comment gốc qua Evidence và SourceRecord. Signal/Pattern refs giải thích cách kết luận, không thay thế nguồn. Kiểm cả sự tồn tại của ID, version/hash, nội dung span và quan hệ hỗ trợ; một URL đúng không đủ để chứng minh claim.

Provenance phải bắt đầu ở Source/Signal, không đợi tới tầng Evidence. Không lấy report do AI viết, summary cũ, meta-pain, persona, niche config hay bài Writer làm nguồn OBSERVED thay comment. Các nguồn đó chỉ có thể là giả định/định hướng có nhãn riêng. Brand facts có nguồn doanh nghiệp được kiểm chứng phải nằm namespace riêng, không được tính vào số khách nói điều gì.

## Quote và số liệu

- Quote phải khớp span của canonical_text trong đúng snapshot. Dấu lược bỏ phải thể hiện rõ và dùng nhiều span; không nối hai người thành một quote.
- Paraphrase ghi là diễn giải và trace về quote; không đặt trong dấu trích dẫn như lời nguyên văn.
- Redaction phải có ghi nhận; không phục hồi phần đã che bằng suy đoán. Không lộ PII khi đưa evidence vào packet.
- Likes/replies phải khớp metadata nguồn tại thời điểm thu thập. Thiếu số là null; không dùng 0 hay số mặc định tạo cảm giác đã đo.
- Số tính toán phải có công thức, input refs, mẫu số, scope, thời điểm. Tỷ lệ trong mẫu comment không đại diện tỷ lệ thị trường hoặc tỷ lệ người mua.
- Không bịa phần trăm dưới tên gọi “tu từ”, không bịa case, doanh thu, kết quả, timeline hoặc quote để viết hấp dẫn hơn.

## Pattern, phản chứng và giới hạn mẫu

Một comment nhiều signal vẫn là một source comment khi đếm support. Dedup repost/import và giữ quy tắc dedup; không coi tác giả ẩn danh là nhiều người chắc chắn khác nhau. Engagement có thể dùng làm metadata ưu tiên nghiên cứu, không tự chứng minh tính đúng hay độ phổ biến pain.

Phải nêu phạm vi lấy mẫu, kênh, thời gian, truy vấn, missing data và khả năng selection bias. Insight phổ quát không thể dựa vào một comment đơn lẻ. Tiêu chuẩn đủ support, clustering và ranking còn chờ review; Phase 0 không đặt ngưỡng số tùy ý.

Giữ evidence SUPPORTS, CONTRADICTS và CONTEXT. Khi nguồn mâu thuẫn, thu hẹp scope hoặc giữ nhiều giả thuyết; không bỏ phản chứng để đạt confidence mong muốn. Không tìm phản chứng và không tìm thấy là hai trạng thái khác nhau.

## Điều kiện chuyển sang nội dung

Chỉ claim OBSERVED/DERIVED đủ kiểm chứng provenance, phù hợp scope, đã đi qua Insight và Human Selection mới được đưa vào allowed_customer_claims. Giả thuyết có thể nằm trong phần nghiên cứu riêng nhưng không được dùng như fact trong câu hỏi dẫn dắt, kể chuyện, hook hoặc CTA. Khi cần claim mới: quay lại nghiên cứu/evidence, tạo version mới và review lại selection.

Phê duyệt Angle không xác minh rằng lời tự nhận của khách là đúng ngoài đời. Nội dung phải giữ attribution và giới hạn này. Writer không đọc thêm persona/config rồi âm thầm bổ sung customer truth.

## Ví dụ minh họa tổng hợp — KHÔNG phải dữ liệu audit/khách hàng

Giả sử source giả lập S-demo có câu “Tôi mất nhiều thời gian tổng hợp báo cáo”.

| Claim minh họa | truth_type và xử lý |
|---|---|
| Người viết S-demo nói nguyên văn câu trên | OBSERVED trong fixture giả lập, không dùng làm evidence thực |
| Người viết mô tả gánh nặng thời gian của việc tổng hợp | DERIVED, scope một người, trace S-demo |
| Người này là CFO và sẵn sàng trả tiền cho phần mềm | HYPOTHESIS chưa có bằng chứng; không gửi như fact cho Writer |
| Đề xuất chủ đề giảm thao tác tổng hợp | PROPOSED, cần insight thật và human review trước nội dung thật |

## Bộ kiểm cần có khi triển khai sau review

Thiếu source, quote lệch, likes bịa, source version đổi, inference không có evidence, đếm trùng signal, user/buyer suy từ @mention, giả thuyết trộn vào facts, selected_angles được nhận như packet, hoặc auto-top giả làm human approval đều phải có trường hợp kiểm âm. Đây là tiêu chí thiết kế cho phase sau; chưa có validator/test V2 được triển khai trong Phase 0.
