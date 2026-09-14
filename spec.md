# Đặc tả — TikTok Insight Miner

Một trang. Bản duyệt ngày 2026-09-14. Người duyệt: Lê Nguyên Tuấn.

---

## 1. Vấn đề

Người làm nội dung một mình và chủ doanh nghiệp nhỏ bán qua mạng xã hội phải ra
bài mới **mỗi tuần**, nhưng không biết khán giả trong ngách đang hỏi gì, đau gì,
phản đối gì — nên mở từng video, đọc tay hàng trăm comment, rồi viết theo cảm tính.

## 2. Người dùng

**Chính:** Tuấn — người làm nội dung cho chủ doanh nghiệp nhỏ, quản lý ngách
`kinh-doanh-27-45`. Hiện là người dùng duy nhất: 4 lần chạy, 3.999 comment.

**Thứ hai, đã thiết kế sẵn chỗ:** một huấn luyện viên và 3–5 nhân viên nội dung,
dùng chung qua web, mỗi người có mật khẩu và hạn mức 20 lần chạy mỗi 24 giờ.

**Hiện họ đang làm gì thay thế:** lướt TikTok, đọc tay; hoặc dùng vidIQ và tokscript
— hai công cụ này cho số liệu kênh và lời thoại video, không đọc được comment.

## 3. Nó làm gì

- **Tìm** video nhiều comment trong ngách từ một từ khoá, hashtag hoặc kênh — không
  phải lướt tay
- **Quét** toàn bộ comment về qua Apify, hoặc nhận comment dán tay từ CSV
- **Phân loại** từng comment bằng Claude thành 7 nhóm: pain, desire, question,
  objection, praise, mention, other — bắt buộc bám comment thật, cấm suy diễn
- **Đề xuất** 10 ý tưởng nội dung kèm hook và dàn ý, mỗi ý trích thẳng comment gốc
- **Chạy định kỳ** không cần ai bấm: tự lấy từ khoá từ kho, xoay vòng tránh trùng,
  lưu lịch sử từng lần chạy và sao lưu lên Google Drive

## 4. KHÔNG làm trong phiên bản này

1. **Không viết bài hoàn chỉnh.** Chỉ đưa ý tưởng và dàn ý. Người viết vẫn là người.
2. **Không đăng bài.** Đầu ra dừng ở file. Việc đăng thuộc công cụ khác.
3. **Không cào nền tảng ngoài TikTok và Facebook.** Không YouTube, không Threads.
4. **Không có cơ sở dữ liệu.** Lịch sử là file CSV và thư mục — đủ cho dưới 100
   lần chạy mỗi tháng, cố ý chưa làm Postgres.
5. **Không chạy nhiều lần cùng lúc.** Mỗi lần chạy khoá giao diện 4–8 phút. Biết rõ,
   cố ý chưa sửa vì chưa tới 20 người dùng đồng thời.
6. **Không có bảng điều khiển thống kê.** Muốn biết ai chạy gì thì mở file log.

## 5. Dữ liệu

**Đầu vào**
| Thứ | Từ đâu |
|---|---|
| Từ khoá, hashtag hoặc tên kênh | Người dùng gõ trên web, hoặc agent tự lấy từ kho 3.529 từ khoá |
| Đường dẫn video TikTok | Máy tự tìm, hoặc người dùng dán |
| Comment dán tay | File CSV |
| Hồ sơ ngách: nhân vật, chỗ đau, giọng viết | Thư mục `niche_configs/`, dạng JSON và Markdown |

**Đầu ra**
| Thứ | Ở đâu |
|---|---|
| `report.md` — phân bố 7 nhóm, câu trích đáng chú ý | Thư mục lần chạy |
| `brief.md` + `brief.json` — 10 ý tưởng, mỗi ý gắn comment gốc | Thư mục lần chạy |
| `classified.json` — từng comment kèm nhãn | Thư mục lần chạy |
| `usage_log.csv` — ai chạy, ngách nào, bao nhiêu comment, tốn bao nhiêu | Gốc dự án |

**Lưu ở đâu**
Ba tầng: ổ đĩa Railway là tầng chính · Google Drive là bản sao lưu · CSV là nhật
ký. Khoá Apify và Anthropic nằm trong biến môi trường Railway, không có trong mã,
`.env` nằm trong `.gitignore` và không có trong lịch sử commit.

## 6. Xong là gì

