# Writing Method Library

> **Vai trò**: Kho **kỹ thuật viết** đã được lọc và chuẩn hoá thành nguyên tắc.
>
> **Đối tượng dùng**: Anh / nhân viên content / Claude (qua production.py) khi tạo Reel, Facebook post, caption, CTA, production brief.

---

## 1. Library này KHÔNG thay thế

Trước khi mở bất kỳ file nào trong folder này — phải hiểu rõ:

| Library KHÔNG thay thế | Vẫn cần đọc trước |
|---|---|
| ❌ Insight thật từ comment audience | `output/<niche>/<date>/classified.json` + `1-liệt-kê.csv` |
| ❌ Voice profile của brand | `profiles/<brand>/voice_profile.md` |
| ❌ Brand-specific writing rules | `profiles/<brand>/write_rules.md` |
| ❌ Judgment chiến lược của con người | Anh / brand owner quyết angle nào quay |

**Quy tắc số 1**: Method là **lớp biên tập** — chỉ áp dụng SAU KHI đã có:
1. Insight thật (từ pipeline `bank` → `select`)
2. Voice profile phù hợp (brand đã định)
3. Big idea đã được duyệt (anh / chị Hiền chọn)

→ Method KHÔNG sinh insight. Method chỉ giúp **dệt lại** insight đã có thành text chất lượng cao hơn.

---

## 2. Library này LÀM gì

Nâng chất lượng **5 lớp** của output content:

| Lớp | File phụ trách | Cụ thể |
|---|---|---|
| **Hook** (3s đầu) | [hook_methods.md](hook_methods.md) | 8 nhóm hook generic — pick 1 phù hợp angle + brand |
| **Cấu trúc / Storytelling** | [storytelling_methods.md](storytelling_methods.md) | 7 thành phần story — bộ khung cho bài kể chuyện |
| **Format video ngắn** | [short_video_methods.md](short_video_methods.md) | 5 đoạn 60s + text overlay + retention |
| **Thuyết phục / CTA** | [persuasion_methods.md](persuasion_methods.md) | Belief shift, objection handling, soft CTA |
| **Editing / QA** | [editing_checklist.md](editing_checklist.md) | Checklist trước khi xuất bản |

Plus 2 file điều phối:
- [method_picker.md](method_picker.md) — Quy tắc match content type → method nào dùng
- [rejected_methods.md](rejected_methods.md) — Anti-patterns BỎ QUA (tactic xấu, đã loại trừ)

Plus **🧭 Message Check layer** — audit structure thông điệp (xem mục 2.4 dưới).

Plus **🇻🇳 Vietnamese Language Layer** — kho câu chữ tiếng Việt (xem mục 2.5 dưới).

Plus **🌿 Chị Hiền Content Formula v1 + Brand Layer v2** — formula chính + 3 file profile, đã test pass bước đầu (xem mục 2.6 dưới).

---

## 2.4 🧭 Message Check layer

> **Audit structure thông điệp trước khi viết** — kiểm tra Hero / Want / Problem / Guide / Plan / CTA / Success / Failure đã đầy đủ chưa.
>
> **KHÔNG phải style viết.** KHÔNG phải template. KHÔNG thay thế voice. Là **kim chỉ nam ngầm** sau câu chữ.

| File | Vai trò |
|---|---|
| [SB7_message_check.md](SB7_message_check.md) | 10 ô audit dựa trên BrandScript / StoryBrand 7 — đã rút gọn cho awareness/nurture content |

**Quy tắc**:
- Mỗi bài chọn **1 message framework chính + 1-2 phụ** (tương lai khi có nhiều framework). KHÔNG trộn 4-5 framework vào 1 bài.
- SB7 hiện là framework **mặc định** cho chị Hiền — fill 10 ô trước khi viết draft.
- 10 ô là **chuẩn bị thông điệp**, KHÔNG có nghĩa cả 10 ô phải xuất hiện rõ trong bài.

**Khi nào skip SB7**: caption ngắn <30 chữ / reply DM / nháp test format. Còn lại — bắt buộc.

---

## 2.5 🇻🇳 Vietnamese Language Layer

> Lớp **câu chữ tiếng Việt** — bổ sung cho hook/storytelling/persuasion. Giúp output có **nhịp, sắc thái, hình ảnh** hơn.

