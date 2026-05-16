# 🔍 Chị Hiền Hook Bank v1 — Review 50 dòng đầu

> **Mục đích**: review 50 hook đầu (H001–H050) của bản auto-classified v1 (365 hooks).
>
> **Brand rule check**:
> - Voice: tĩnh / thật / sâu / đứng cạnh / không phán xét
> - Khách hàng = Hero, chị Hiền = Guide
> - 30 bài đầu: KHÔNG dùng CTA bán hàng / inbox / lead magnet / scarcity / tư vấn
> - Hook bank = reference layer, KHÔNG thay Writing Rules / Content Formula
> - Insight thật = lõi
>
> **Source**: `data/reference_hooks/chi_hien_hook_bank_v1_auto_classified_CSV_FOR_CLAUDE.csv` (paste inline trong chat)
> **Generated**: 2026-05-10 · v1
>
> **KHÔNG sửa**: profile / draft / calendar / code / README / formula / SOP. KHÔNG tạo D8–D30.

---

## 📊 Tổng quan 50 dòng đầu

| Phân loại auto | Số hook | Nhận xét |
|---|---|---|
| PASS | 22/50 | Phần lớn đúng — gentle/insightful tone hợp |
| ADAPT | 25/50 | Đa số chỉ thêm "Có khi" prefix — adapt còn cơ học |
| HOLD | 3/50 | Sales hook (H001, H006, H042) — đúng |
| REJECT | 0/50 | (Không có trong 50 đầu) |

→ Tỉ lệ phân loại tổng thể **chấp nhận được** (~70% đúng), nhưng có nhiều case cần re-classify trước khi áp cho 315 hook còn lại.

---

## 1. 🚨 Hook đang PASS nhưng nên ADAPT/HOLD/REJECT

### H022 — `PASS → nên ADAPT (làm mềm)`
> *"Không phải bạn thiếu thời gian, bạn thiếu một lý do đủ lớn."*

**Lý do**: Câu chứa cấu trúc "thiếu X — thiếu Y" với chủ ngữ "bạn" có thể tạo cảm giác **phán xét** ("bạn thiếu" = bạn thiếu sót). Voice chị Hiền tránh phán xét.

→ Hiện đã ADAPT trong cột Chị Hiền Hook nhưng vẫn giữ y nguyên — nên có cảnh báo "phải thực sự làm mềm, không chỉ thêm 'Có khi'".

**Đề xuất câu chỉnh**: *"Có khi không phải bạn thiếu thời gian — mà là bạn chưa có một lý do đủ thật."* (đổi "đủ lớn" → "đủ thật" cho match voice; chuyển sang Pattern "Không phải X — mà là Y" trong write_rules nhóm 2)

### H042 — `HOLD chuẩn, không cần đổi`
> *"Tiền bạn kiếm ra đang mua điều gì: tự do hay mệt mỏi?"*

→ Phân loại HOLD đúng vì có "Tiền bạn kiếm ra" — implicit về business. Nhưng câu này **không hẳn sales hook**, có thể là reflection. Có thể dùng được sau D8 với adapt nhẹ. Khuyến nghị: chuyển từ HOLD → **ADAPT (Sau 30 bài)** thay vì HOLD cứng.

### H048 — `Mis-classified Tone — nên là Insightful, không phải Confrontational`
> *"Tự do tài chính bắt đầu từ tự do trong suy nghĩ về bản thân."*

→ Câu này **gentle, philosophical** — không gắt. Phân loại Confrontational sai. Nên đổi Tone = Insightful, Risk = Hợp, ADAPT = giữ nguyên (PASS được).

---

## 2. ✅ Hook đang ADAPT có thể chuyển PASS

### H004 — `ADAPT → PASS`
> *"Cuộc đời bạn sẽ trông sao nếu dám sống đúng mong muốn?"*

→ Tone Gentle, không gắt, đúng pattern Q11 chị Hiền (câu hỏi nội tâm). Cột Chị Hiền Hook giữ y nguyên — nghĩa là không cần adapt thật. Nên đổi PASS.

### H007 — `ADAPT → PASS`
> *"Nếu bạn tin mình đủ giỏi, bạn dám làm gì ngay hôm nay?"*

→ Reflective, hợp tone. Cột Chị Hiền Hook giữ y nguyên. Nên PASS.

### H026 — `ADAPT → PASS`
> *"Bạn không mắc kẹt, bạn chỉ chưa dám nói 'đủ rồi'."*

