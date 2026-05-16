# 🪶 Chị Hiền Expression Bank v1

> **Vai trò**: Ngân hàng **biểu đạt tiếng Việt** giúp câu chữ thuận miệng, có khẩu cảm Việt, ít lửng củng, ít giống câu dịch, ít văn mẫu AI. Đây **không phải Writing Rules** — Writing Rules nói "phải làm gì", file này gợi "có thể nói thế nào".
>
> **Đối tượng**: anh / nhân viên content / Claude khi cần draft hoặc rewrite câu mà câu cũ "đúng ý nhưng nghe chưa thuận miệng".
>
> **Source**:
> - `profiles/chi-hien/write_rules.md` v2.2 — đặc biệt **mục II.5** (Câu đúng ý chưa đủ — phải thuận miệng tiếng Việt)
> - `profiles/chi-hien/voice_profile.md` v2.0 — 5 chất voice (Ấm / Rõ / Đẹp / Vững / Thực tế)
> - D1–D10 đã viết (rút câu thật đã pass)
>
> **Generated**: 2026-05-10 · v1

---

## 0. Cách dùng file này — 5 nguyên tắc

1. **Không copy máy móc.** Mỗi cụm là gợi ý biểu đạt, không phải câu sẵn để dán.
2. **Insight thật là lõi.** Expression Bank không thay insight — nó chỉ giúp insight đã có được nói thuận miệng hơn.
3. **Voice là nhạc trưởng.** Khi 1 cụm trong bank conflict với voice 5 chất → bỏ cụm, giữ voice.
4. **Không dùng từ đẹp để che insight yếu.** Nếu insight chưa rõ → quay lại pipeline, đừng tô son cho câu rỗng.
5. **Đọc to trong đầu** sau khi viết: *"Một phụ nữ Việt 27–45 có thật sự nghĩ hoặc nói câu này không?"* Nếu không → rewrite, không giữ vì câu "có vẻ đẹp".

---

# 1. Vietnamese Naturalness Examples

> Câu **đúng ý nhưng nghe chưa thuận miệng** vs câu **đời hơn, có khẩu cảm Việt**.

| ❌ Lửng củng / câu viết / hơi dịch | ✅ Đời hơn, thuận miệng |
|---|---|
| Chắc không ai đỡ kịp mình đâu. | Mình buông ra thì mọi thứ sẽ rối. |
| Câu hỏi bạn dành cho ai cũng được, trừ chính mình. | Bạn hay hỏi người khác cần gì. Nhưng lâu rồi, bạn quên hỏi chính mình câu đó. |
| Cảm xúc của bạn không phải là trách nhiệm của riêng bạn. | Cảm xúc của người khác — không phải cảm xúc của bạn. |
| Bạn đang trải qua sự kiệt sức về mặt cảm xúc. | Có những hôm bạn thấy mệt mà không gọi tên được. |
| Hãy cho phép bản thân được nghỉ ngơi. | Cho phép mình ngồi yên một phút. |
| Bạn cần kết nối sâu hơn với nội tâm của mình. | Dừng lại đủ lâu để nghe thấy chính mình. |
| Việc tự chăm sóc bản thân là rất quan trọng. | Có những việc nhỏ chỉ mình bạn biết là mình đang cần. |
| Bạn xứng đáng có một cuộc sống tốt đẹp hơn. | Bạn không cần trở thành ai khác để bắt đầu. |
| Đó là một hành trình dài để tìm lại chính mình. | Phần khó nhất không phải là bắt đầu — là dừng lại đủ lâu để biết bắt đầu từ đâu. |
| Hãy yêu bản thân mình nhiều hơn. | Hôm nay, để dành lại cho mình một câu — ngắn cũng được. |

### Nguyên tắc đối chiếu

