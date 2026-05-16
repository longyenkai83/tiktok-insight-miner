# 📚 SOP — Thêm / Cập nhật Writing Method

> **Phiên bản**: v1 (2026-05-10)
> **Đối tượng**: anh Tuấn + Claude + nhân viên content lead
> **Phạm vi áp dụng**: mọi method được thêm vào hệ thống — bắt đầu từ brand chị Hiền, áp được cho brand khác sau này

---

## 1. Mục đích SOP

Quy trình chuẩn khi thêm hoặc cập nhật một writing method (Kallaway / SB7 / Vietnamese Language Layer / formula brand…) vào hệ thống — để:

1. **Đảm bảo method mới KHÔNG thay thế** insight thật, voice brand, hoặc workflow chính.
2. **Tránh việc Claude dùng nhầm method như công thức viết chính** — kéo bài về template, mất giọng riêng.
3. **Giữ workflow ổn định** — không loạn khi có method mới đến từ Notion / sách / khoá.
4. **Giữ tính re-runnable** — sau 6 tháng vẫn nhớ method nào để làm gì.

---

## 2. Phân loại method (6 lớp)

Mỗi method khi vào hệ thống phải được **gán đúng 1 trong 6 loại** dưới đây. Loại quyết định: file đặt ở đâu, ai dùng, conflict thì cái nào thắng.

| # | Loại | Vai trò | Ví dụ hiện có | File path |
|---|---|---|---|---|
| **1** | **Core Formula** | Công thức chính của brand — orchestration tất cả các lớp khác | Chị Hiền Content Formula v1 | `docs/writing_methods/<brand>_content_formula_v1.md` |
| **2** | **Attention Layer** | Tăng hook / retention — kỹ thuật giữ chân 3 giây đầu + nhịp giữa bài | Kallaway | (nằm trong Core Formula, mục Attention) |
| **3** | **Message Layer** | Kiểm tra structure thông điệp đầy đủ chưa | SB7 Message Check | `docs/writing_methods/SB7_message_check.md` |
| **4** | **Language Layer** | Làm câu chữ tiếng Việt có nhịp + sắc thái + hình ảnh | Vietnamese Language Layer | `docs/writing_methods/language_bank/` |
| **5** | **Editing Checklist** | Kiểm tra trước khi publish | Editing Checklist | `docs/writing_methods/editing_checklist.md` |
| **6** | **Reference Library** | Thư viện tham khảo — KHÔNG tự động áp dụng vào bài | hook_methods, storytelling_methods, persuasion_methods, rejected_methods | `docs/writing_methods/<topic>_methods.md` |

→ **Quy tắc gán loại**:
- 1 method = **1 loại chính**. Nếu method có 2 vai trò (vd Kallaway có cả attention check + CTA framework) → chọn vai trò chủ đạo.
- Nếu không gán được loại → method chưa đủ rõ → **hoãn**, không nhồi vào hệ thống.
- Reference Library KHÔNG bao giờ được tự động áp dụng — chỉ tra cứu khi cần.

---

## 3. Nguyên tắc bắt buộc (7 không phá vỡ)

| # | Nguyên tắc | Ý nghĩa |
|---|---|---|
| 1 | **Insight thật là lõi** | Không có quote audience từ pipeline → method nào cũng vô dụng. Method KHÔNG sinh insight. |
| 2 | **Audience là Hero** | Mọi method phải phục vụ audience. Brand owner / chị Hiền là Guide, không phải Hero. |
| 3 | **Brand voice là nhạc trưởng** | Voice profile của brand quyết tone cuối cùng. Method là nhạc cụ. |
| 4 | **Method mới chỉ là công cụ** | Không biến method thành mục đích. Output cuối là **bài chạm audience**, không phải "bài đã pass method X". |
| 5 | **Conflict → voice brand thắng** | Khi method (Kallaway / SB7 / …) conflict với voice brand → bỏ method, giữ voice. |
| 6 | **Không biến method thành công thức cứng** | Method = checklist tham khảo. Không "fill 7 ô rồi ghép thành script". |
| 7 | **Không update README/index trước khi test** | Method chưa pass test → không link vào README, không add vào workflow chính. Test rồi mới publicize. |

---

