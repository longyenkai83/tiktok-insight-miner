# WRITE RULES — Base (Generic)

> **Vai trò**: Luật viết chung **cho mọi output content** sinh ra bởi tool này (caption, script, brief, post...).
>
> **Đối tượng**: Bất kỳ user nào, bất kỳ brand nào, bất kỳ ngành nào.
>
> **Quan hệ với brand-specific rules**: File này là **base layer**. Mỗi brand có file `profiles/<brand>/write_rules.md` riêng để **extend / override** các luật ở đây cho phù hợp giọng riêng.

---

## 1. Nguyên tắc cốt lõi (8 rule)

### 1.1 Bám vào comment / quote thật

- Mỗi angle / brief PHẢI link rõ tới ≥ 1 quote thật từ comment audience
- Reference quote nguyên văn trong script hoặc text overlay (proof of demand)
- KHÔNG generate insight không có nguồn

### 1.2 Không bịa câu chuyện cá nhân

- Tool không được thêm chi tiết cá nhân không có trong source data (persona file, niche config)
- Nếu brand cần case study → user/brand cung cấp story, AI chỉ format
- Câu nói dạng "Mình từng làm việc X 10 năm" — chỉ dùng nếu fact đó có trong `profiles/<brand>/about.md`

### 1.3 Không hứa kết quả quá đà

❌ TRÁNH:
- "Khoá học giúp bạn kiếm 100tr/tháng"
- "7 ngày thay đổi cuộc đời"
- "Theo công thức này 100% thành công"
- "Triệu phú X tuổi", "Làm giàu nhanh"

✅ THAY BẰNG:
- "Cách bạn có thể bắt đầu xây thu nhập"
- "Một góc nhìn để dừng lại và nghĩ"
- "Có người đã thử và đây là kết quả của họ" (cite cụ thể)

### 1.4 Không viết giọng guru / lên lớp

❌ TRÁNH:
- "Bạn cần phải hiểu rằng..."
- "Tôi sẽ chỉ cho bạn cách..."
- "Đây là bí mật mà không ai dạy bạn"
- "Hãy tin vào bản thân mình", "Đừng bỏ cuộc"
- "Bạn xứng đáng được X" (lặp đi lặp lại)

✅ THAY BẰNG:
- "Mình từng nghĩ X. Cho đến khi..."
- "Có một góc nhìn khác mình muốn chia sẻ"
- "Hôm nọ đọc một comment làm mình suy nghĩ..."

### 1.5 Không sáo rỗng

Câu sáo rỗng = câu có thể áp vào BẤT KỲ chủ đề nào nếu đổi danh từ. Ví dụ:

❌ "Hành trình thay đổi bản thân là một chuyến đi đầy ý nghĩa"
- Có thể đổi "thay đổi bản thân" → "kinh doanh" / "làm mẹ" / "tập gym" → vẫn fit
- → SÁO

✅ "Mình quyết định đóng tiệm bánh sau 2 năm. Không phải vì thất bại — mà vì có một buổi chiều con ngồi đợi một mình và mình không có mặt ở đó."
- Cụ thể chi tiết, không generic
- → SẠCH

### 1.6 Viết rõ, có insight, có hành động nhỏ

Mỗi bài / brief PHẢI có 3 thành phần:
1. **Sự thật rõ** (1 câu cụ thể, không vague)
2. **Insight / góc nhìn** (1 idea người đọc có thể mang về)
3. **Hành động nhỏ** (1 việc người đọc có thể làm hôm nay, không cần đầu tư lớn)

Thiếu 1 trong 3 → bài chưa xong.

### 1.7 CTA mềm, không ép bán

❌ TRÁNH:
- "Chỉ còn X suất — đăng ký ngay!"
- "Like nếu bạn đồng ý, share cho người cần"
- "Comment GIÁ để biết thêm"
- "Inbox NOW"
- FOMO + khan hiếm giả tạo

✅ THAY BẰNG:
- Lời mời: "Nếu bạn cũng đang ở đó, comment 1 từ mình biết bạn không một mình"
- Save-share dạng tự nhiên: "Lưu lại nếu cần đọc lại sau"
- Question CTA: "Bạn nghĩ sao? Em muốn nghe góc nhìn của bạn"

### 1.8 Production brief vẫn cần người duyệt

- Output AI là **draft 1**, KHÔNG phải final
- Anh / brand owner phải đọc qua trước khi giao team quay
- Edit Big idea / Hook / Caption cho khớp tone cá nhân
- Veto angle off-brand

→ Tool **augment** judgement, KHÔNG **replace** judgement.

---

## 2. Luật về cấu trúc

### 2.1 Mở bài

❌ KHÔNG mở bằng:
- Lời chào ("Xin chào!", "Hi cả nhà!")
- Giới thiệu bản thân ("Mình là X, hôm nay mình muốn chia sẻ...")
- "Có một câu chuyện..." / "Có một người..." / "Có một kiểu..." (dạng AI tone leakage)
- "Bạn có biết rằng..." / "Bạn đã bao giờ..." (clichés)
- Statistics rời rạc không context

✅ MỞ BẰNG:
- Sự thật cứng (1 câu cụ thể trực diện)
- Khoảnh khắc cụ thể (in medias res — bắt đầu từ giữa hành động)
- Câu hỏi nội tâm (câu hỏi người đọc đang mang nhưng chưa dám nói ra)
- Nghịch lý (đặt 2 thứ mâu thuẫn cạnh nhau)

### 2.2 Kết bài

❌ KHÔNG kết bằng:
- Recap dài dòng các điểm đã nói
- "Hy vọng bài viết hữu ích"
- "Cảm ơn các bạn đã đọc"
- "Đừng quên like, share, follow"

