# 🤖 Agent định kỳ — hướng dẫn dùng

> Quét insight TikTok rồi viết kịch bản, chạy tự động hằng tuần, không cần ai ngồi canh.

## Nó làm gì

Mỗi lần chạy, agent đi hết 5 khâu cho từng job:

| Khâu | Việc | Kết quả |
|---|---|---|
| 0 | Lấy từ khoá | Rút từ kho `keyword-research-dataforseo`, tuần sau tự lấy từ khoá khác |
| 1 | Quét + phân loại | `report.md` (insight thô) + `brief.md` (10 góc nội dung) |
| 2 | Dựng bảng insight | `1-liệt-kê.csv` · `2-sắp-xếp.md` · `3-lựa-chọn.md` |
| 3 | Tự chọn angle | `_master/selected_angles.json` — **không cần ai tick tay** |
| 4 | Viết kịch bản | `4-thực-thi/angle-XX.md` — hook, lời thoại, cảnh quay, caption, CTA |
| 5 | So sánh 2 luồng | `so-sanh-nguon.md` — chỉ khi có cả job TikTok lẫn job fanpage cùng niche |

Trước đây dây chuyền đứt ở khâu 3: phải có người mở `3-lựa-chọn.md` tick `[x]` thì mới đi tiếp được. Giờ cờ `--auto-top` cho máy tự chọn N angle điểm cao nhất.

**Anh vẫn giữ quyền duyệt.** Angle máy chọn mang nhãn `selected_by: "auto"` trong `selected_angles.json`. Muốn đổi: mở `3-lựa-chọn.md`, tick tay rồi chạy lại `tim select` — angle anh tick luôn được giữ, không bao giờ bị máy cắt bớt.

---

## Bước 1 — Điền từ khoá

Mở [agent_config.json](../agent_config.json). Mỗi mục trong `jobs` là một lần quét độc lập.

Có 2 cách cấp từ khoá:

**Cách A — tự điền tay.** Điền thẳng vào `keyword`:

```json
"keyword": ["kinh doanh online", "khởi nghiệp thất bại"]
```

**Cách B — rút từ kho keyword research** (đang bật sẵn). Agent tự lấy từ file CSV của app `keyword-research-dataforseo`, mỗi tuần lấy nhóm khác nhau nên không quét trùng.

Kho hiện có **3.529 từ khoá**. Bộ lọc quyết định còn lại bao nhiêu:

| Bộ lọc | Còn lại | Đủ chạy (3 từ khoá/tuần) |
|---|---:|---:|
| Không lọc gì | 3.529 | 1.176 tuần |
| `min_vol: 300` | 158 | 52 tuần |
| `min_vol: 500`, `max_kd: 60`, informational | 66 | 22 tuần |
| **`min_vol: 1000`, `max_kd: 40`, informational** ← đang dùng | **38** | **12 tuần** |

_(Số đếm bằng lệnh trên file thật ngày 2026-09-11, không phải ước lượng.)_

Muốn quét rộng hơn thì hạ `min_vol` hoặc bỏ `intent`.

Điền xong, đổi `"enabled": false` thành `true`.

## Bước 2 — Chạy thử, không tốn tiền

```
start-weekly-agent.bat --dry-run
```

Nó in ra đúng các câu lệnh sẽ chạy và từ khoá tuần này, **không gọi API, không mất đồng nào**. Xem thấy ổn mới chạy thật.

## Bước 3 — Chạy thật một lần

```
start-weekly-agent.bat
```

Lần đầu nên chạy tay để xem có lỗi khoá API hay không, và để biết thực tế tốn bao nhiêu tiền.

Kết quả để lại trong `output/_agent-logs/`:

- `<ngày>-tom-tat.md` — bản tóm tắt ngắn, đọc cái này trước
- `<ngày>__<job>.log` — log thô đầy đủ, chỉ mở khi có hỏng
- `keyword-state.json` — nhớ đã quét từ khoá nào

## Bước 4 — Đặt lịch hằng tuần

Mở PowerShell **quyền Administrator**, dán lệnh này (chạy 8h05 sáng thứ Hai):