## 4. Quy trình thêm / cập nhật method (6 bước)

```
[1] Xác định loại
        ↓
[2] Tạo / update file method riêng
        ↓
[3] Ghi rõ DÙNG ĐỂ + KHÔNG DÙNG ĐỂ
        ↓
[4] KHÔNG sửa draft / calendar / code / profile
        ↓
[5] Test trên 1-2 bài cũ
        ↓
[6] PASS → mới link vào README / workflow chính
```

### 4.1 Bước 1: Xác định loại

Trả lời 3 câu trước khi bắt đầu:
- Method này thuộc loại nào trong 6 loại ở mục 2?
- Method này **thay thế** hay **bổ sung** cho method đã có?
- Có conflict tiềm ẩn với voice brand nào đang dùng không?

→ Nếu không gán được loại / conflict không rõ → **hoãn**, hỏi anh trước khi tạo file.

### 4.2 Bước 2: Tạo / update file method riêng

- **Method mới** → tạo file mới ở path đúng theo bảng phân loại (mục 2).
- **Method đã có** → update file hiện tại, KHÔNG tạo file v2 song song trừ khi có lý do rõ.
- Đặt tên file theo convention: `<topic>_<type>.md` (vd: `SB7_message_check.md`, `chi_hien_content_formula_v1.md`).
- KHÔNG tạo file ngoài `docs/writing_methods/` nếu method là generic.
- KHÔNG đặt method brand-specific trong folder generic mà không note rõ "exception".

### 4.3 Bước 3: Ghi rõ DÙNG ĐỂ + KHÔNG DÙNG ĐỂ

Mỗi file method PHẢI có 2 mục đầu tiên:
- **Vai trò** (1-3 câu): method này dùng để làm gì.
- **KHÔNG được làm gì**: method này KHÔNG thay thế cái nào. Conflict với cái nào → cái kia thắng.

→ Thiếu 1 trong 2 mục → file chưa xong.

### 4.4 Bước 4: KHÔNG sửa draft / calendar / code / profile

Trong bước tạo / update method:
- ❌ KHÔNG sửa file draft bài viết (D1-D7, etc.)
- ❌ KHÔNG sửa calendar (`content-calendar-*.json/.md`)
- ❌ KHÔNG sửa code module (`production.py`, `content_calendar.py`, `cli.py`, etc.)
- ❌ KHÔNG sửa brand profile (`profiles/<brand>/`)
- ❌ KHÔNG sửa strategy config (`strategy_configs/`)
- ❌ KHÔNG sửa niche config (`niche_configs/`)

→ Method đứng riêng. Việc áp dụng method vào draft là **bước riêng**, sau khi method đã pass test.

### 4.5 Bước 5: Test method trên 1-2 bài cũ

Audit ngược (xem chi tiết mục 5 dưới):
- Chọn 1-2 bài đã viết (vd D2, D6).
- Chạy method check trên bài đó.
- Chấm PASS / NEEDS LIGHT EDIT / FAIL.
- Đề xuất câu chỉnh nếu có — KHÔNG tự sửa bài.

### 4.6 Bước 6: PASS → link vào README / workflow chính

Chỉ khi method **pass test trên ≥ 1 bài thật**:
- Update `docs/writing_methods/README.md` (index) để add link.
- Update workflow chính trong `docs/MVP_WORKFLOW.md` mục 7D nếu method ảnh hưởng order of operations.
- Update Core Formula brand (vd `chi_hien_content_formula_v1.md`) nếu method là Attention/Message/Language Layer.

→ KHÔNG link vào README ngay khi tạo file. KHÔNG promote method chưa test.

---

## 5. Quy trình test method

```
Chọn 1-2 bài cũ
        ↓
Chỉ audit — KHÔNG viết lại
        ↓
Chấm PASS / NEEDS LIGHT EDIT / FAIL
        ↓
Đề xuất câu chỉnh (nếu cần)
        ↓
Anh / brand owner duyệt
        ↓
Mới sửa bài (nếu được duyệt)
```

### 5.1 Quy tắc test

