# 🎼 Chị Hiền Content Formula v1

> **Vai trò**: Công thức viết RIÊNG cho thương hiệu Trịnh Nhi Hiền. Kết hợp 6 lớp đã có thành 1 quy trình 7 bước thống nhất.
>
> **Brand-specific exception**: file này nằm trong `docs/writing_methods/` để dễ tra cứu nhưng **không generic** — formula gắn với voice chị Hiền. Các method file khác trong thư mục vẫn giữ generic. Khi build brand mới → tạo `<brand>_content_formula_v1.md` riêng, KHÔNG dùng lại file này.
>
> **Khi dùng**: mỗi bài viết cho chị Hiền — Short FB / Long FB / Reel 60s / Reel 90–120s / Educational post.
>
> **Generated**: 2026-05-10 · v1
> **Source layers**: SB7 + Voice profile chị Hiền + Vietnamese Language Layer + Kallaway A/R framework + Editing Checklist + Insight pipeline.

---

## 1. Nguyên tắc lõi (5 không phá vỡ)

| # | Nguyên tắc | Ý nghĩa |
|---|---|---|
| 1 | **Insight thật trước, kỹ thuật sau** | Không có quote audience từ pipeline → không viết. Kỹ thuật chỉ là lớp dệt insight đã có. |
| 2 | **Voice là cuối cùng** | Khi Kallaway / SB7 / VN Language conflict với voice chị Hiền → voice thắng. |
| 3 | **Audience là Hero, chị Hiền là Guide** | Không bao giờ chị Hiền là nhân vật chính. Chị Hiền đứng cạnh, không đứng trên. |
| 4 | **Kallaway là kỹ thuật giữ chân, không phải giọng nói** | Kỹ thuật Kallaway điều chỉnh **3 giây đầu + nhịp giữa bài** — KHÔNG quyết định nội dung hay tone. |
| 5 | **Không bịa chi tiết cá nhân chị Hiền** | Chỉ dùng những gì có trong `profiles/chi-hien/about.md`. Quan sát chung được, life story bịa thì không. |

---

## 2. Vai trò 6 lớp trong công thức

| Lớp | Trả lời câu hỏi | File source |
|---|---|---|
| **1. Insight thật** | "Câu này có người thật nói không? Score bao nhiêu? Quote gốc ở đâu?" | `output/<niche>/<date>/classified.json` + `selected_angles.json` |
| **2. SB7 Message Check** | "Hero / Want / Problem / Guide / Plan / CTA / Success / Failure đầy đủ chưa?" | `docs/writing_methods/SB7_message_check.md` |
| **3. Voice Chị Hiền** | "Câu chữ có giống chị Hiền nói không? Có phá voice profile không?" | `profiles/chi-hien/{about, voice_profile, write_rules}.md` |
| **4. Kallaway A/R** | "3 giây đầu có giữ chân không? Nhịp giữa bài có rớt không?" | (file này — mục 4) |
| **5. VN Language Layer** | "Tiếng Việt có nhịp + sắc thái + hình ảnh không?" | `docs/writing_methods/language_bank/` |
| **6. Editing Checklist** | "Có bug nào trước khi đăng không? (sáo / generic / lẫn tone / banned word)" | `docs/writing_methods/editing_checklist.md` |

→ **Thứ tự áp dụng**: 1 → 2 → 3 → 4 → 5 → 6. KHÔNG đảo. Skip lớp 1 = bài generic. Skip lớp 6 = bài có bug đăng public.

---

## 3. Công thức tổng quát 7 bước

```
[1] Real Insight       (quote thật từ pipeline)
        ↓
[2] Hook               (Kallaway: No Delay + Clarity — 3 giây đầu)
        ↓
[3] Emotional Mirror   (Kallaway: Thought Broadcasting — gọi đúng cảm xúc audience đang có)
        ↓
[4] Gentle Reframe     (Voice chị Hiền: tuyên ngôn philosophical, không guru)
        ↓
[5] Small Plan         (SB7 ô 7: hành động nhỏ ≤ 5 phút)
        ↓
[6] Soft CTA           (Voice + SB7 ô 8: invitation, không command)
        ↓
[7] Language Polish    (VN Language Layer + Editing Checklist)
```