| File | Mục đích |
|---|---|
| [language_bank/README.md](language_bank/README.md) | Index + cách dùng Language Bank |
| [language_bank/vietnamese_rhetoric.md](language_bank/vietnamese_rhetoric.md) | 11 biện pháp tu từ (so sánh, ẩn dụ, tương phản, đảo ngữ, chơi chữ…) |
| [language_bank/vietnamese_word_classes.md](language_bank/vietnamese_word_classes.md) | 10 từ loại — trọng tâm tình thái từ + trợ từ + phó từ (mềm câu) |
| [language_bank/expressive_word_groups.md](language_bank/expressive_word_groups.md) | 8 nhóm từ biểu đạt (láy, lóng, đồng nghĩa, trái nghĩa, địa phương, thành ngữ…) |
| [language_bank/tone_and_register.md](language_bank/tone_and_register.md) | 5 tone + check lẫn tone + Hán-Việt vs thuần Việt + giác quan |
| [language_bank/language_bank_template.md](language_bank/language_bank_template.md) | Bảng audit 7 cột — phân tích bài viral của creator giỏi |
| [language_bank/language_bank_audit_prompt.md](language_bank/language_bank_audit_prompt.md) | Prompt mẫu cho Claude tự audit theo template |

**Khi nào dùng**: Sau khi pick hook/storytelling/persuasion method → mở Language Bank chọn 1-2 biện pháp tu từ + tone phù hợp insight → viết draft → chạy `editing_checklist.md`.

**Khi nào KHÔNG dùng**: Chưa có insight thật / chưa đọc voice profile brand → Language Bank chỉ là lớp câu chữ, không sinh ý.

---

## 2.6 🌿 Chị Hiền Content Formula v1 + Brand Layer v2 (production-ready)

> **Trạng thái**: Đã test pass bước đầu trên D1–D7 tuần 1. Brand Layer v2 đã được chị Hiền tự chỉnh tay thêm **Long-term direction** + **rule mới về từ dài hạn**.
>
> Workflow chính cho mọi bài tiếp theo của brand chị Hiền.

### Files (Brand Layer v2 — chuẩn mới nhất)

| Layer | File | Vai trò |
|---|---|---|
| **Core Formula** | [chi_hien_content_formula_v1.md](chi_hien_content_formula_v1.md) | Formula chính cho brand chị Hiền — orchestration 6 lớp |
| **Brand Layer v2** — 1 | [`profiles/chi-hien/about.md`](../../profiles/chi-hien/about.md) | Who I am / What I do / **Long-term brand direction** / What makes me tick / Audience / Brand voice / Active projects / Core message |
| **Brand Layer v2** — 2 | [`profiles/chi-hien/voice_profile.md`](../../profiles/chi-hien/voice_profile.md) | 18 câu Q&A + **Long-term voice direction** (5 chất: ấm, rõ, đẹp, vững, thực tế) |
| **Brand Layer v2** — 3 | [`profiles/chi-hien/write_rules.md`](../../profiles/chi-hien/write_rules.md) | Tone, xưng hô, hook, pattern, format, checklist + **Rule "Những từ dài hạn của thương hiệu" (Section VIII.4)** |

### Thứ tự đọc khi viết content cho chị Hiền (BẮT BUỘC)

```
[1] profiles/chi-hien/about.md                    — biết chị Hiền là ai + định hướng dài hạn
        ↓
[2] profiles/chi-hien/voice_profile.md            — biết giọng + 5 chất voice + ranh giới
        ↓
[3] profiles/chi-hien/write_rules.md              — biết kỹ thuật câu chữ + rule từ dài hạn
        ↓
[4] docs/writing_methods/chi_hien_content_formula_v1.md  — biết đường đi 7 bước
        ↓
[5] docs/writing_methods/SB7_message_check.md     — fill 10 ô structure thông điệp
        ↓
[6] docs/writing_methods/editing_checklist.md     — check trước khi đăng
```

→ KHÔNG được đảo. Skip 1-3 = bài đúng kỹ thuật nhưng sai người. Skip 5-6 = bài có bug đăng public.

### 🌱 Định hướng dài hạn (theo Brand Layer v2)

Chị Hiền **không chỉ là healing / soft content**. Điểm đến dài hạn là giúp phụ nữ có chuyên môn và trải nghiệm sống xây một cuộc sống có:

- **Tự do nội tâm** (qua thiền định / quan sát nội tâm)
- **Dòng tiền bền vững** (không phải làm giàu nhanh)
- **Công việc có cấu trúc** (không phải gồng bằng sức người)
- **Hệ thống hỗ trợ** (chatbot, automation — không phải khoe công cụ)
- **Coaching** (dẫn đường, không dạy đời)
- **Sự bình yên không tách rời thực tế**