- **Chỉ audit, không viết lại**: ghi câu hiện tại + câu đề xuất, KHÔNG override file bài.
- **Test trên bài đã có** (vd D2 = Short FB, D6 = Reel chạm sâu) — không test trên bài mới chưa viết.
- **Chấm 3 mức**: PASS / NEEDS LIGHT EDIT / FAIL. Không có "tốt hơn" / "cũng được" — phải rõ.
- **Output audit là 1 file riêng**: `output/<niche>/4-thực-thi/<test-name>-audit.md`. KHÔNG sửa file bài.

### 5.2 Khi nào method PASS

- ≥ 1 bài đã viết PASS toàn bộ check của method.
- Hoặc bài đã viết FAIL nhưng câu đề xuất chỉnh **không phá voice brand**.
- Method KHÔNG conflict với voice profile của brand đang test.

### 5.3 Khi nào method FAIL — không add vào hệ thống

- Mọi bài test đều phải chỉnh nặng để pass method → method ép quá, không fit voice.
- Câu đề xuất chỉnh phá voice brand (vd thêm FOMO, thêm guru tone) → method không phù hợp.
- Method conflict với 1 trong 7 nguyên tắc bắt buộc (mục 3).

→ FAIL → **không add**, có thể save vào `rejected_methods.md` để tránh re-evaluation sau này.

---

## 6. Case study hiện tại: Kallaway

Kallaway là ví dụ thực tế về cách áp SOP này. Lessons learned:

### 6.1 Phân loại đúng
- Kallaway được đưa vào như **Attention Layer** (loại 2 trong mục 2).
- KHÔNG gọi là "Kallaway Formula" — vì sẽ ngầm hiểu là Core Formula → conflict voice brand.
- Tên đúng: **"Kallaway Attention Layer"** trong Chị Hiền Content Formula v1.

### 6.2 KHÔNG dùng để
- Thay voice chị Hiền.
- Viral-script công thức (research shock facts → 3 hook versions → chạy theo viral).
- FOMO / scarcity / khan hiếm giả.
- Lead magnet trap ("comment 'CHECKLIST' để nhận tài liệu").
- Inbox tư vấn / follow ngay trong 30 bài đầu (chưa đủ trust).

### 6.3 Giữ lại — essentials cho 30 bài đầu
- Hook rõ — 4 yếu tố (No Delay / Clarity / Relevance / Intrigue).
- **Contrast** — cơ chế tương phản (đã có trong VN Language Layer).
- **Thought Broadcasting** — gọi câu audience đang nghĩ.
- **Alignment** — Hook / Body / CTA cùng nói 1 ý (FB) hoặc Spoken / Text / Visual cùng nói 1 ý (Reel).
- **CTA mềm** đúng nhiệt độ thị trường lạnh.

### 6.4 Bỏ / rút gọn
- Lead magnet sớm.
- Inbox tư vấn.
- Follow ngay.
- Scarcity + deadline.
- Bảng kỹ thuật quá dài (Dopamine Ladder 6 tầng chi tiết → bỏ section riêng).
- 9 Hook Formats → rút còn 4 ưu tiên cho 30 bài đầu.
- 6 Story Locks → giữ 2 essentials, 4 cái khác mention 1 dòng.

### 6.5 Bài học rút ra cho method tương lai

| Bài học | Áp dụng cho method tới |
|---|---|
| Method gốc có nhiều phần — không phải tất cả essentials | Lọc trước khi nạp. Phần nào "nice to have" → bỏ hoặc đưa xuống "dùng sau". |
| Wording gốc dễ kéo về tone marketing | Adapt từng câu theo voice brand. KHÔNG copy y nguyên ví dụ CTA gốc. |
| Method có thể có CTA framework nhưng brand không sẵn sàng | Phân biệt theo nhiệt độ audience. 30 bài đầu = Lạnh = CTA mềm thôi. |
| Source là Notion private → không phải ai cũng access | Tóm tắt vào file, không link Notion làm reference duy nhất. |

---

## 7. Output chuẩn sau mỗi lần update

Sau MỌI lần thêm / update method, Claude (hoặc người làm) phải báo cáo đúng 4 mục:

### 7.1 File đã tạo / sửa
Liệt kê đường dẫn file cụ thể (markdown link). Phân biệt:
- File **tạo mới**
- File **sửa** (kèm note mục nào)