- **Câu lửng củng** thường có: cấu trúc bị động, danh từ hoá ("sự kiệt sức"), trạng từ thừa ("mặt cảm xúc"), từ Anh-Việt ngắc ngứ ("kết nối sâu"), khẳng định trống ("rất quan trọng"), slogan ("hãy yêu bản thân").
- **Câu thuận miệng** thường: ngắn hơn, có chủ ngữ rõ, dùng động từ đời thường, có 1 hình ảnh hoặc 1 khoảnh khắc cụ thể, có khoảng nghỉ (dấu gạch ngang / xuống dòng).

---

# 2. Anchor Sentence Bank

> Câu **neo** — ngắn, có lực, dùng để **kết đoạn** hoặc tạo **điểm rơi** giữa bài. Không sáo, không slogan.

### 2.1 Câu neo signature (xuyên suốt brand)

- *Dừng lại đủ lâu để nghe thấy chính mình.*
- *Thứ bạn cần không phải là thêm — mà là rõ hơn.*
- *Bạn không cần trở thành ai khác để bắt đầu.*
- *Tự do không ai trao cho bạn. Bạn phải tự xây.*
- *Mình từng ở chỗ bạn đang đứng.*

### 2.2 Câu neo theo Layer

**Inner Clarity / Self-worth**:
- *Cuối cùng vẫn phải là mình thôi.*
- *Nhỏ thôi. Nhưng là của bạn.*
- *Trời không sập.*
- *Bạn không một mình. Chỉ là bạn đã quen ở một mình.*

**Behavior / Role Burden**:
- *Mình buông ra thì mọi thứ sẽ rối.*
- *Bạn rất nhạy. Chỉ là độ nhạy đó chưa quay về với chính bạn.*
- *Câu đó nhanh đến mức — bạn không kịp nghe câu hỏi của mình.*

**Body Wisdom**:
- *Cơ thể là người cuối cùng lên tiếng. Khi nó nói, thường đã muộn.*
- *Vai nặng từ lúc nào, bạn không nhớ.*

**Permission / Self-compassion**:
- *Cho phép mình buồn. Đừng cho phép mình tự trách. Hai cái đó khác nhau.*
- *Bạn được phép dừng — không vì ai cả.*

### 2.3 Nguyên tắc viết câu neo mới

- ≤ 12 chữ là lý tưởng. Vượt 16 chữ → cắt.
- 1 hình ảnh **hoặc** 1 đối lập, không cả hai trong cùng câu neo.
- Đứng riêng 1 dòng. Không ghép vào đoạn dài.
- Không dùng dấu chấm than. Không "hãy", "phải", "cần".

---

# 3. Contrast Pair Bank

> Cặp tương phản **mềm** — không "tốt vs xấu", mà "bên ngoài vs bên trong" / "biểu hiện vs gốc".

### 3.1 Cặp gốc

| Bên ngoài / biểu hiện | Bên trong / sự thật |
|---|---|
| chăm người khác | bỏ quên mình |
| làm được nhiều | không còn nhẹ |
| gồng để ổn | không thật sự ổn |
| có mặt cho mọi người | vắng mặt với chính mình |
| trả lời nhanh cho người khác | quên hỏi chính mình |
| chu đáo với mọi người | xa lạ với nhu cầu của mình |
| giữ mọi thứ gọn | bên trong đang rối |
| nói "mình ổn" | chưa kịp hỏi mình thật sự thế nào |

### 3.2 Cặp dùng cho từng Layer

**Inner Clarity**:
- biết nhiều / chưa thấy rõ
- học thêm / chưa hiểu mình thêm
- bận / không nghĩ

**Behavior / Role Burden**:
- nhận việc nhanh / mệt chậm
- ôm hết / cô đơn trong gánh
- không ai bắt / vẫn tự nhận

**Money & Safety** (dùng từ D22+):
- có tiền / chưa có quyền chọn
- thu nhập tăng / khoảng thở giảm

**Life Freedom** (dùng từ D22+):
- tự do đi / không tự do dừng
- chọn được lịch / chưa chọn được nhịp

### 3.3 Cách dùng

- Đặt 2 vế **cạnh nhau** trong cùng câu hoặc 2 câu liền kề.
- Vế bên ngoài đứng trước → vế bên trong đứng sau (đào sâu).
- KHÔNG dùng "nhưng" thẳng thừng — dùng "—", xuống dòng, hoặc "chỉ là".

