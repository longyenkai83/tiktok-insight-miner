# 03 — EVIDENCE RULES

## Phase 3 — membership, support và giới hạn ngữ nghĩa

Input phải khớp artifact hash và từng joined source hash, không tự chữa mismatch. Một context thiếu không chặn signals; orphan context không được tạo pattern. Input partial/error và validation issues được giữ trong snapshot/envelope, không biến lỗi extraction thành bằng chứng hoàn chỉnh.

Closed catalog chỉ lấy accepted claims sau Phase 1/2 source-span validation. Model chỉ trả pair IDs/relation kind; unknown member, self relation, invalid truth/fields, duplicate/conflicting pair hoặc merge khác category bị loại. Semantic provider lỗi giữ exact baseline có issue và semantic_status=error, không báo semantic success.

Code không chứng minh semantic relation là đúng: same meaning/variation/possible contradiction đều DERIVED, cần human review. Labels dùng quote đại diện, không thêm facts; label nguyên văn vẫn có thể không đại diện hết group. Context distribution/wording variants hiển thị khác biệt, không chốt final segments. Complete-link hạn chế over-merge nhưng có thể over-split khi model bỏ sót pair.

Phản chứng giữ source ref và không được cộng vào support của group bị phản bác. Search status CHECKED_WITHIN_INPUT chỉ khi semantic pass hợp lệ; NOT_CHECKED cho exact-only/error. Chưa thấy phản chứng trong accepted claims không đồng nghĩa không tồn tại; rejected extraction/raw text chưa thành claim không được tự thêm thành member.

Support đếm một source comment một lần dù có nhiều signals. Missing metrics = null với coverage; known zero khác unknown. Không threshold thành công, priority score, automatic strong_candidate hay verified. Recurrence chỉ mô tả sample, không suy speech thành behavior/payment/market demand. Cùng nguyên tắc Strategyzer, B2C và truth types.

## Phase 2 — cùng quy tắc nguồn, thêm context candidates

Chỉ OBSERVED/DERIVED; model trả field + quote/confidence/truth type theo comment ID, code tạo claim từ exact source span. Source hash/span và helper validation được dùng chung với Phase 1, kiểm cả khi deserialize contexts.json. Không tạo tuổi/giới/thu nhập/địa lý/nghề/gia đình/ownership/purchase stage/motivation không có trong nguồn. Video topic/author metadata không được dùng suy audience. Field lạ/B2B/free-form claim bị schema từ chối; quote không có trong nguồn bị loại riêng có issue/index/field.

Field assignment vẫn là candidate per comment và cần review ngữ nghĩa: substring đúng không chứng minh câu đùa, giả định hay lời kể về người khác mô tả chính tác giả. Prompt yêu cầu giữ phủ định/uncertainty và đủ context, không ép classification. Không coi `audience_segment` là cluster của nhiều comment; Phase 3 giữ context variants, chưa chốt final segment.

Product Opportunity là PROPOSED; xác thực demand cần Assumption → Experiment → Evidence → Decision trong phase tương lai. Không tự nâng customer truth vì có ý tưởng sản phẩm, Value Map, confidence hoặc approval.

## Phase 1 — hậu kiểm đã triển khai

`signal_extractor.validate_batch()` xử lý JSON theo từng item sau structured output bằng JSON Schema sinh từ Pydantic. Dùng `messages.create(output_config=...)` thay `messages.parse()` để một claim sai kiểu không làm mất toàn batch trước khi salvage. Chỉ log issue code, ID/index và token/cache counters, không log lời khách hay exception body/API key.

- Unknown model ID: loại record lạ, ghi envelope issue; missing ID: giữ source với status error; duplicate ID: không chọn tùy tiện một bản, trả error cho ID đó.
- Input ID trùng hoặc không có locator hợp lệ: từ chối input trước API, không tạo ID giả.
- Quote phải có trong source sau duy nhất whitespace normalization, phân biệt hoa/thường, dấu và punctuation. Lưu lại exact source span; không gộp quote của nhiều comment.
- Phase 1.1 không yêu cầu model sinh claim. Code chỉ tạo claim từ exact source span sau khi evidence_quote đã hợp lệ; không sửa quote bịa/paraphrase. Trường claim/demographic/context ngoài transport bị loại. HYPOTHESIS/PROPOSED không qua schema Phase 1.
- Claim lỗi loại riêng và có issue/index; comment có lỗi item là partial kể cả không còn claim, không đánh nhầm no_signal. no_signal chỉ là response hợp lệ với signals rỗng. Record/batch không dùng được là error.
- LANGUAGE phải OBSERVED và literal; repeated_expressions chỉ hợp lệ khi lặp ít nhất hai lần trong chính comment. Đây không phải corpus-level repetition; lặp xuyên comment thuộc language bank Phase 3, không sửa Phase 1.
- API/refusal/truncated/JSON lỗi tạo error records để không mất nguồn. Authentication error dừng các request còn lại; artifact vẫn giữ đủ source cùng lỗi. Không biến API failure thành empty success.

Giới hạn: code bảo đảm nguồn text/ID/shape và ngăn claim thêm lời, không chứng minh nhãn category hay cách hiểu sarcasm của model luôn đúng. Confidence là mức tự đánh giá, không là bằng chứng. Cần architect review chất lượng trước giai đoạn sau; semantic entailment/paraphrase tự do chưa triển khai.

## Phân biệt điều quan sát và điều kết luận

OBSERVED chỉ có nghĩa hệ thống ghi nhận được lời nói hoặc metadata từ nguồn. Nếu khách nói “sản phẩm X gây Y”, chỉ được trình bày đó là lời khách phản ánh; chưa thể khẳng định X thực sự gây Y. Chuẩn hóa ý nghĩa, phân biệt `user_buyer_distinction` (optional) khi cần hoặc suy nguyên nhân là DERIVED/HYPOTHESIS tùy bằng chứng.

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

Thiếu source, quote lệch, likes bịa, source version đổi, inference không có evidence, đếm trùng signal, `user_buyer_distinction` (optional) suy từ @mention, giả thuyết trộn vào facts, selected_angles được nhận như packet, hoặc auto-top giả làm human approval đều phải có trường hợp kiểm âm. Đây là tiêu chí thiết kế cho phase sau; chưa có validator/test V2 được triển khai trong Phase 0.