### 3.1 Real Insight (Bước 1)

- **Input**: 1 quote audience từ `selected_angles.json`. Score ≥ 10. Có bucket pain/desire/question.
- **Output**: 1 câu insight rõ — đã verify "có người thật nói câu này".
- **Cấm**: viết bài không có insight gốc. Đoán "audience chắc đang nghĩ X" mà không có quote.

### 3.2 Hook (Bước 2 — Kallaway)

- **Mục tiêu**: 3 giây đầu (Reel) hoặc 1 câu đầu (FB post) khiến audience **dừng lướt**.
- **Kỹ thuật**:
  - **No Delay**: KHÔNG mở bằng "Xin chào" / "Hôm nay mình muốn chia sẻ" / "Có một câu chuyện..."
  - **Clarity**: ngay câu đầu audience hiểu bài về gì + có liên quan đến mình không
- **Pattern voice chị Hiền**: 4 lựa chọn từ `write_rules.md` — Hard Truth / In Medias Res / Paradox / Inner Question.
- **Ví dụ đúng**: *"Bạn không tự nhiên tiêu cực đâu. Bạn đang ngồi cạnh người khiến bạn tiêu cực."* (D1)
- **Ví dụ sai**: *"Hôm nay mình muốn chia sẻ về câu chuyện của một người chị..."* (delay + AI tone)

### 3.3 Emotional Mirror (Bước 3 — Kallaway Thought Broadcasting)

- **Mục tiêu**: gọi đúng cảm xúc audience đang có nhưng chưa dám nói thành lời.
- **Kỹ thuật**: nói câu mà audience đang nghĩ trong đầu — họ thấy "ơ, đúng cảm giác mình".
- **Pattern voice chị Hiền**: chi tiết cụ thể (cuộc gọi / bữa cơm / nhóm chat) thay vì "rất nhiều người đang...".
- **Ví dụ đúng**: *"Một cuộc gọi gần đây — bạn không nhớ rõ nói gì, chỉ nhớ gác máy xong vai nặng."* (D1)
- **Ví dụ sai**: *"Theo nghiên cứu, 70% phụ nữ đang stress."* (data lạnh, không mirror cảm xúc)

### 3.4 Gentle Reframe (Bước 4 — Voice chị Hiền)

- **Mục tiêu**: chuyển góc nhìn audience — từ "mình là vấn đề" sang "có cách hiểu khác".
- **Kỹ thuật**: 1 tuyên ngôn philosophical (SB7 ô 5) — ngắn, sâu, không guru.
- **Pattern voice chị Hiền**: dùng "—" tạo nhịp ngừng. Câu ngắn sau câu dài. Không "bạn phải / bạn cần".
- **Ví dụ đúng**: *"Cảm xúc của người khác — không phải cảm xúc của bạn."* (D1) · *"Thời gian là thứ duy nhất mình không in lại được."* (D4)
- **Ví dụ sai**: *"Hãy yêu bản thân nhiều hơn!"* (sáo + lệnh + dấu chấm than)

### 3.5 Small Plan (Bước 5 — SB7 ô 7)

- **Mục tiêu**: 1 hành động nhỏ audience làm được trong ≤ 5 phút / ≤ 1 ngày.
- **Cấm**: plan đòi hỏi đầu tư lớn (mua khoá học / đăng ký / đầu tư thời gian dài).
- **Pattern voice chị Hiền**: hành động đời thường, có chi tiết cụ thể (5 phút / 1 phút / pha thứ nóng / ngồi yên).
- **Ví dụ đúng**: *"Tối nay, thử ngồi yên 1 phút trước khi mở laptop — chỉ 1 phút thôi."* (D2) · *"Hôm nay, cho phép mình buồn 5 phút — không kèm 'lẽ ra mình phải...'"* (D6)
- **Ví dụ sai**: *"Đăng ký khoá học 7 ngày để thay đổi cuộc đời."* (offer + thời gian dài + hứa kết quả)