---

# 4. Emotional Verb Bank

> Động từ **đời thường** — chính xác hơn "cảm thấy", "trải qua", "đối mặt".

### 4.1 Động từ về gánh / giữ / né

| Động từ | Sắc thái | Ví dụ |
|---|---|---|
| **ôm** | nhận quá nhiều việc, không chia | *"bạn ôm hết việc về mình"* |
| **gồng** | giữ tư thế cứng để chịu, mệt mà không show | *"bạn đang gồng cho mọi thứ ổn"* |
| **giữ** | không muốn buông, lo nếu buông sẽ rối | *"bạn vẫn thấy phải tự giữ mọi thứ"* |
| **né** | tránh né cảm xúc / sự thật bằng hành vi bề mặt | *"bạn né câu hỏi đó bằng cách nhận thêm việc"* |
| **lờ đi** | nghe thấy nhưng không quay lại | *"nhu cầu nhỏ đó bị lờ đi mỗi ngày"* |
| **đè xuống** | chủ động ấn cảm xúc cho khuất | *"bạn đè cảm giác mệt xuống để làm cho xong"* |
| **nén lại** | giữ trong lòng, không cho ra | *"bạn nén câu trả lời lại — và cười"* |

### 4.2 Động từ về buông / chậm / nghe

| Động từ | Sắc thái | Ví dụ |
|---|---|---|
| **buông ra** | thả nhẹ, không phải bỏ | *"thử buông ra một việc — chỉ một"* |
| **đặt xuống** | có ý thức, có chủ định | *"đặt câu hỏi đó xuống ít nhất một phút"* |
| **nhìn lại** | quay đầu, không vội đi tiếp | *"ngồi yên đủ lâu để nhìn lại"* |
| **gọi tên** | đặt tên chính xác cho điều đang có | *"gọi tên nỗi sợ — không cần xử lý nó"* |
| **ngồi yên** | không làm gì, không phải lười | *"ngồi yên một phút trước khi mở thêm tab"* |
| **đi chậm lại** | giảm nhịp, không phải dừng hẳn | *"đi chậm từ phòng này sang phòng khác"* |
| **nghe lại mình** | quay vào lắng nghe nội tâm | *"hôm nay thử nghe lại mình một câu"* |

### 4.3 Cấm sử dụng nếu không có ngữ cảnh thật

- "trải qua" — quá general, mất sắc thái
- "đối mặt" — quá kịch tính
- "cảm thấy" — passive, không cụ thể (dùng "thấy" thường thuận miệng hơn)
- "đấu tranh" — không thuộc voice chị Hiền
- "vượt qua" — slogan healing, sáo

---

# 5. Light Metaphor Bank

> Ẩn dụ **nhẹ, đời, không làm màu**. Mục tiêu: làm rõ cảm giác — không trang trí.

### 5.1 Ẩn dụ về cơ thể / không gian

- **vai nặng** — gánh, cảm xúc người khác mang theo
- **mắt khô** — chiều dài một ngày không nghỉ
- **vai cứng** — gồng kéo dài
- **tay lạnh** — căng thẳng không nói ra
- **một khoảng dừng** — pause tự nhiên giữa nhịp
- **một khoảng giữa** — lúc việc chưa xong, mình chưa kiểm tra
- **một cánh cửa khép** — sự khép lòng / không cho ai vào phần việc của mình

### 5.2 Ẩn dụ về vật / khoảnh khắc

- **một ly nước** — nhu cầu rất nhỏ, đủ thật
- **một câu hỏi bị bỏ quên** — điều ngầm nhưng cốt
- **một việc nhỏ nằm trên vai** — gánh không tên
- **một buổi sáng có trà** — không gian được chọn
- **một lần nhìn ra cửa sổ, không nghĩ gì** — khoảnh khắc quay vào
- **một tab nữa** — symbol của thói quen "chưa xong"

