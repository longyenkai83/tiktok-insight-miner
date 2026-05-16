# 🇻🇳 Vietnamese Language Bank

> **Vai trò**: Lớp **câu chữ tiếng Việt** — bổ sung cho hook / storytelling / persuasion. Giúp bài viết có **nhịp, sắc thái, hình ảnh** hơn.
>
> **Đối tượng dùng**: Anh / nhân viên content / Claude khi viết draft, edit câu, hoặc audit bài viral.

---

## 1. Language Bank này KHÔNG thay thế

| KHÔNG thay thế | Vẫn cần dùng trước |
|---|---|
| ❌ Hook / Storytelling / Persuasion methods | `../hook_methods.md`, `../storytelling_methods.md`, `../persuasion_methods.md` |
| ❌ Voice profile của brand | `profiles/<brand>/voice_profile.md` |
| ❌ Insight thật từ pipeline | `output/<niche>/<date>/classified.json` |

Language Bank chỉ là **lớp câu chữ** — đứng SAU cùng, áp dụng KHI viết draft. Không sinh ý tưởng, không quyết angle.

---

## 2. 7 file trong Language Bank

| File | Trả lời câu hỏi |
|---|---|
| [vietnamese_rhetoric.md](vietnamese_rhetoric.md) | "Câu này có thể dùng biện pháp tu từ nào để mạnh hơn?" |
| [vietnamese_word_classes.md](vietnamese_word_classes.md) | "Câu này thiếu loại từ nào (động từ mạnh? tình thái từ? phó từ?) để tự nhiên hơn?" |
| [expressive_word_groups.md](expressive_word_groups.md) | "Có thể dùng từ láy / thành ngữ / từ trái nghĩa nào để câu có sắc?" |
| [tone_and_register.md](tone_and_register.md) | "Câu này tone gì? Có lẫn tone không? Có hợp brand không?" |
| [language_bank_template.md](language_bank_template.md) | "Bài viral này hay nhờ điều gì về câu chữ?" — bảng audit 7 cột |
| [language_bank_audit_prompt.md](language_bank_audit_prompt.md) | Prompt mẫu để Claude phân tích bài viral theo template |

(File hiện tại — README — là index.)

---

## 3. Khi nào dùng — quy trình ngắn

```
[1] Có outline (từ calendar / brief)
[2] Pick hook + storytelling + persuasion method (đã có)
[3] TRƯỚC KHI viết draft → mở Language Bank, chọn:
        • 1-2 biện pháp tu từ phù hợp insight
        • Từ loại nổi bật (đặc biệt tình thái / trợ / phó từ — cho mềm câu)
        • 1 nhóm từ biểu đạt (láy / thành ngữ / trái nghĩa…)
        • Tone/register thống nhất với voice profile
[4] Viết draft
[5] Chạy editing_checklist (cũ + 6 check VN mới)
```

→ Language Bank là **menu**, không phải **luật**. Pick cái fit, bỏ cái không hợp.

---

## 4. Khi nào KHÔNG dùng

- ❌ Khi chưa có insight thật → quay lại pipeline `bank → select`
- ❌ Khi chưa đọc voice profile brand → đọc trước
- ❌ Khi viết tin nhắn nội bộ / DM → không cần audit câu chữ
- ❌ Khi cố nhồi mọi biện pháp vào 1 bài → bài thành "khoe chữ", mất tự nhiên

---

## 5. Nguyên tắc khi áp dụng

1. **Ít mà tinh** — 1 bài tốt nên có 1-2 biện pháp tu từ rõ + 1-2 từ láy/thành ngữ đắt, không phải 10 cái lẻ tẻ.
2. **Phục vụ ý, không khoe chữ** — biện pháp nào không làm ý rõ hơn → bỏ.
3. **Hợp tone brand** — chị Hiền tone thân mật, không chơi chữ kiểu báo lá cải, không nói quá kiểu sale FOMO.
4. **Test đọc to** — câu nào đọc lên thấy gượng → sửa, dù đúng quy tắc.

---

## 6. Nguồn tham khảo

- [Wiki — Từ loại tiếng Việt](https://vi.wikipedia.org/wiki/T%E1%BB%AB_lo%E1%BA%A1i)
- [Wiki — Danh sách biện pháp tu từ](https://vi.wikipedia.org/wiki/Danh_s%C3%A1ch_bi%E1%BB%87n_ph%C3%A1p_tu_t%E1%BB%AB)
- Tài liệu tiếng Việt nội bộ anh Tuấn cung cấp (nguồn chính, lọc theo mục tiêu ứng dụng content)

---

**Updated**: 2026-05-10 · v1 (initial Language Bank)