### 3.6 Soft CTA (Bước 6 — SB7 ô 8 + Voice chị Hiền)

- **Mục tiêu**: kéo comment thật để feed pipeline vòng sau, không bán.
- **Kỹ thuật**: invitation cụ thể (comment 1 từ / 1 việc / 1 cái tên).
- **Cấm**: "đăng ký NGAY", "chỉ còn X suất", "Like nếu đồng ý", inbox NGAY, link bán hàng.
- **Ví dụ đúng**: *"Comment 1 cái tên — chỉ trong đầu cũng được nhé."* (D4) · *"Chỉ cần để lại một chữ — mình sẽ đọc."* (D6)
- **Ví dụ sai**: *"Đăng ký workshop free → comment EMAIL!"* (FOMO + lệnh + free trap)

### 3.7 Language Polish (Bước 7 — VN Language Layer + Editing Checklist)

- **Mục tiêu**: câu chữ có nhịp + sắc thái + hình ảnh, không sáo.
- **Kỹ thuật**:
  - 1-2 biện pháp tu từ (tương phản / điệp / câu hỏi tu từ / nói giảm / đảo ngữ)
  - Tình thái từ + trợ từ + phó từ ở câu kết / CTA cho mềm
  - Đại từ "mình / bạn" đồng nhất
  - Chạy `editing_checklist.md` Nhóm 7 (VN check) trước khi đăng
- **Cấm**: nhồi 4-5 biện pháp/bài. Câu nào không phục vụ ý → bỏ.

---

## 4. Kallaway Attention Layer (đã adapt cho chị Hiền)

> **Vai trò**: lớp **attention/retention** cho 3 giây đầu + nhịp giữa bài. KHÔNG phải giọng viết. KHÔNG quyết định nội dung.
>
> **Nguyên tắc bắt buộc**: voice chị Hiền là nhạc trưởng. Kallaway conflict với voice → voice thắng. KHÔNG FOMO. KHÔNG guru. KHÔNG hook giật sốc. KHÔNG biến bài thành viral-script công thức.
>
> **Tóm tắt từ Kallaway note** — đã rút gọn cho 30 bài đầu của chị Hiền. Các phần Kallaway không cần thiết cho giai đoạn awareness được đưa xuống "chưa dùng" hoặc bỏ.

---

### 4.1 Hook Formula — 4 yếu tố cho 3 giây đầu

Mọi hook phải pass 4/4 yếu tố:

| Yếu tố | Định nghĩa | Test |
|---|---|---|
| **No Delay** | Câu đầu = câu cốt lõi. Không khoảng đệm. | Cắt 5 giây đầu — bài còn hiểu được không? Nếu CÓ → là delay. |
| **Clarity** | 3 giây đầu audience hiểu bài về gì + có liên quan đến mình không. | Người ngoài niche có hiểu bài đang nói gì không? |
| **Relevance** | Bài nói thẳng đến **1 nhóm cụ thể**. | Persona ngoài nhóm có thấy bài thuộc về mình không? Nếu KHÔNG → relevance đúng. |
| **Intrigue** | Curiosity gap nhẹ — KHÔNG clickbait sốc. | Đọc hook — có muốn xem tiếp không? |

→ Pass 4/4 mới qua hook check. Fail 1 → viết lại.

#### 4.1.bis — Checklist 4 lỗi hook (rút gọn)

- **Delay**: mở vòng vo, giới thiệu bản thân quá sớm.
- **Confusion**: câu dài, khó hiểu, nhiều thuật ngữ.
- **Irrelevance**: người đọc không thấy mình trong câu mở.
- **No Intrigue**: đọc xong không có lý do đọc tiếp.

→ Voice chị Hiền hay dính lỗi **Delay** nhất (tone tĩnh dễ "warm up" trước khi vào ý). Audit hook luôn check Delay đầu tiên.

---

### 4.2 Hook Formats — 4 ưu tiên cho 30 bài đầu