✅ KẾT BẰNG:
- 1 câu neo (thứ người đọc mang theo sau khi đóng app)
- 1 câu hỏi mở (để người đọc tự suy nghĩ)
- CTA mềm dưới dạng lời mời

### 2.3 Độ dài

- **Đủ dài để nói hết điều cần nói — KHÔNG dài hơn**
- Nếu 1 đoạn bỏ đi mà bài vẫn đủ nghĩa → bỏ đi
- Mỗi câu phải có: sự thật, chi tiết cụ thể, hoặc đẩy câu chuyện tiến về phía trước

---

## 3. Luật về ngôn ngữ

### 3.1 Show don't tell

❌ "Điều này rất quan trọng vì..."
✅ Cho thấy tại sao quan trọng qua chi tiết cụ thể

❌ "Cảm xúc rất mạnh"
✅ Mô tả thân thể: "tay run, miệng khô, ngực thắt"

### 3.2 Tránh inflation (thổi phồng tầm quan trọng)

❌ "Khoảnh khắc đó đánh dấu một bước ngoặt quan trọng trong hành trình phát triển bản thân"
✅ "Mình đóng cửa tiệm sau 2 năm. Buổi chiều đó con ngồi đợi một mình."

### 3.3 Đặt fact lên trước, nhận xét sau

❌ "Đây là một câu hỏi rất hay từ một người đọc của mình"
✅ "Hôm qua có người hỏi: '...'"

### 3.4 Không elegant variation gượng gạo

Nếu từ đúng là "chuyên môn" — gọi là chuyên môn cả bài. Đừng tìm "năng lực", "kỹ năng", "thế mạnh" để xen kẽ cho có vẻ đa dạng.

### 3.5 Vague attributions

❌ "Các chuyên gia nói rằng..."
❌ "Nghiên cứu cho thấy..."
✅ Cite cụ thể: "Theo báo cáo X năm Y, tác giả Z nói rằng..."
✅ Nếu không có nguồn → KHÔNG dùng câu đó

### 3.6 Khi không có thông tin → nói thẳng là không có

❌ Đừng đoán hoặc lấp đầy bằng câu mơ hồ
✅ "Mình chưa có data về điều này" / "Cái này mình chưa biết — sẽ tìm hiểu thêm"

---

## 4. Luật về định dạng

### 4.1 Bold

- Dùng **tiết kiệm** — chỉ khi thực sự cần nhấn mạnh
- KHÔNG bold mọi từ khoá
- Không dùng bold để "trang trí" làm bài trông sang

### 4.2 Bullet points

- Dùng khi liệt kê thực sự cần (3+ items độc lập, không có narrative flow)
- KHÔNG dùng cho mọi thứ
- Bài kể chuyện ưu tiên đoạn văn chảy tự nhiên

### 4.3 Headings

- Chỉ cho bài DÀI cần điều hướng
- Bài kể chuyện thường KHÔNG cần heading

### 4.4 Emoji

- KHÔNG dùng trong heading
- KHÔNG dùng làm dấu phân đoạn
- Dùng tiết kiệm — chỉ khi đúng tone brand cho phép

### 4.5 Dấu chấm than

- Hạn chế (1-2 lần / bài tối đa)
- KHÔNG dùng để giả lập emotion

---

## 5. The test — Kiểm tra trước khi xuất bản

Trước khi giao bất kỳ output nào (caption, brief, script):

1. **Generic test**: Đoạn này có thể áp dụng cho BẤT KỲ chủ đề nào nếu đổi danh từ không?
   - Có → quá chung chung, viết lại với chi tiết cụ thể

2. **Show don't tell**: Có câu nào đang nói "điều này quan trọng" thay vì cho thấy tại sao?
   - Có → cắt bình luận, để sự thật tự nói

3. **Banned phrases check**: Có cliché / sáo ngữ / từ guru nào trong bài?
   - Có → viết lại

4. **Human test**: Một người thực sự hiểu chủ đề có viết như vậy không? Có nghe như thông cáo báo chí / Wikipedia không?
   - Sai giọng → viết lại

5. **3 thành phần test**: Bài có đủ (1) sự thật rõ + (2) insight + (3) hành động nhỏ?
   - Thiếu 1 → chưa xong

---

## 6. Cách áp dụng trong tool này

### 6.1 Khi production.py generate brief

System prompt của Claude phải inject:
- Toàn bộ rules từ file này (base)
- + override / extension từ `profiles/<brand>/write_rules.md`

### 6.2 Khi nhân viên / anh edit thủ công

Trước khi save final, chạy qua "The test" mục 5.

### 6.3 Khi onboard nhân viên content mới

Đọc file này TRƯỚC, rồi đọc tiếp file brand-specific.

---

## 7. Lifecycle của file này

- File này **stable** — chỉ update khi có insight thực về luật viết phổ quát
- KHÔNG nhồi giọng riêng 1 brand vào đây
- Brand-specific rules → file riêng `profiles/<brand>/write_rules.md`

---

**Updated**: 2026-05-09 · v1 (initial — đúc kết từ MVP "kinh-doanh-27-45")

**Tài liệu liên quan**:
- [VOICE_PROFILE_TEMPLATE.md](VOICE_PROFILE_TEMPLATE.md) — Template để mỗi brand điền voice riêng
- [MVP_WORKFLOW.md](MVP_WORKFLOW.md) — Cách dùng file này trong workflow hàng ngày
- [SOP_BUILD_INSIGHT_V1.md](SOP_BUILD_INSIGHT_V1.md) — Quy trình build insight chung