```powershell
schtasks /create /tn "TikTok Insight Agent" /tr "D:\Tuan-CoWork\TUAN-insight-miner\start-weekly-agent.bat --task" /sc weekly /d MON /st 08:05 /f
```

Cờ `--task` bảo nó chạy xong tự đóng, không đứng chờ bấm phím.

Kiểm tra / chạy thử / xoá lịch:

```powershell
schtasks /query /tn "TikTok Insight Agent"     # xem lịch
schtasks /run   /tn "TikTok Insight Agent"     # chạy ngay, không đợi thứ Hai
schtasks /delete /tn "TikTok Insight Agent" /f # xoá lịch
```

**Máy phải bật lúc đó.** Máy ngủ thì lỡ tuần ấy — Task Scheduler có tuỳ chọn chạy bù, bật trong giao diện Task Scheduler nếu cần.

---

## Luồng 2 — Comment từ fanpage của anh

Ngoài TikTok (thị trường rộng), agent lấy được cả comment + tin nhắn inbox từ **fanpage của chính anh** (khách đã biết anh). Hai luồng chạy riêng, ra 2 báo cáo riêng, rồi agent tự sinh **bảng so sánh** — thị trường nói gì, khách anh nói gì, lệch nhau ở đâu.

```
TikTok  ─► output/<niche>/<ngày>__agent-tiktok/    report.md · brief.md
Fanpage ─► output/<niche>/<ngày>__agent-fb/        report.md · brief.md
                        └──► output/<niche>/<ngày>__agent-so-sanh/so-sanh-nguon.md
```

**Vì sao không trộn chung một bể**: TikTok một lần ra ~1.000 comment, fanpage một tuần vài chục. Trộn vào thì tiếng khách anh chiếm ~5%, chìm nghỉm.

### Lấy token Facebook