Trong giai đoạn audience Lạnh, chỉ dùng 4 hook format (Kallaway principle — đã adapt cho Chị Hiền):

| # | Format | Pattern voice match | Ví dụ từ D1–D7 |
|---|---|---|---|
| 1 | **Contrarian nhẹ** | Pattern A (Hard Truth), Pattern C (Paradox) | D3: *"Muốn buông không có nghĩa bạn đã chọn sai"* |
| 2 | **Story Hook** | Pattern B (In Medias Res) | D7: *"Bận thì không phải nghĩ"* — mở từ giữa câu nói |
| 3 | **"Bạn đang…"** | Pattern A (Hard Truth) gọi trạng thái | D1: *"Bạn đang ngồi cạnh người khiến bạn tiêu cực"* |
| 4 | **Question / Self-reflection** | Pattern D (Inner Question) | D7: *"mình đang bận để trốn điều gì?"* |

→ **5 hook còn lại — dùng sau**: Proof / Case Study, Fortune Teller, Tutorial, Secret Reveal, Investigator — chỉ dùng khi có insight thật hoặc dữ liệu thật, không dùng để làm bài giật chú ý.

→ **1 hook = 1 format chính.** KHÔNG trộn 3-4 format.

---

### 4.3 Story Locks — 2 essentials cho chị Hiền

Trong 6 Story Locks Kallaway, chỉ 2 cái là essential cho voice chị Hiền:

| Story Lock | Vai trò | Ví dụ |
|---|---|---|
| **Thought Broadcasting** | Nói câu mà audience đang nghĩ nhưng chưa dám nói ra | D2: *"Bạn không thật sự yêu công việc đâu"* |
| **Contrast** (tương phản) | Đặt 2 thứ đối nhau cạnh nhau — cơ chế underlying của mọi attention lock | D6: *"Không phải vì mình yếu — mà vì một phần bên trong đã quá mệt"* |

→ **Contrast** đã có trong VN Language Layer (biện pháp tu từ tương phản) — đây là cùng 1 kỹ thuật, gọi 2 tên khác nhau.

→ **4 Story Lock khác** (Branded Naming / Assumption Language / Negative Frames / Loop Openers) không phải essentials cho 30 bài đầu. Đặc biệt **Branded Naming bắt buộc tránh** vì vi phạm Q5 voice profile ("không dùng framework có tên").

---

### 4.4 Alignment — 3 lớp cùng nói 1 ý

**Cho Reel** (Spoken / Text / Visual):

| Lớp | Yêu cầu |
|---|---|
| **Spoken Hook** | Câu nói đầu (audio) — voice tĩnh |
| **Text Hook** | Text overlay đầu — đồng ý với Spoken, không lặp y nguyên |
| **Visual Hook** | B-roll đầu — hỗ trợ ý, không trang trí |

→ Test: tắt audio — text + visual có hiểu bài về gì không? Tắt video — audio có đủ không?

**Cho FB Post** (Hook / Body / CTA):

| Lớp | Yêu cầu |
|---|---|
| **Hook** | 1-2 câu đầu — Pattern A/B/C/D |
| **Body** | Toàn bài — deliver đúng điều hook hứa |
| **CTA** | Cuối bài — mời thêm 1 hành động liên quan đến hook + body |

→ Test: hook hứa X → body deliver X → CTA mời thêm X? Nếu hook nói A mà body nói B → audience confused.

---

### 4.5 CTA theo nhiệt độ thị trường

| Nhiệt độ | Audience | CTA cho phép | Cho 30 bài đầu? |
|---|---|---|---|
| **🥶 Lạnh** | Lần đầu thấy chị Hiền · AWARE stage | Comment 1 từ · Comment số/A-B-C · Tự quan sát trong lòng | ✅ **Tuần 1 (D1–D7) tất cả ở đây** |
| **♨️ Ấm** | Đã follow ≥ 1 tháng · CONSIDER stage | Câu hỏi sâu hơn · Mời chia sẻ trải nghiệm | (D8–D21 — tune sau khi tuần 1 ra data) |
| **🔥 Nóng** | Đã engage nhiều · DECIDE stage | Offer cụ thể | ❌ **KHÔNG dùng trong 30 bài đầu** |