### 5.3 Ẩn dụ thiên nhiên (dùng tiết kiệm)

- **trời không sập** — sau khi buông
- **cơn / mùa** — thời lượng cảm xúc kéo dài
- **dòng / nhịp** — nhịp sống

### 5.4 Cấm

- **vibration / năng lượng / tần số** — spiritual quá
- **vũ trụ / linh hồn / bản thể** — không thuộc voice chị Hiền
- **chiến binh / chiến đấu** — voice quá mạnh
- **toả sáng / rực rỡ** — sáo, biểu diễn

---

# 6. Soft Transition Bank

> Cụm **chuyển ý mềm** — không "thứ nhất / thứ hai", không "tuy nhiên / mặt khác".

### 6.1 Mở chuyển từ biểu hiện → gốc rễ

- *Nhưng nếu nhìn kỹ hơn...*
- *Có khi vấn đề không nằm ở...*
- *Phần khó nhìn nhất là...*
- *Đây là phần khó nói thành lời.*
- *Sau này, nếu ngồi yên đủ lâu, bạn sẽ thấy...*
- *Câu đó nghe đơn giản. Nhưng nó không đơn giản.*

### 6.2 Mở chuyển từ phán xét → đứng cạnh

- *Không phải vì bạn sai. Chỉ là bạn đã quen...*
- *Không phải vì bạn yếu. Là vì...*
- *Không phải vì bạn không thương mình. Là vì bạn quen quá rồi.*
- *Có khi bạn không phải là người [X]. Bạn chỉ là người chưa [Y].*

### 6.3 Mở chuyển từ nhận diện → hành động nhỏ

- *Hôm nay, thử một lần.*
- *Tuần này, thử một lần.*
- *Không cần một câu trả lời lớn.*
- *Chỉ cần thấy [X] — chưa cần làm gì với nó.*
- *Quay lại nghe mình không cần [X lớn]. Nó có thể chỉ là [Y nhỏ].*

### 6.4 Cấm

- "Theo nghiên cứu..." — voice chị Hiền không lecture
- "Như chúng ta đã biết..." — generic, AI tone
- "Hôm nay mình muốn chia sẻ..." — delay (write_rules III.2)
- "Chúng ta hãy cùng..." — mất voice "đứng cạnh"

---

# 7. Inner Question Bank

> Câu hỏi **nội tâm** — audience tự hỏi mình, không bị chất vấn từ ngoài.

### 7.1 Câu hỏi về nhu cầu hiện tại

- *Mình đang cần gì lúc này?*
- *Mình đang cần gì trong 10 phút tới?*
- *Mình đang sợ điều gì lúc này?*
- *Mình đang gồng điều gì mà không nhận ra?*

### 7.2 Câu hỏi về động cơ

- *Mình đang làm vì muốn, hay vì sợ?*
- *Mình đang giữ vì cần, hay vì quen?*
- *Mình đang nhận vì thật sự nên nhận, hay vì sợ ai đó thất vọng?*
- *Mình đang chứng minh điều gì, và cho ai?*

### 7.3 Câu hỏi về tín hiệu

- *Mình đang bỏ qua tín hiệu nào của cơ thể?*
- *Cảm giác mệt này đến từ đâu — hôm nay, hay từ trước rất lâu?*
- *Câu nào trong đầu mình đang lặp đi lặp lại mà mình không nhận ra?*

### 7.4 Câu hỏi về tương lai gần

- *Phiên bản nhẹ hơn của mình — đang chờ mình làm điều gì?*
- *Một việc nhỏ hôm nay — sẽ trở thành gì sau 1 năm?*
- *Nếu không phải vì kỳ vọng của ai cả — mình thật sự muốn nhịp nào?*

### 7.5 Nguyên tắc dùng

- Chỉ **đặt 1 câu hỏi nội tâm** trên 1 đoạn / 1 ý. Đặt liên tiếp 3-4 câu hỏi → audience phòng thủ.
- Câu hỏi để **soi vào**, không để **chất vấn**. Không "Sao bạn lại...?" / "Tại sao bạn không...?".
- Câu hỏi nội tâm thường **đặt trong italic** (*"..."*) để tách khỏi narration.