→ Voice cần phục vụ định hướng này, không chỉ chạm cảm xúc.

### 🎚 Voice chuẩn — 5 chất (theo voice_profile.md mục "Long-term voice direction")

| Chất | Ý nghĩa |
|---|---|
| **Ấm** | Người đọc thấy an toàn và được hiểu |
| **Rõ** | Người đọc nhìn đúng vấn đề |
| **Đẹp** | Câu chữ có chiều sâu, hình ảnh, sự tinh tế |
| **Vững** | Nội dung có lực dẫn đường, không chỉ an ủi |
| **Thực tế** | Thiền / dòng tiền / hệ thống / coaching / chatbot / automation không tách khỏi đời sống thật |

→ Voice đúng = **đứng cạnh người đọc, nhưng vẫn đủ rõ để mở cho họ một con đường.**

### Nguyên tắc cốt lõi

1. **Insight thật là lõi.** Voice là nhạc trưởng. Formula là đường đi. Writing Rules là bộ lọc cuối.
2. **Kallaway chỉ là Attention Layer** — không phải voice, không phải formula chính. Conflict với voice → bỏ Kallaway, giữ voice.
3. **Writing Rules là bộ lọc cuối, không phải cái lồng.** Rule II.3 đã làm mềm: *"Không cấm một từ chỉ vì nó chung. Chỉ kiểm tra câu có bị mờ không. Ưu tiên sự thật hơn sự cụ thể giả. Nếu không có con số thật, không ép thành con số."*
4. **5 nguyên tắc khi nói về định hướng dài hạn**:
   - Không biến **dòng tiền** thành làm giàu nhanh.
   - Không biến **hệ thống** thành lạnh lùng.
   - Không biến **thiền định** thành né tránh thực tế.
   - Không biến **coaching** thành dạy đời.
   - Không biến **automation** thành khoe công cụ.
5. **Không né các từ dài hạn** (`dòng tiền`, `hệ thống`, `chatbot`, `automation`, `coaching`, `thiền định`, `tự do`, `công việc bền vững`) khi đúng ngữ cảnh — nhưng **không dùng chúng như buzzword hoặc bán hàng quá sớm**. (Xem write_rules.md Section VIII.4)

### 30 bài đầu — quy tắc CTA + chủ đề

**KHÔNG dùng** trong 30 bài đầu:
- ❌ CTA inbox, lead magnet, scarcity, tư vấn, bán hàng, đăng ký
- ❌ Đẩy offer / sản phẩm / khoá học cụ thể
- ❌ Mention giá / "chỉ còn X suất"

**VẪN có thể nói nhẹ** ở tầng niềm tin / góc nhìn (nếu bám insight thật):
- ✅ Tự do (nội tâm, lựa chọn, nhịp sống)
- ✅ Dòng tiền (như cảm giác có thêm quyền chọn — không phải số tiền cụ thể)
- ✅ Hệ thống (như cách tạo khoảng trống — không phải khoe tool)
- ✅ Bình yên (đứng cạnh thực tế — không né tránh)
- ✅ Công việc bền vững (như nền — không phải kết quả nhanh)

→ Dùng để **mở góc nhìn**, không phải mở phễu bán hàng.

### Trạng thái test bước đầu (tuần 1 D1–D7)

| Bài | Format | Verdict | Ghi chú |
|---|---|---|---|
| **D2** | Short FB | ✅ PASS | Bài chuẩn, dùng làm reference Short FB |
| **D1 90s** | Reel mở rộng | ✅ PASS | Pass theo rule II.3 mới (không ép số giả) |
| **D4 90s** | Reel mở rộng | ✅ PASS | Có Plan rõ — reference Reel 90s |
| **D6 100–110s** | Reel mở rộng | ⚠️ Acceptable trade-off | Hook "Có khi…" — trade-off có chủ ý, rule v2.1 III.1 cho phép |

→ Audit chi tiết xem `output/kinh-doanh-27-45/4-thực-thi/week-01-*-audit.md`.

→ **Cần re-audit nhẹ D1/D2/D4/D6 sau update Brand Layer v2** vì voice 5 chất + định hướng dài hạn có thể yêu cầu thêm "vững" / "thực tế" hơn ở một số bài hiện thiên về "ấm/đẹp" thuần.

### 🪝 Hook Bank — chỉ là reference layer

