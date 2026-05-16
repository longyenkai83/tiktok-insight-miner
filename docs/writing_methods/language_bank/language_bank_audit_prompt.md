# 🤖 Language Bank Audit — Prompt mẫu

> **Mục đích**: Prompt sẵn để paste vào Claude (hoặc LLM khác) → tự động phân tích bài viral theo Language Bank Template.
>
> **Cách dùng**: Copy prompt → paste vào Claude → paste bài cần audit → nhận output bảng 7 cột.

---

## Prompt chính

```
Bạn là chuyên gia phân tích câu chữ tiếng Việt.

Nhiệm vụ: Phân tích BÀI VIẾT TIẾNG VIỆT bên dưới theo Language Bank Template gồm 7 cột:

1. Câu gốc (1 câu, copy nguyên văn)
2. Biện pháp tu từ (so sánh, ẩn dụ, hoán dụ, nhân hoá, nói quá, nói giảm, điệp ngữ, chơi chữ, tương phản, liệt kê, đảo ngữ, câu hỏi tu từ — pick 1-2 cái rõ nhất; ghi "Không" nếu không có)
3. Từ loại nổi bật (đặc biệt chú ý: động từ mạnh, tình thái từ, trợ từ, phó từ — vì 4 loại này tạo nên sức câu tiếng Việt)
4. Nhóm từ biểu đạt (từ láy / từ lóng / từ đồng âm / từ đồng nghĩa / từ trái nghĩa / từ địa phương / từ bắt trend / thành ngữ-tục ngữ — ghi "Không" nếu không có)
5. Tone / Register (trang trọng / thân mật / suồng sã / thơ / báo chí — pick 1 chủ đạo, có thể note 1 phụ)
6. Điểm mạnh (1-2 câu — vì sao câu này đắt?)
7. Học được gì (1 câu — nguyên tắc rút ra, KHÔNG copy nguyên câu)

YÊU CẦU OUTPUT:
- Chọn 5-10 câu HAY NHẤT trong bài (không cần audit cả bài).
- Format markdown table 7 cột.
- Cuối bảng: rút ra 3-5 PATTERN LẶP LẠI trong bài (cấu trúc / từ ngữ / nhịp).
- KHÔNG bịa biện pháp nếu không thấy. KHÔNG khen suông.

CẢNH BÁO:
- Nếu câu là trần thuật bình thường, không có biện pháp tu từ → ghi "Không / câu trần thuật" — đừng cố gán.
- Tone phải nhất quán đánh giá: 1 câu thường chỉ có 1 tone chủ đạo.
- Nếu bài thuộc tone báo chí / data → biện pháp tu từ thường ít hoặc không có → đó là bình thường.

BÀI CẦN PHÂN TÍCH:
[paste bài tiếng Việt vào đây]
```

---

## Prompt phụ — sau khi audit 5-10 bài, rút pattern chung

Sau khi anh đã audit 5-10 bài của 1 creator, dùng prompt này để tổng hợp:

```
Mình đã audit 5 bài của [tên creator] theo Language Bank Template.
Dữ liệu audit ở phần PATTERN cuối mỗi bài.

Nhiệm vụ:
1. Xác định 5-7 PATTERN LẶP LẠI qua ≥ 3/5 bài (về biện pháp tu từ, từ loại đặc trưng, nhịp câu, cấu trúc đoạn).
2. Đánh giá: pattern nào là "bài học chung" (universal — ai cũng học được), pattern nào là "cá tính riêng creator" (chỉ hợp creator đó).
3. Đề xuất: với brand [tên brand mình] có voice [paste 2-3 câu mô tả voice], pattern nào nên áp dụng / không nên áp dụng?

OUTPUT FORMAT:
## Pattern lặp ≥ 3/5 bài
1. [Pattern] — bằng chứng (số bài xuất hiện)
...

## Phân loại
- Universal (áp dụng được cho nhiều brand): ...
- Cá tính creator (chỉ hợp creator đó): ...

## Khuyến nghị cho brand [X]
- ✅ Áp dụng: ... (lý do)
- ⚠️ Test trước: ... (lý do)
- ❌ Không áp dụng: ... (lý do)

DỮ LIỆU AUDIT:
[paste 5 bảng audit từ prompt chính vào đây]
```

---

## Prompt bonus — check 1 đoạn draft của mình

Khi anh viết xong draft, muốn check nhanh 1 đoạn về câu chữ:

```
Bạn là chuyên gia câu chữ tiếng Việt. Phân tích đoạn draft bên dưới theo 4 trục:

1. **Biện pháp tu từ** — đoạn này có bao nhiêu biện pháp? Có bị nhồi quá hay thiếu?
2. **Từ loại** — mật độ động từ mạnh? Có thiếu tình thái từ / trợ từ / phó từ làm câu khô không?
3. **Nhóm từ biểu đạt** — có dùng từ láy / thành ngữ / cặp trái nghĩa nào? Có hợp lý không?
4. **Tone** — có nhất quán không? Có lẫn tone (vd thân mật + jargon) không?

Cuối cùng: đề xuất 3 chỉnh sửa cụ thể nhất (chỉ ra câu nào, sửa thành gì, vì sao).

KHÔNG khen chung chung. KHÔNG bịa vấn đề. Nếu đoạn ổn → nói "ổn", chỉ ra điểm mạnh.

ĐOẠN DRAFT:
[paste đoạn vào đây]

VOICE PROFILE BRAND (để check tone đúng không):
[paste 3-5 dòng key về voice — ví dụ: "Brand chị Hiền: tone thân mật-trầm, xưng mình/bạn, không dùng từ lóng, không buzzword, ưu tiên thuần Việt"]
```

---

## 📌 Lưu ý khi dùng prompt với Claude

1. **Paste cả bối cảnh brand** vào prompt bonus → Claude sẽ đánh giá đúng tone.
2. **Đừng tin 100%** Claude — cuối cùng anh / brand owner đọc lại. Claude có thể bịa biện pháp khi câu không có.
3. **Chạy 2 lần** với prompt chính trên cùng 1 bài → so sánh → cái nào trùng = chắc, cái nào lệch = bỏ qua.
4. **Lưu output** vào `output/<niche>/_master/audit-language-[creator]-[date].md` để dùng lại.

---

**Updated**: 2026-05-10 · v1