---

# 8. Words to Avoid / Use Carefully

> **Không cấm tuyệt đối** — chỉ kiểm ngữ cảnh. Một từ có thể dùng nếu nó mô tả đúng một sự thật cụ thể; cùng từ đó dùng để làm câu nghe "cao cấp hơn" → loại.

### 8.1 Từ healing dễ thành đẹp giả

| Từ | Khi nào loại | Khi nào giữ được |
|---|---|---|
| **chữa lành** | dùng generic, không nói rõ chữa cái gì | nếu có 1 sự kiện / 1 cảm giác cụ thể đứng sau |
| **thức tỉnh** | dùng spiritual chung | gần như luôn nên đổi từ — voice chị Hiền không "thức tỉnh" |
| **hành trình** | sáo ngữ, dùng để làm dài câu | nếu thật sự là 1 chuỗi events theo thời gian |
| **phiên bản tốt hơn** | "self-help" template | ưu tiên *"phiên bản nhẹ hơn / vững hơn / thật hơn"* (cụ thể hơn) |
| **năng lượng nữ tính** | cliché, không thuộc voice | tránh hẳn trong 30 bài đầu |
| **yêu bản thân** | slogan, không có hành động đứng sau | đổi sang câu hành vi cụ thể (*"để dành cho mình một câu"*) |
| **kết nối sâu sắc** | sáo, AI tone | đổi sang *"đứng cạnh"* / *"nghe rõ"* |
| **chuyển hoá** | spiritual + thuật ngữ | đổi sang *"thay đổi cách nhìn"* / *"rõ thêm một chút"* |
| **khai mở** | spiritual quá | gần như luôn nên đổi — voice chị Hiền không "khai mở" |
| **nội lực** | cliché self-help | đổi sang *"sức bên trong"* / mô tả hành vi cụ thể |

### 8.2 Cụm khẳng định trống

- "rất quan trọng" — không nói được gì
- "vô cùng cần thiết" — sáo
- "hãy nhớ rằng..." — lecture
- "điều bạn cần biết là..." — guru tone
- "hãy luôn..." — command

### 8.3 Trạng từ thừa

- "thực sự / thật sự" — dùng nhiều thành filler
- "vô cùng / rất / cực kỳ" — passive intensifier, không tăng lực
- "một cách [X]" (vd "một cách tự nhiên") — danh từ hoá thừa, dùng adverb thuần ("tự nhiên")

### 8.4 Cụm AI / câu dịch

Xem `write_rules.md` mục VIII.3. Bổ sung tiếng Việt:

- "không thể phủ nhận rằng..."
- "trên thực tế..."
- "đáng nói là..."
- "điều thú vị là..."
- "có một sự thật là..." (trừ khi sau đó là sự thật **cứng** — không phải opening fluff)

---

# 9. Before-After Rewrite Examples

> Mỗi ví dụ: **Không nên** → **Vì sao chưa ổn** → **Tốt hơn** → **Vì sao tốt hơn**.

### Example 1 — Câu neo

**Không nên**:
> *"Hãy luôn nhớ rằng bạn xứng đáng được yêu thương và quan tâm bởi chính mình."*

**Vì sao chưa ổn**:
- "hãy luôn" — command + sáo
- "xứng đáng được [X]" — cấu trúc bị động, danh từ hoá
- "yêu thương và quan tâm" — 2 từ trừu tượng đứng cạnh nhau, làm câu mờ
- "bởi chính mình" — câu dịch (by yourself)

**Tốt hơn**:
> *"Nhỏ thôi. Nhưng là của bạn."*

**Vì sao tốt hơn**:
- 7 chữ, đứng riêng
- Có nhịp (2 câu ngắn, dấu chấm tách)
- Cụ thể (gắn với 1 nhu cầu nhỏ trước đó trong bài)
- Không command, không "hãy"

---

### Example 2 — Hook