### 7.2 Mục nào đã sửa
Cụ thể section (mục 4 / mục 8 / etc.). KHÔNG nói chung chung "đã update file".

### 7.3 Có sửa ngoài scope không
Trả lời thẳng:
- **Không** — nếu chỉ sửa file được phép.
- **Có** — list rõ file ngoài scope đã sửa + lý do (phải có justification mạnh).

### 7.4 Có cần test không
Trả lời thẳng:
- **Có** — đề xuất bài cũ nào dùng để test (vd D2, D6).
- **Không** — chỉ khi update là wording / typo / format. Nếu là logic / nguyên tắc / công thức → bắt buộc test.

---

## 8. Anti-pattern khi thêm method

| # | Anti-pattern | Hậu quả |
|---|---|---|
| 1 | Tạo file method và link luôn vào README chưa test | Workflow loạn, nhân viên dùng method chưa verified |
| 2 | Sửa draft bài cùng lúc với tạo method | Khó audit method có thực sự work không |
| 3 | Copy nguyên framework gốc không adapt | Mất voice brand, bài thành template |
| 4 | Gán method vào nhiều loại cùng lúc (vừa Core vừa Attention vừa Reference) | Confused về vai trò, không biết khi nào dùng |
| 5 | Skip "DÙNG ĐỂ + KHÔNG DÙNG ĐỂ" — chỉ ghi DÙNG ĐỂ | 6 tháng sau quên, dùng method sai context |
| 6 | Cite nguồn private (Notion / Slack) làm reference duy nhất | Người mới onboard không truy cập được |
| 7 | Bump version v1 → v2 mỗi lần edit nhỏ | Mất history, khó track thay đổi thật |
| 8 | Dùng method để biện minh khi bài không chạm | Method là công cụ, không phải shield. Bài không chạm = quay lại insight + voice. |

---

## 9. Quy trình emergency — khi method đã add nhưng phát hiện sai

Nếu phát hiện method đã add nhưng:
- Conflict với voice brand
- Đẩy bài về tone marketing
- Audience phản ứng tiêu cực

→ **Quy trình rollback**:
1. KHÔNG xoá file method (giữ làm history).
2. Update file method, thêm section đầu: **"⚠️ DEPRECATED — không dùng từ ngày X. Lý do: ..."**
3. Update README index — bỏ link đến method này.
4. Update Core Formula của brand (vd `chi_hien_content_formula_v1.md`) — bỏ reference.
5. Audit các bài đã viết theo method này — note bài nào cần re-edit.
6. Move file vào subfolder `docs/writing_methods/_deprecated/` nếu chắc chắn không dùng lại.

→ KHÔNG xoá silent. Mọi rollback phải có note rõ lý do.

---

## 10. Lifecycle SOP này

- File này **stable** — chỉ update khi có insight mới về quy trình thêm method.
- Update theo version (`v1` → `v2`) khi thay đổi 1 trong 7 nguyên tắc bắt buộc (mục 3).
- KHÔNG update để add nguyên tắc mới chỉ vì 1 case lẻ — đợi pattern lặp ≥ 3 lần.

---

## 11. Tài liệu liên quan

- [SOP_BUILD_INSIGHT_V1.md](SOP_BUILD_INSIGHT_V1.md) — quy trình build insight pipeline
- [MVP_WORKFLOW.md](MVP_WORKFLOW.md) — workflow vận hành hàng ngày, mục 7D về Writing Methods
- [WRITE_RULES_BASE.md](WRITE_RULES_BASE.md) — luật viết chung
- [writing_methods/README.md](writing_methods/README.md) — index Writing Method Library
- [writing_methods/chi_hien_content_formula_v1.md](writing_methods/chi_hien_content_formula_v1.md) — case study Core Formula brand chị Hiền
- [writing_methods/SB7_message_check.md](writing_methods/SB7_message_check.md) — case study Message Layer
- [writing_methods/language_bank/README.md](writing_methods/language_bank/README.md) — case study Language Layer

---

**Updated**: 2026-05-10 · v1
**Tinh thần**: Method là **công cụ**, không phải **luật**. Insight + Voice là cuối cùng. Nếu method làm bài mất chạm → bỏ method, giữ chạm.