`data/reference_hooks/chi_hien_hook_bank_v2_refined.csv` (365 hooks đã refine):
- **KHÔNG thay** insight thật / voice chị Hiền / Content Formula
- **KHÔNG mặc định** chị Hiền = chỉ mềm
- Hook cần giữ đủ 4 archetype: **Caregiver + Explorer + Lover + Sage**
  - Caregiver: an toàn, đứng cạnh
  - Explorer: mở đường, không bị buộc một khuôn
  - Lover: đẹp, tinh tế
  - Sage: quan sát đúng bản chất, có chiều sâu
- Trong 30 bài đầu, chỉ filter `Stage = "30 bài đầu"` + `Calendar Stage Match` phù hợp với cluster calendar tuần đó.

### Khi nào KHÔNG dùng Formula v1

- Caption ngắn <30 chữ → quá ngắn cho 7 bước.
- Reply DM / tin nhắn nội bộ → không phải content public.
- Story ngắn / nháp test format → format chưa cần audit.

→ Còn lại — bài public cho audience chị Hiền — dùng đầy đủ workflow trên.

---

## 3. Nguyên tắc chuẩn hoá khi nạp vào library

### 3.1 Nguyên tắc, không công thức cụ thể

Library này chứa **nguyên tắc viết phổ quát** — KHÔNG copy nguyên block công thức có bản quyền của creator nào.

Ví dụ:
- ✅ "Hook dạng câu hỏi nội tâm: đặt câu hỏi người đọc đang mang trong người nhưng chưa dám nói ra"
- ❌ "Theo framework AIDA của Russell Brunson..." (cite đặc thù creator)
- ❌ Copy nguyên template bullet "Step 1 / Step 2 / Step 3" của 1 KOL cụ thể

### 3.2 Trích từ data thô — qua bước "lọc"

Khi anh có bài học mới từ Notion / sách / khoá học, trước khi nạp vào library cần **lọc 3 lần**:

| Lọc lần 1 | Lọc lần 2 | Lọc lần 3 |
|---|---|---|
| Bỏ phần cite creator cụ thể | Bỏ phần đặc thù 1 ngành | Bỏ phần lặp với file đã có |
| Tách ra **nguyên tắc** | Generalize thành ngôn ngữ chung | Merge vào file phù hợp |

→ Xem mục 6 dưới đây cho **quy trình ingestion** chi tiết.

### 3.3 Mỗi method KHÔNG cite creator cụ thể (anti-bias)

Library cố ý không gắn tên creator cho từng method vì:
- Tránh idolize 1 creator
- Tránh bias "phải làm như anh X mới đúng"
- Method là tool — ai cũng có thể dùng

---

## 4. Cách dùng — quy trình 4 bước

```
[1] Chọn angle    → Anh tick [x] trong 3-lựa-chọn.md → tim select
[2] Hiểu brand    → Đọc profiles/<brand>/{about, voice_profile, write_rules}
[3] PICK methods  → Mở method_picker.md → chọn 2-4 file cần dùng cho output type
[4] Edit + check  → Áp method → chạy editing_checklist.md trước khi xuất bản
```

### Ví dụ flow cho 1 Reel 60s của chị Hiền:

1. Đã có Angle 01 (từ Bước 6B) + Big idea + CTA
2. Đọc `profiles/chi-hien/{about, voice_profile, write_rules}` — nắm giọng
3. Mở `method_picker.md` → "Reel 60s" → mở 4 file: `short_video_methods.md`, `hook_methods.md`, `storytelling_methods.md`, `persuasion_methods.md`
4. Pick:
   - Hook: "Hard Truth" (vì chị Hiền là Caregiver — fit pattern này)
   - Story: 7 thành phần (skip "xung đột bên trong" cho Reel ngắn)
   - Format: 5 đoạn 60s
   - CTA: soft + comment keyword
5. Viết draft → chạy `editing_checklist.md` → xuất bản

---

## 5. Method KHÔNG ép — chỉ gợi ý

Library này là **kit dụng cụ**, không phải **luật**.

- Anh / chị Hiền có thể chọn KHÔNG dùng method nào nếu thấy không fit
- 1 angle có thể dùng 1-3 method, không nhất thiết phải dùng hết
- Method nào không match brand → SKIP, đừng cố ép

→ Voice profile chị Hiền vẫn là **nguồn cuối cùng** quyết định giọng.

---

## 6. Cách bổ sung bài học mới từ Notion (ingestion process)