**Không nên**:
> *"Phụ nữ chúng ta thường có xu hướng đặt nhu cầu của người khác lên trên nhu cầu của bản thân."*

**Vì sao chưa ổn**:
- "Phụ nữ chúng ta" — generic, đứng trên
- "có xu hướng" — câu viết, không phải câu nghĩ
- "đặt [X] lên trên [Y]" — cấu trúc câu dịch
- Không có "bạn", không gọi audience

**Tốt hơn**:
> *"Bạn hay hỏi người khác cần gì. Nhưng lâu rồi, bạn quên hỏi chính mình câu đó."*

**Vì sao tốt hơn**:
- Có "bạn" — gọi đúng 1 người
- 2 vế đối, ngắn-dài-ngắn
- "lâu rồi" — khẩu cảm Việt
- "quên hỏi chính mình câu đó" — đời, đúng cách phụ nữ Việt nghĩ

---

### Example 3 — Chuyển ý

**Không nên**:
> *"Tuy nhiên, mặt khác, chúng ta cần phải nhìn nhận rằng điều này còn đến từ một nguyên nhân sâu xa hơn."*

**Vì sao chưa ổn**:
- "Tuy nhiên / mặt khác" — đứng cạnh nhau, dư
- "cần phải nhìn nhận rằng" — cụm AI
- "nguyên nhân sâu xa hơn" — generic, mơ hồ

**Tốt hơn**:
> *"Nhưng nếu nhìn kỹ hơn, đây là phần khó nói thành lời."*

**Vì sao tốt hơn**:
- Gọn, 1 nhịp
- "nhìn kỹ hơn" thay "nhìn nhận"
- "khó nói thành lời" — khẩu cảm Việt cụ thể

---

### Example 4 — Body paragraph

**Không nên**:
> *"Sự kiệt sức về mặt cảm xúc mà bạn đang trải qua không phải là dấu hiệu của sự yếu đuối. Nó là kết quả tự nhiên của việc bạn đã gánh quá nhiều trong một thời gian dài."*

**Vì sao chưa ổn**:
- "sự kiệt sức về mặt cảm xúc" — danh từ hoá nặng, lửng củng
- "đang trải qua" — passive
- "kết quả tự nhiên" — cụm câu viết
- "trong một thời gian dài" — generic

**Tốt hơn**:
> *"Có những hôm bạn thấy mệt mà không gọi tên được. Không phải vì bạn yếu — là vì bạn đã giữ nó lâu hơn cơ thể có thể chịu."*

**Vì sao tốt hơn**:
- "Có những hôm" — gọi khoảnh khắc cụ thể
- "thấy mệt" thay "trải qua sự kiệt sức"
- Negative Frames (*"Không phải vì... — là vì..."*) — pattern voice chị Hiền
- "giữ nó lâu hơn cơ thể có thể chịu" — cụ thể, có hình ảnh

---

### Example 5 — CTA

**Không nên**:
> *"Hãy bình luận xuống dưới chia sẻ với mình câu chuyện của bạn để chúng ta cùng nhau lan toả thông điệp này nhé!"*

**Vì sao chưa ổn**:
- "Hãy" + "nhé" — command pha sến
- "chia sẻ câu chuyện" — sáo
- "lan toả thông điệp" — buzzword
- Dấu chấm than — phá voice tĩnh

**Tốt hơn**:
> *"Nếu chưa muốn nói ra, chỉ cần giữ câu hỏi này cho mình."*

**Vì sao tốt hơn**:
- Cho phép audience không comment công khai
- Câu mở cửa, không command
- Không dấu chấm than
- Đúng CTA cho 30 bài đầu (write_rules VI.1)

---

### Example 6 — Câu nội tâm

**Không nên**:
> *"Tôi cần phải tự hỏi bản thân rằng tôi thực sự muốn gì trong cuộc sống này."*

**Vì sao chưa ổn**:
- "tôi cần phải tự hỏi bản thân" — câu dịch, danh từ hoá
- "thực sự muốn gì trong cuộc sống này" — generic, sáo
- Dùng "tôi" — không phải xưng hô voice chị Hiền