1. Vào [developers.facebook.com](https://developers.facebook.com) → tạo app (loại Business) nếu chưa có.
2. Mở **Tools → Graph API Explorer**.
3. Chọn app → ô **User or Page** chọn fanpage của anh.
4. Thêm quyền: `pages_read_engagement` (bắt buộc). Muốn đọc inbox thêm `pages_messaging` + `pages_manage_metadata`.
5. Bấm **Generate Access Token** → copy.
6. Điền vào `.env`:

```
FB_PAGE_TOKEN=EAAxxxx...
FB_PAGE_ID=1234567890
```

Page ID xem ở phần **About** của fanpage, hoặc Graph API Explorer gõ `me?fields=id` với token vừa tạo.

**Token ngắn hạn hết sau ~1 giờ.** Đổi sang dài hạn (60 ngày) bằng **Tools → Access Token Debugger → Extend**, hoặc lấy Page token vĩnh viễn qua `me/accounts` với user token dài hạn. Hết hạn thì agent báo lỗi 190 kèm hướng dẫn, không chạy sai.

### Kiểm chứng trước khi tin

```
tim fb-fetch --probe
tim fb-fetch --probe --with-inbox
```

Nó gọi thật 1 bài + 1 comment (+ 1 hội thoại) và in response thô để anh đối chiếu tên field — đúng nguyên tắc "không bịa field" của dự án. Tên người và số điện thoại trong probe đã được che.

### Bật job fanpage

Trong `agent_config.json`, job `fanpage-cua-anh` đang `"enabled": false`. Điền token vào `.env` xong thì đổi thành `true`. Để cùng `niche` với job TikTok thì agent tự sinh bảng so sánh.

Muốn lấy cả inbox: `"with_inbox": true`.

### Riêng tư — luật cứng đã cài trong code

| Luật | Cách làm |
|---|---|
| Không lưu tên thật | `author` = `fb-` + 8 ký tự băm từ id. Cùng người → cùng mã, nhưng không lần ngược được |
| Che số điện thoại / email / link | Regex che **trước khi ghi ra đĩa và trước khi gửi lên Claude** → `[sđt]`, `[email]`, `[link]` |
| Bỏ tin của chính mình | Comment/tin nhắn do Page gửi bị loại — đó là câu trả lời của anh, không phải tiếng khách |
| Inbox không lưu thô | `raw` chỉ giữ `conversation_id`, không giữ response gốc |

Có 20 test tự động bảo vệ các luật này ([tests/unit/test_fb_page_source.py](../tests/unit/test_fb_page_source.py)), trong đó một test kiểm tra "không rò tên, email, số điện thoại, user id ở bất kỳ đâu trong JSON".

Nhân viên mở webapp cũng chỉ thấy bản đã che.

---

## Bước 5 — Lớp agent Claude đọc kết quả (tuỳ chọn)

Phần trên là dây chuyền máy: chạy đúng kịch bản, không suy nghĩ. Muốn có agent **đọc kết quả rồi báo cáo cho anh** thì thêm một routine trong Claude Code Desktop.

Trong Claude Desktop → tab **Code** → **Routines** → **New routine** → chọn **Local**:

- **Folder**: `D:\Tuan-CoWork\TUAN-insight-miner`
- **Schedule**: Weekly, thứ Hai, 09:00 (sau agent máy 1 tiếng)
- **Instructions**: dán đoạn dưới

```
Đọc file tóm tắt mới nhất trong output/_agent-logs/ (tên dạng <ngày>-tom-tat.md).

Nếu có job hỏng: mở file log tương ứng, tìm nguyên nhân thật, nói rõ hỏng ở
khâu nào và cách sửa. Đừng đoán — trích đúng dòng lỗi trong log.

Nếu mọi job chạy trọn:
1. Đọc report.md của lần chạy này.
2. So với lần chạy tuần trước (thư mục output/<niche>/ có sẵn các lần trước).
3. Trả lời đúng 3 câu hỏi, mỗi câu 2-3 dòng:
   - Tuần này audience nói gì mà tuần trước không nói?
   - Nhóm insight nào đang tăng, nhóm nào đang nguội?
   - Trong các angle máy tự chọn, cái nào đáng quay nhất và vì sao?
4. Nếu có file so-sanh-nguon.md: đọc bảng "Theo nguồn", chỉ ra 1-2 chỗ
   thị trường (TikTok) và khách của anh (FB) lệch nhau rõ nhất.
5. Liệt kê file kịch bản mới sinh ra trong 4-thực-thi/.

Viết bằng tiếng Việt, xưng "em", gọi Tuấn là "anh". Ngắn gọn, không sáo rỗng.
KHÔNG bịa số. Số nào cũng phải đếm được từ file thật.
```

Routine chỉ chạy khi app Claude Desktop đang mở và máy thức.

---

## Khi có trục trặc

| Hiện tượng | Nguyên nhân thường gặp |
|---|---|
| `Không có job nào đang bật` | Chưa đổi `"enabled": true` trong agent_config.json |
| `chưa có keyword/profile/hashtag/keyword_source` | Job chưa có nguồn từ khoá nào |
| `không thấy niche_configs/<tên>.json` | Tên `niche` trong job sai, phải khớp tên file trong `niche_configs/` |
| Hỏng ở khâu 1 | Thường là hết hạn mức Apify hoặc sai `APIFY_TOKEN` trong `.env` |
| Hỏng ở khâu 4 | Thường là sai `ANTHROPIC_API_KEY` — xem log để chắc |
| Chạy mãi ra cùng từ khoá | `rotate` đang để `false`, hoặc `keyword` điền tay đè lên kho |

Log thô luôn nằm ở `output/_agent-logs/<ngày>__<job>.log`.

---

## Chi phí — nói thẳng

Một lần chạy quét 985 comment tốn **$1.37** (số thật từ [LATEST.md](../LATEST.md), lần chạy 2026-07-21). Khâu 4 viết kịch bản dùng Opus nên đội thêm, phụ thuộc `auto_top` đặt mấy angle.

Chạy hằng tuần thì nhân 4 mỗi tháng. Muốn rẻ hơn:

- Hạ `max_comments` (200 → 100)
- Hạ `auto_top` (5 → 3)
- Đặt `ANTHROPIC_MODEL=claude-haiku-4-5` trong `.env` cho khâu phân loại
- Tắt `run_production` nếu tuần đó chỉ cần insight, chưa cần kịch bản

Lần chạy thật đầu tiên sẽ cho con số chính xác — chạy tay một lần rồi xem `usage_log.csv`.