→ **Audit**: mỗi CTA tự hỏi "audience đang ở nhiệt độ nào?" — nếu không chắc → mặc định **Lạnh**.

→ **Quy tắc vàng thị trường lạnh**: tuần 1 (D1–D7) KHÔNG mention sản phẩm / giá / offer ở BẤT KỲ vị trí nào trong bài.

#### 4.5.bis — CTA Toolkit cho 30 bài đầu (chỉ 3 loại)

Trong giai đoạn awareness, chỉ dùng 3 dạng CTA (Kallaway principle — đã adapt cho Chị Hiền):

1. **Comment 1 từ** — invitation mềm, không hứa quà.
2. **Comment số / A-B-C** — qualify nhẹ, không hứa "mình gửi tiếp".
3. **Tự quan sát, không cần trả lời** — cho phép audience không comment công khai.

**Ví dụ CTA đúng giọng chị Hiền:**

- "Comment 1 từ — mình muốn biết bạn đang thấy gì."
- "Bạn đang ở 1, 2 hay 3?"
- "Nếu chưa muốn nói ra, chỉ cần tự trả lời trong lòng cũng được."
- "Tuần sau mình sẽ viết tiếp phần này."

**📦 CTA chưa dùng trong 30 bài đầu:**

- Comment từ khoá để nhận resource (lead magnet trap)
- Inbox cá nhân hoá để tư vấn (chưa đủ trust)
- Scarcity + deadline (chưa có offer)
- Follow để không bỏ lỡ (voice chị Hiền không "kêu gọi follow")

→ Sau D30, khi có data audience thật, mới reconsider 4 CTA này — nhưng vẫn phải adapt theo voice (bỏ FOMO, bỏ "ngay", bỏ hứa hẹn quá đà).

---

### 4.6 Ghi chú cuối mục

> **Kallaway trong file này chỉ dùng để kiểm tra attention/retention. Không dùng để thay voice Chị Hiền. Nếu kỹ thuật làm bài mất độ lắng, bỏ kỹ thuật.**

---

## 5. Cách TRÁNH dùng Kallaway sai (5 anti-pattern)

| # | Anti-pattern | Vì sao sai cho chị Hiền |
|---|---|---|
| 1 | **Giật sốc quá** ("ĐỪNG ĐỌC NẾU BẠN YẾU TIM!") | Phá voice tĩnh-trầm. Audience trung niên ghét clickbait. |
| 2 | **FOMO** ("Chỉ còn 24h!" / "Bỏ qua sẽ hối hận!") | Vi phạm Q15-Q17 voice profile. Tạo áp lực = mất trust. |
| 3 | **Guru tone** ("Mình sẽ chỉ cho bạn cách...") | Phá Q9 voice profile (chị Hiền là Guide, không Hero). |
| 4 | **Viral-script công thức** (5 hook formula copy từ KOL khác) | Bài thành template — mất giọng riêng. Audience nhận ra ngay. |
| 5 | **Hy sinh giọng để lấy retention** (cắt câu chậm để theo nhịp video) | Voice chị Hiền chính là retention — audience ở lại vì giọng, không phải vì giật. |

→ **Quy tắc số 1**: Khi Kallaway conflict với voice chị Hiền → **voice thắng**. Mất 0.5 giây retention không bằng mất tone đặc trưng.

---

## 6. Template áp dụng cho 5 format

### 6.1 Short FB Post (200–350 chữ)

```
[Hook: 1-2 câu — Pattern A/B/C/D]              ← Bước 2 (No Delay + Clarity)
        ↓
[Emotional Mirror: 2-3 câu chi tiết cụ thể]    ← Bước 3 (Thought Broadcasting)
        ↓
[Reframe: 1-2 câu tuyên ngôn philosophical]    ← Bước 4 (Gentle Reframe)
        ↓
[Small Plan: 1 câu hành động ≤ 5 phút]         ← Bước 5
        ↓
[Câu neo: 1 câu để lại trong đầu audience]     ← Bước 7 (Language Polish)
        ↓
[Soft CTA: 1 câu invitation]                   ← Bước 6
```