**Tốt hơn**:
> *"Mình đang cần gì trong 10 phút tới?"*

**Vì sao tốt hơn**:
- Dùng "mình" (xưng nội tâm)
- Có giới hạn thời gian cụ thể (10 phút) — bớt áp lực phải trả lời lớn
- Câu hỏi nhỏ, đủ thật để tự trả lời

---

### Example 7 — Reframe

**Không nên**:
> *"Đã đến lúc bạn ngừng đặt người khác lên trên bản thân mình và bắt đầu yêu thương chính mình nhiều hơn."*

**Vì sao chưa ổn**:
- "Đã đến lúc bạn ngừng [X]" — command + áp lực
- "đặt người khác lên trên" — câu dịch
- "yêu thương chính mình nhiều hơn" — slogan, không có hành động cụ thể

**Tốt hơn**:
> *"Bạn không cần một buổi sáng tĩnh hay một kỳ nghỉ xa. Chỉ cần dừng lại nửa nhịp và hỏi mình một câu rất ngắn."*

**Vì sao tốt hơn**:
- Không command
- Cụ thể: "nửa nhịp" + "câu rất ngắn"
- Mở đường nhỏ, có thể làm ngay
- Match signature *"Thứ bạn cần không phải là thêm — mà là rõ hơn"*

---

# 10. Lifecycle file này

- **Stable**: chỉ update khi có ≥ 5 cụm mới đáng thêm vào 1 trong 9 sections.
- **Bump version** (v1 → v2) khi:
  - Thêm 1 section mới (vd Money & Safety expression bank cho D22+)
  - Hoặc rà soát toàn bộ sau 60 bài để loại các cụm không còn tự nhiên
- KHÔNG nhồi cụm chỉ vì 1 case lẻ — đợi cụm xuất hiện ≥ 3 lần qua nhiều bài đã pass review.

---

# 11. Khi nào KHÔNG dùng file này

- ❌ Trước khi có insight thật → quay lại pipeline, đừng tô son cho câu rỗng
- ❌ Trước khi đọc Voice profile → đọc trước, voice là nhạc trưởng
- ❌ Trong reply DM ngắn → không cần ngân hàng
- ❌ Khi chỉ cần 1 caption < 30 chữ → viết thẳng, không tra bank

→ Còn lại — bài public cho audience chị Hiền — pick các cụm phù hợp insight + voice, **không copy nguyên**.

---

# 12. Quan hệ với các file khác

```
profiles/chi-hien/write_rules.md (v2.2)
    ↓ mục II.5 — "thuận miệng tiếng Việt" định ra LUẬT
    ↓
docs/writing_methods/language_bank/chi_hien_expression_bank_v1.md (file này)
    ↓ cung cấp NGUYÊN LIỆU để câu chữ pass II.5
    ↓
draft bài (D1–D30, sau đó)
```

- **Write Rules** nói "phải kiểm câu có thuận miệng tiếng Việt không".
- **Expression Bank** đưa **gợi ý biểu đạt** + **ví dụ before-after** để rewrite câu lửng củng.
- **Hook Pattern Bank** (`chi_hien_hook_pattern_bank_v1.md`) tạo **cấu trúc hook**; Expression Bank tô màu **câu chữ** trong cấu trúc đó.
- **Content Formula v1** giữ **đường đi 7 bước**; Expression Bank là **bộ lọc cuối** ở bước 7 (Language Polish).

→ 4 file này đọc cùng nhau, không thay nhau.

---

**Updated**: 2026-05-10 · v1
**Tổng**: 9 sections + 50+ cụm gợi ý + 7 before-after examples
**Source**: write_rules v2.2 (II.5) + voice profile v2 + D1–D10 đã viết
**Tinh thần**: Insight thật là lõi. Voice là nhạc trưởng. Expression Bank chỉ giúp câu chữ thuận miệng và giàu sắc thái hơn — không thay được sự thật.