→ Đã có structure Negative Frames (Story Lock essential cho chị Hiền). Cột Chị Hiền Hook giữ y nguyên. Nên PASS.

### H049 — `ADAPT → PASS sau khi đã chỉnh`
> *"Bạn có dám đòi hỏi nhiều hơn từ cuộc đời này không?"*

→ Phiên bản đã adapt: *"Có khi bạn có thể thử đòi hỏi nhiều hơn từ cuộc đời này không?"* — đã làm mềm OK. Có thể coi là PASS sau adapt.

---

## 3. 💸 Hook bán hàng / content / offer trong 30 bài đầu

### Đúng phân loại HOLD (3 hook)
- ✅ **H001**: *"Mình không bán [sản phẩm], mình bán phiên bản mới của bạn."* — Sales pitch rõ
- ✅ **H006**: *"Người ta không mua [sản phẩm], họ mua cảm giác trở thành [phiên bản]."* — Sales framework rõ
- ✅ **H042**: *"Tiền bạn kiếm ra đang mua điều gì..."* — implicit business (xem mục 1)

### KHÔNG có hook bán hàng nào lọt vào "30 bài đầu" trong 50 dòng đầu ✅

→ Auto-classifier làm tốt trong việc giữ sales hook ra khỏi 30 bài đầu.

### ⚠️ Lưu ý: Hook đụng "tiền" được giữ trong 30 bài đầu (H034–H041, H045–H047, H050)

Các hook này về tiền nhưng **dạng reflection cá nhân** (không sales), được phân loại 30 bài đầu. Điều này hợp lý nếu insight gốc audience có nhắc đến tiền (vd cluster TIEN_BAC_BINH_YEN trong calendar). Nhưng cần lưu ý:

- Trong 30 bài đầu (cluster "Bắt đầu lại — không cần gồng"), audience đang ở AWARE stage — có thể **chưa sẵn sàng** với chủ đề tiền sâu.
- Đề xuất: chỉ dùng các hook tiền này ở **D22–D30** (cluster "Tiền để mình thở" — DECIDE stage) theo calendar v1.

---

## 4. 🎤 Cột "Chị Hiền Hook" — kiểm tra voice

### Pattern phổ biến: thêm "Có khi" prefix

Hơn 50% hook ADAPT trong 50 dòng đầu chỉ áp công thức:
> Original: `[Câu confrontational]` → Chị Hiền: `Có khi [Câu confrontational]`

→ **Đây là adapt cơ học, không thực sự làm mềm voice.** Voice chị Hiền không chỉ thêm "Có khi" mà thay đổi **structure + từ ngữ**.

**Ví dụ adapt cơ học**:
- H003: *"Bạn đang làm việc hay đang né đối diện với chính mình?"* → *"Có khi bạn đang làm việc hay đang né đối diện với chính mình?"* — vẫn là câu hỏi confrontational, chỉ thêm "Có khi"

**Ví dụ adapt tốt** (đáng học):
- H028: *"Khi nào bạn mới dừng xin phép được sống đúng với mình?"* → *"Có khi mình chỉ cần bắt đầu bằng việc dừng xin phép được sống đúng với mình?"* — đổi structure: từ chất vấn audience → mời cùng quan sát
- H008: *"Bạn đã bao lần nói 'để mai'?"* → *"Có bao nhiêu lần mình đã nói 'để mai'?"* — chuyển ngôi từ "bạn" → "mình", nhẹ nhàng hơn nhiều

→ **Bài học**: adapt formula nên là **đổi ngôi + đổi structure**, không chỉ thêm prefix.

### Vấn đề khác
- Một số hook đã ADAPT nhưng giữ y nguyên (H004, H007, H012, H026, H049 phần) — chứng tỏ phân loại nhầm, đáng PASS
- Một số hook ADAPT nhưng vẫn còn từ judgemental (H013 — "bao lâu rồi mà chưa nhận ra" — vẫn confrontational)

---

## 5. 📋 Rule cần chỉnh trước khi phân loại 315 hook còn lại

### Rule #1 — Phân biệt Tone chuẩn

Hiện auto-classifier dùng từ khoá để gán Tone, dẫn đến nhiều case sai:
- H048: gán Confrontational nhưng câu gentle
- H013: gán Confrontational nhưng phải xét context