→ Tổng: ~250 chữ. Không heading. Câu ngắn xen câu dài. 1-2 dấu gạch ngang.

### 6.2 Long FB Post (500–700 chữ)

```
[Hook: 1-2 câu — Pattern A/B/C/D]              ← Bước 2
        ↓
[Story / Observation: 2 đoạn — 2 nhịp tương phản hoặc 2 khoảnh khắc] ← Bước 3
        ↓
[Conflict / Root Cause: 1 đoạn — sắc thái công bằng] ← Bước 3 đào sâu
        ↓
[Reframe / Realization: 1 đoạn — tuyên ngôn philosophical + câu hỏi tu từ]  ← Bước 4
        ↓
[Application: 1 đoạn — Small Plan ≤ 5 phút có chi tiết] ← Bước 5
        ↓
[Anchor: 1-2 câu neo cuối]                     ← Bước 7
        ↓
[Soft CTA: 1 câu invitation]                   ← Bước 6
```

→ Tổng: ~600 chữ. Có thể có 1-2 sub-heading (vd "Hành động nhỏ"). Đoạn xen đoạn dài-ngắn.

### 6.3 Reel 60s

```
0:00–0:08    [Hook — Pattern A/B/C/D]                    ← Bước 2
0:08–0:25    [Emotional Mirror — 3 quan sát cụ thể]      ← Bước 3
0:25–0:42    [Insight + Reframe — 1 tuyên ngôn]          ← Bước 4
0:42–0:58    [Câu neo + Plan ngầm + Soft CTA]            ← Bước 5+6+7
```

→ 4 đoạn, không có chỗ cho pause. Plan thường ngầm trong CTA.

### 6.4 Reel 90–120s

```
0:00–0:10    [Hook — Pattern A/B/C/D]                       ← Bước 2
0:10–0:35    [Emotional Mirror — 3-4 quan sát + 1 cảnh thứ 2] ← Bước 3
0:35–0:55    [Insight đào sâu — 2-3 lớp]                    ← Bước 3 đào sâu
0:55–1:15    [Reframe + Plan rõ — tuyên ngôn + hành động]   ← Bước 4+5
1:15–1:30    [Câu neo + Soft CTA]                           ← Bước 6+7

(với 100-120s: thêm 1-3 nhịp pause cho cảm xúc ngấm — dùng B-roll im lặng)
```

→ 5 đoạn. Có chỗ thở. Plan có thể tách rõ thành câu riêng. Bài chạm sâu nên dùng 100-120s.

### 6.5 Educational post (300–500 chữ)

```
[Hook — Counter-Belief hoặc Paradox]            ← Bước 2 (Intrigue mạnh)
        ↓
[Câu dẫn — 1 câu đặt context]                   ← Bước 3 (relevance)
        ↓
[3 ý chính — điệp cấu trúc 3 lần]               ← Bước 4 (Reframe × 3)
        ↓
[Ví dụ ngắn — generic, không bịa cá nhân]       ← Bước 3 đào sâu
        ↓
[Hành động nhỏ — 1 plan rõ]                     ← Bước 5
        ↓
[Soft CTA — comment số / 1 từ]                  ← Bước 6
```

→ Tổng: ~400 chữ. Dùng bold cho 3 ý chính (chỉ bold heading, không bold mọi từ khoá). Không quá 3 dấu gạch ngang/đoạn.

---

## 7. Checklist TRƯỚC khi viết

Fill 7 ô này trước khi bắt đầu draft:

- [ ] **Insight gốc**: quote audience từ `selected_angles.json` đâu? Score? Bucket?
- [ ] **SB7 10 ô**: đã fill rõ chưa? Pass tất cả ô?
- [ ] **Voice profile**: đã đọc lại Q11 (pattern mở bài) + Q12 (structure) + Q13 (CTA) chưa?
- [ ] **Format**: bài này là Short FB / Long FB / Reel 60s / Reel 90-120s / Educational?
- [ ] **Pattern mở bài**: chọn Pattern A / B / C / D nào (theo write_rules)?
- [ ] **VN biện pháp tu từ**: chọn 1-2 cái nào (tương phản / điệp / câu hỏi tu từ / nói giảm / đảo ngữ)?
- [ ] **Banned word check**: scan list trong `write_rules.md` — đảm bảo không lọt.

→ Thiếu 1 ô → quay lại fill, KHÔNG viết.

---

## 8. Checklist SAU khi viết (trước khi đăng)

Chạy 12 câu này trên draft:

**🎯 Insight & Voice (4 câu)**
- [ ] **Insight thật**: quote gốc có xuất hiện trong bài (ít nhất ngầm)?
- [ ] **Voice giống chị Hiền**: đọc to → có nghe như chị Hiền nói không, hay như AI / KOL khác?
- [ ] **Hero là audience**: chị Hiền có chiếm spotlight không? Chị Hiền là Guide, không phải Hero.
- [ ] **Plan rõ**: có 1 hành động ≤ 5 phút audience làm được không?

**🪝 Attention & Retention (4 câu — Kallaway check)**
- [ ] **Hook 4 yếu tố**: pass No Delay + Clarity + Relevance + Intrigue (mục 4.1)? Cắt 5 giây đầu — bài còn hiểu được không? Nếu CÓ → 5 giây đầu là delay.
- [ ] **Hook Format**: bài có dùng đúng 1 trong 4 format ưu tiên cho 30 bài đầu (Contrarian nhẹ / Story Hook / "Bạn đang…" / Question — mục 4.2)? KHÔNG trộn nhiều format. KHÔNG dùng các format "dùng sau" trừ khi có insight thật.
- [ ] **Alignment**: Reel — Spoken / Text / Visual có cùng nói 1 ý? FB — Hook hứa X → Body deliver X → CTA mời thêm X? (mục 4.4)
- [ ] **CTA đúng nhiệt độ**: audience đang Lạnh / Ấm / Nóng (mục 4.5)? Tuần 1 (D1–D7) bắt buộc Lạnh.

**🇻🇳 Language & Editing (4 câu)**
- [ ] **CTA mềm + đúng giai đoạn**: chỉ dùng 3 dạng cho 30 bài đầu (Comment 1 từ / Comment số / Tự quan sát — mục 4.5.bis)? KHÔNG comment từ khoá để nhận resource / KHÔNG inbox cá nhân hoá / KHÔNG scarcity / KHÔNG follow ngay?
- [ ] **VN Language**: có 1-2 biện pháp tu từ (không nhồi)? Tình thái từ ở câu kết?
- [ ] **Story Lock essentials**: có dùng Thought Broadcasting hoặc Contrast (mục 4.3)? KHÔNG dùng Branded Naming.
- [ ] **Editing checklist**: chạy `editing_checklist.md` — đặc biệt Nhóm 6 (bịa story) + Nhóm 7 (VN check).

→ Pass 12/12 → đăng. Fail 1+ → fix trước.

→ **Quy tắc khi conflict**: nếu Kallaway check fail nhưng voice chị Hiền tốt → giữ voice, sửa Kallaway. KHÔNG ngược lại.

---

## 9. Quan hệ với các file khác

```
┌─────────────────────────────────────────────────────┐
│  CHỊ HIỀN CONTENT FORMULA v1 (file này)             │
│  ↓ kết hợp 6 lớp:                                   │
│                                                      │
│  [1] Insight pipeline                               │
│      → output/<niche>/<date>/classified.json        │
│      → output/<niche>/_master/selected_angles.json  │
│                                                      │
│  [2] SB7 Message Check                              │
│      → docs/writing_methods/SB7_message_check.md    │
│                                                      │
│  [3] Voice chị Hiền                                 │
│      → profiles/chi-hien/about.md                   │
│      → profiles/chi-hien/voice_profile.md           │
│      → profiles/chi-hien/write_rules.md             │
│                                                      │
│  [4] Kallaway Attention Layer                       │
│      → file này, mục 4                              │
│        (essential checks đã adapt cho Chị Hiền)     │
│                                                      │
│  [5] Vietnamese Language Layer                      │
│      → docs/writing_methods/language_bank/          │
│                                                      │
│  [6] Editing Checklist                              │
│      → docs/writing_methods/editing_checklist.md    │
└─────────────────────────────────────────────────────┘
```