**Kết quả kiểm tra được, ba phép thử:**

1. **Người lạ dùng được.** Một người chưa từng thấy công cụ mở
   `insight.lenguyenkhang.com`, nhập mật khẩu, gõ một từ khoá, và trong 15 phút
   nhận được `brief.md` có 10 ý tưởng, mỗi ý có comment gốc kèm theo.
2. **Máy tự chạy.** Đúng lịch, agent định kỳ chạy trọn 5 khâu không ai bấm, và
   sáng hôm sau trong Google Drive có thư mục lần chạy mới.
3. **Không bịa.** Chọn ngẫu nhiên 5 trong 10 ý tưởng, mỗi comment được trích phải
   tìm thấy nguyên văn trong `raw_comments.json`.

**Mốc thời gian:**
| Mốc | Hạn |
|---|---|
| Đẩy bản v0.5.0 lên GitHub, 70 test xanh | 15/09/2026 |
| Video Pre-Demo Day nộp | 15/09/2026, 23:59 |
| Ba người ngoài dùng thật, có phản hồi ghi lại | 17/09/2026 |
| Agent định kỳ chạy thật trên lịch ít nhất một lần | 19/09/2026 |
| Demo Day | 20/09/2026 |

## 7. Dễ hỏng ở đâu

Chín lỗi dưới đây **đã từng xảy ra thật** và được ghi trong tài liệu kiến trúc của
dự án. Ba món nợ cuối là biết trước, cố ý để sau.

| Chỗ hỏng | Đã xảy ra thế nào | Chặn thế nào |
|---|---|---|
| **Apify đổi kiểu trả về giữa hai phiên bản** | `run.get("defaultDatasetId")` hỏng vì bản mới trả object, không trả dict | Hàm đọc chấp nhận cả 3 dạng; ghim phiên bản SDK |
| **Nhật ký CSV lệch mã hoá** | Ghi có BOM, đọc không BOM → mất cột `timestamp` | Ghi và đọc cùng `utf-8-sig` |
| **Điều kiện tên model bị lỗi thời** | Kiểm `opus-4-7` hoặc `opus-4-6` → nâng lên 4-8 là tắt ngầm chế độ suy nghĩ | Kiểm theo tiền tố `opus-4` |
| **File JSON hỏng → ghi đè mất sạch** | Bắt lỗi rồi gán rỗng, ghi đè file cũ | Sao lưu kèm mốc giờ trước khi ghi |
| **Regex đọc brief sai định dạng** | Dấu `:` đặt sai chỗ, bắt nhầm trường CTA | Kiểm regex với nhiều định dạng thật |
| **Chrome tự dịch làm vỡ giao diện** | Chrome Translate sửa DOM, Streamlit không tải được | Thẻ `notranslate` |
| **Chạy mà không truyền ngách** | Không có `--niche` → tự đoán sai → tắt ngầm hồ sơ ngách | Truyền tường minh, tự đoán chỉ là dự phòng |
| **Phân loại thất bại im lặng** | Khoá sai (401) mà log vẫn báo thành công với 0 comment | Dừng ngay khi 401, hoặc 3 mẻ liên tiếp trống |
| **Vượt hạn mức Apify** | 06/09/2026 dùng vượt $29 trả trước, phải nâng lên $40 | Theo dõi qua email cảnh báo; đặt trần theo lần chạy |
| *Nợ 1 — Giao diện khoá khi chạy* | Mỗi lần 4–8 phút, đóng tab là mất tiến trình | Cố ý chưa sửa. Sửa khi có trên 20 người dùng |
| *Nợ 2 — Không có cơ sở dữ liệu* | CSV không tra cứu được theo ngách hay theo người | Cố ý chưa sửa. Chuyển Postgres khi trên 100 lần/tháng |
| *Nợ 3 — Một file 1.900 dòng* | Giao diện, logic, cấu hình chung một chỗ | Cố ý chưa sửa. Tách sau Demo Day |

---

## Ghi chú duyệt

Tôi đã đọc lại và sửa hai chỗ. Mục 4 ban đầu chỉ có 3 dòng — thêm 3 món nợ kỹ
thuật vào vì chúng là quyết định "cố ý chưa làm", đúng nghĩa mục này. Mục 6 ban
đầu chỉ có "người lạ dùng được" — thêm phép thử "không bịa", vì cấm suy diễn là
luật đã khoá trong mã, phải có cách kiểm.