**Đề xuất**:
- **Confrontational** = chứa "bạn..." + cấu trúc chất vấn + có hint phán xét
- **Reflective/Insightful** = câu khẳng định / quan sát, không trực tiếp đối chất
- **Gentle** = có "có thể", "có lẽ", câu hỏi mở không ép

### Rule #2 — Adapt KHÔNG chỉ là thêm "Có khi"

Khi gán ADAPT, công thức cần phải:
1. **Đổi ngôi**: "Bạn đang..." → "Có khi mình..." (chuyển sang reflection cùng audience)
2. **Đổi structure**: từ chất vấn → mời quan sát
3. **Bỏ từ judgemental**: "thiếu", "không có", "chưa biết" → "chưa rõ", "đang cần nhìn lại"

→ Nếu chỉ thêm "Có khi" mà giữ y câu cũ → **không phải ADAPT**, nên đánh PASS hoặc REJECT (nếu confrontational quá).

### Rule #3 — Phân biệt Sales hook vs Reflection về tiền

Hiện trộn lẫn:
- **Sales hook** (HOLD): có "bán", "khách", "sản phẩm", "phiên bản mới của bạn" → đúng
- **Reflection về tiền** (PASS / Sau 30 bài): có "tiền", "tự do tài chính", "thu nhập" — không sales

**Đề xuất**: tách 2 loại. Reflection tiền có thể PASS cho 30 bài đầu nếu audience cluster có chủ đề tiền (theo calendar D22–D30).

### Rule #4 — Hook đụng "tiền/sự nghiệp" trong 30 bài đầu — cần align với calendar

Calendar tuần 1 có cluster "Bắt đầu lại — không cần gồng" (BINH_YEN_CHUA_LANH + KINH_DOANH_KIET_SUC). Hook tiền không phù hợp tuần 1.

**Đề xuất**: thêm cột mới `Calendar Stage Match` để map hook → tuần phù hợp:
- Tuần 1 (D1–D7): chủ đề bình yên, kiệt sức — hook về cảm xúc, ranh giới
- Tuần 2 (D8–D14): giá trị bản thân — hook về self-discovery
- Tuần 3 (D15–D21): gia đình, gánh nặng — hook về vai trò
- Tuần 4 (D22–D30): tiền, tự do — hook về tài chính (nhưng vẫn không sales)

### Rule #5 — Hook spiritual / linh hồn / vũ trụ — không dùng

Trong 50 đầu chưa thấy nhưng đã được flag trong CSV (H098, H099, H145, H199, H249, H351, H355). Brand chị Hiền không dùng "linh hồn", "vũ trụ", "vibration" trong nội dung public — nên REJECT, không adapt.

### Rule #6 — Hook có placeholder `[sản phẩm]`, `[X]`, `[kết quả]` — cần fill thật

Vài hook có `[sản phẩm]`, `[ngày cụ thể]`. Nếu giữ placeholder trong production → bài thành template lộ. Cần rule: **không giữ placeholder qua phase production**.

---

## 6. 📝 Tổng kết & đề xuất hành động

### Tỉ lệ pass/fail của 50 hook đầu
- **PASS đúng (giữ nguyên)**: 22 hook ✅
- **ADAPT đúng (cần chỉnh thật)**: ~15 hook ⚠️
- **ADAPT cơ học (chỉ thêm "Có khi", có thể PASS)**: ~10 hook ⚠️
- **Mis-classified Tone**: 1–2 hook (H048, H013)
- **HOLD đúng**: 3 hook ✅

→ **Khoảng 70% phân loại OK**, 30% cần chỉnh.

### Trước khi auto-classify 315 hook còn lại — chỉnh 6 rule trên