→ File này KHÔNG thay thế bất kỳ file nào ở trên — là **lớp orchestration** trên cùng.

---

## 10. Lifecycle

- File này **stable** — chỉ update khi có insight mới về cách kết hợp 6 lớp.
- KHÔNG nhồi method techniques mới vào đây — chúng thuộc các file generic (`hook_methods.md` etc.)
- KHÔNG nhồi voice của brand khác vào đây — file này riêng cho chị Hiền.
- Khi nâng version (vd thêm Insight pipeline v2 hoặc Kallaway v2 chi tiết) → bump v1 → v2.

---

## 11. Khi nào KHÔNG dùng formula này

- Caption Instagram <30 chữ → quá ngắn cho 7 bước
- Reply DM → trò chuyện trực tiếp
- Story ngắn / nháp test → format chưa cần audit
- Email cá nhân / tin nhắn nội bộ → không phải content public

→ Còn lại — **bài public cho audience chị Hiền** — dùng đầy đủ 7 bước.

---

## 12. Nguồn tham khảo

- **SB7 / BrandScript**: Donald Miller — *Building a StoryBrand*. Đã rút gọn cho awareness/nurture context (xem `SB7_message_check.md`).
- **Kallaway A/R framework**: agency Kallaway / Brendan Kallaway — kỹ thuật retention cho short-form video. **Tóm tắt từ Kallaway note**, đã rút gọn và adapt cho voice chị Hiền + giai đoạn 30 bài đầu. Phần Kallaway trong file này giữ lại 4 nhóm essentials:
  1. **Hook Formula 4 yếu tố** (No Delay / Clarity / Relevance / Intrigue) — mục 4.1
  2. **Hook Formats — 4 ưu tiên** (Contrarian nhẹ / Story Hook / "Bạn đang…" / Question) — mục 4.2 · 5 hook khác đưa xuống "dùng sau"
  3. **Story Locks — 2 essentials** (Thought Broadcasting + Contrast) — mục 4.3 · 4 lock khác bỏ hoặc tránh
  4. **Alignment + CTA theo nhiệt độ** — mục 4.4 + 4.5

  → **Adapt cho chị Hiền**: chị Hiền KHÔNG dùng Secret Reveal / Branded Naming / CTA Nóng / lead magnet trap / FOMO / scarcity giả trong 30 bài đầu. Tone tĩnh-trầm — không drama, không clickbait.

  → **Không thêm vào formula chính**: Authority Likeable (về cách quay), Viral Script Framework (đẩy về tone giật), 7 Story Structures, TAM Resonance.

  → **Insight Strength Check** (thay tên cho Viral Script Framework): chỉ dùng để kiểm tra insight có đủ lực không, không dùng để chạy theo viral.

  → **Kallaway là lớp attention/retention, không phải giọng viết.** Mọi nguyên tắc adapt theo `profiles/chi-hien/`.

- **Vietnamese Language Layer**: nguồn nội bộ + wiki tiếng Việt (xem `language_bank/README.md`).
- **Voice chị Hiền**: tự xây từ about.md + voice_profile.md + write_rules.md (chị Hiền viết).

→ **Formula này là tổng hợp** — không phải copy nguyên 1 framework nào. Mọi lớp đều adapt cho voice + niche cụ thể.

---

**Updated**: 2026-05-10 · v1
**Tinh thần**: Formula là **dàn nhạc**. Voice chị Hiền là **nhạc trưởng**. Các lớp khác là **nhạc cụ**. Khi nhạc trưởng và 1 nhạc cụ conflict → nhạc trưởng quyết.