> **Tinh thần**: Notion là "kho thô" — Library là "kho đã lọc". Đừng paste thẳng từ Notion vào Library.

### Quy trình 5 bước

```
[1] Đọc bài học gốc trong Notion
[2] Tự hỏi 3 câu (xem 6.1)
[3] Nếu PASS → trích nguyên tắc (xem 6.2)
[4] Map vào file đúng (xem 6.3)
[5] Add với meta + giữ KHÔNG cite creator (xem 6.4)
```

### 6.1 Trước khi add — tự hỏi 3 câu

| Câu hỏi | Nếu KHÔNG → SKIP |
|---|---|
| Method này có **nguyên tắc rõ** đằng sau không (không phải mẹo riêng 1 creator)? | Bỏ |
| Method này có **conflict** với WRITE_RULES_BASE hoặc voice chị Hiền không? | Conflict → bỏ hoặc ghi vào `rejected_methods.md` |
| Method này đã có trong Library chưa (đừng duplicate)? | Có rồi → merge thay vì add mới |

### 6.2 Trích nguyên tắc

Format mỗi method (chuẩn cho cả 8 file):

```markdown
### [Tên ngắn] (vd: Hard Truth Hook)

**Nguyên tắc**: 1-2 câu mô tả core idea
**Khi dùng**: Loại brand / loại content phù hợp
**Khi không dùng**: Trường hợp NÊN tránh
**Ví dụ chung**: 1 ví dụ generic (KHÔNG cite brand cụ thể)
**Lưu ý cho chị Hiền** (optional): nếu method có hint riêng cho brand
```

### 6.3 Map vào file đúng

| Bài học về... | File đích |
|---|---|
| Hook / mở bài | `hook_methods.md` |
| Cấu trúc kể chuyện | `storytelling_methods.md` |
| Format Reel/TikTok | `short_video_methods.md` |
| Thuyết phục / chuyển belief / CTA | `persuasion_methods.md` |
| Anti-pattern / tactic xấu | `rejected_methods.md` |
| Quy tắc viết DON'T (universal) | `../WRITE_RULES_BASE.md` *(không phải Library — là LỚP 2)* |
| Quy tắc viết của 1 brand cụ thể | `../../profiles/<brand>/write_rules.md` *(LỚP 3)* |

### 6.4 Add với meta + KHÔNG cite

Khi add method mới, kèm:
```markdown
<!--
Added: 2026-MM-DD
Source category: notion-storytelling-notes / book-X / course-Y (general — KHÔNG tên creator)
Lockdown: KHÔNG copy block công thức nguyên văn
-->

### [Method name]
...
```

→ Sau 6 tháng vẫn nhớ method từ đâu, nhưng KHÔNG bị "lock" vào 1 creator.

### 6.5 Khi nào KHÔNG add vào Library

- Method **chỉ work cho 1 brand cụ thể** → cho vào `profiles/<brand>/write_rules.md`
- Method là **fact / data** chứ không phải nguyên tắc viết → cho vào nơi khác (knowledge base)
- Method là **công thức bán hàng cụ thể** (vd: pricing strategy) → KHÔNG thuộc Library này

---

## 7. Lifecycle file trong Library

| File | Update khi nào | Ai update |
|---|---|---|
| README.md (file này) | Khi cấu trúc Library thay đổi | Anh + Claude |
| method_picker.md | Khi thêm content type mới | Anh |
| 5 method files | Khi có bài học mới qua quy trình 6 | Anh + nhân viên content lead |
| editing_checklist.md | Khi phát hiện bug pattern mới | Anh |
| rejected_methods.md | Khi gặp tactic xấu cần ghi nhớ | Anh |

→ **Stable, không churn**. Update có chủ đích, không spam.

---

## 8. Tài liệu liên quan

- `../WRITE_RULES_BASE.md` — Luật viết DON'T (LỚP 2)
- `../VOICE_PROFILE_TEMPLATE.md` — Schema voice cho brand mới
- `../../profiles/chi-hien/` — Voice profile cụ thể chị Hiền
- `../MVP_WORKFLOW.md` — Hands-on guide cho anh / nhân viên
- `../SOP_BUILD_INSIGHT_V1.md` — Quy trình kỹ thuật chung

---

**Updated**: 2026-05-10 · v1.4 (sync Brand Layer v2 đã update: Long-term direction + 5 chất voice + rule từ dài hạn + Hook Bank reference)
**Tinh thần**: Method là **bậc thềm**, không phải **luật**. Voice cá nhân vẫn là cuối cùng.