1. Refine rule phân loại Tone (Rule #1)
2. Refine adapt formula — không chỉ thêm "Có khi" (Rule #2)
3. Tách Sales hook vs Reflection tiền (Rule #3)
4. Thêm cột Calendar Stage Match (Rule #4)
5. REJECT hook spiritual rõ ràng (Rule #5)
6. Loại bỏ placeholder trước production (Rule #6)

### Khi nào dùng Hook Bank này
- ✅ Khi viết hook draft cho bài chị Hiền — dùng làm gợi ý, không copy nguyên văn
- ✅ Khi cần inspiration cho 1 chủ đề cụ thể — filter theo "Use Case"
- ❌ KHÔNG copy hook gốc (cột Original Hook) — voice không phải của chị Hiền
- ❌ KHÔNG dùng làm Writing Rules / Content Formula — đây là reference layer
- ❌ KHÔNG tự fill `[sản phẩm]` mà chưa có offer thật

### Nguyên tắc cuối cùng

> Hook bank = **menu inspiration**.
> Insight thật + Voice chị Hiền + Content Formula v1 = **bếp chính**.
> Không có insight thật → không hook nào cứu được bài.

---

## 7. Phụ lục — bảng nhanh 50 hook đầu

| ID | Verdict suggested | Note |
|---|---|---|
| H001 | HOLD ✅ | Sales hook |
| H002 | ADAPT ✅ | Cần đổi structure thật, không chỉ "Có khi" |
| H003 | ADAPT ⚠️ | Vẫn confrontational sau adapt |
| H004 | **PASS** (đổi từ ADAPT) | Gentle đủ rồi |
| H005 | ADAPT ✅ | Pattern Negative Frames OK |
| H006 | HOLD ✅ | Sales hook |
| H007 | **PASS** (đổi từ ADAPT) | Gentle đủ rồi |
| H008 | ADAPT ✅ | Adapt structure tốt (đổi ngôi) |
| H009 | PASS ✅ | |
| H010 | PASS ✅ | |
| H011 | ADAPT ✅ | Adapt làm mềm tốt |
| H012 | PASS ✅ | |
| H013 | ADAPT ⚠️ | Adapt chưa đủ — vẫn "bao lâu rồi mà chưa nhận ra" |
| H014 | PASS ✅ | |
| H015 | ADAPT ⚠️ | Adapt chỉ giữ y câu cũ |
| H016 | PASS ✅ | |
| H017 | PASS ✅ | |
| H018 | ADAPT ⚠️ | "ngày cuối cùng" hơi nặng — cần đổi |
| H019 | PASS ✅ | |
| H020 | PASS ✅ | |
| H021 | PASS ✅ | |
| H022 | ADAPT ⚠️ | Đổi "đủ lớn" → "đủ thật" |
| H023 | ADAPT ⚠️ | Vẫn confrontational sau adapt |
| H024 | PASS ✅ | |
| H025 | ADAPT ✅ | "Có khi" prefix OK ở case này |
| H026 | **PASS** (đổi từ ADAPT) | Negative Frames đẹp, không cần adapt |
| H027 | PASS ✅ | |
| H028 | ADAPT ✅ | Adapt structure rất tốt |
| H029 | PASS ✅ | |
| H030 | PASS ✅ | |
| H031 | PASS ✅ | |
| H032 | PASS ✅ | |
| H033 | ADAPT (Sau 30 bài) ✅ | Đụng tiền + tâm lý — đúng phải sau D7 |
| H034 | PASS ✅ | |
| H035 | PASS ✅ | |
| H036 | PASS ✅ | |
| H037 | PASS ✅ | |
| H038 | ADAPT (Sau 30 bài) ✅ | "không sai" + "sai là" — gắt nhẹ |
| H039 | PASS ✅ | |
| H040 | PASS ✅ | |
| H041 | PASS ✅ | |
| H042 | **ADAPT (Sau 30 bài)** (đổi từ HOLD) | Reflection tiền, không sales — không cần HOLD cứng |
| H043 | ADAPT ✅ | Đổi ngôi tốt |
| H044 | ADAPT (Sau 30 bài) ✅ | "trốn việc chữa lành" — sâu, hợp Sau 30 bài |
| H045 | PASS ✅ | |
| H046 | PASS ✅ | |
| H047 | PASS ✅ | |
| H048 | **Tone fix: Insightful + PASS** (đổi từ Confrontational + ADAPT) | Câu gentle, không gắt |
| H049 | ADAPT ✅ | Adapt làm mềm OK |
| H050 | PASS ✅ | |

→ **Sau review**: thay đổi đề xuất cho **6 hook**: H004 (ADAPT→PASS), H007 (ADAPT→PASS), H026 (ADAPT→PASS), H042 (HOLD→ADAPT Sau 30), H048 (Tone fix + PASS).

---

**File này**: review only · Generated 2026-05-10 · v1
**Source CSV**: paste inline trong chat (data/reference_hooks/chi_hien_hook_bank_v1_auto_classified_CSV_FOR_CLAUDE.csv)

**KHÔNG sửa**: profile · draft · calendar · code · README · formula · SOP. KHÔNG tạo D8–D30.
