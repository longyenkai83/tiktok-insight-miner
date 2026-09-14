# TikTok Insight Miner

> Nghe khán giả nói gì trong comment, rồi biết tuần này nên viết bài gì.

**Đang chạy tại:** https://insight.lenguyenkhang.com · **Bản hiện tại:** v0.5.0 (2026-09-11) · 90 test tự động

## Vấn đề

Người làm nội dung một mình và chủ doanh nghiệp nhỏ bán qua mạng xã hội phải ra bài mới mỗi tuần, nhưng không biết khán giả trong ngách đang hỏi gì, đau gì, phản đối gì. Cách phổ biến: mở từng video, đọc tay hàng trăm comment, rồi viết theo cảm tính — mất nửa ngày, kết quả tuỳ hôm.

## Nó làm gì

Nhập một từ khoá → máy tự tìm video nhiều comment trong ngách → quét comment về → Claude phân loại từng comment thành 7 nhóm (**pain / desire / question / objection / praise / mention / other**) → viết **10 ý tưởng nội dung** kèm hook và dàn ý, mỗi ý gắn thẳng vào comment gốc.

Luật khoá trong mã: **không bịa**. Ý tưởng nào không trích được comment nguyên văn thì bị loại.

Một lần chạy thật: 31 video, 2.898 comment, vài phút, khoảng 1 USD.

## Dành cho ai

- Người làm nội dung cho chủ doanh nghiệp nhỏ — đang là người dùng chính
- Đội nội dung 3–5 người dùng chung qua web, mỗi người có mật khẩu và hạn mức riêng

## Ba cách dùng

| Cách | Dành cho | Bắt đầu ở đâu |
|---|---|---|
| **Web** — gõ từ khoá, bấm chạy | Người không cần cài gì | https://insight.lenguyenkhang.com (cần mật khẩu) |
| **Dòng lệnh** — `tim run ...` | Người quen terminal, muốn chạy hàng loạt | Mục "Dùng bằng dòng lệnh" bên dưới |
| **Agent định kỳ** — không ai bấm | Chạy mỗi tuần, tự rút từ khoá, tự lưu | [docs/AGENT_DINH_KY.md](docs/AGENT_DINH_KY.md) |

## Kiến trúc

- **Sơ đồ mở bằng trình duyệt:** [kien-truc.html](kien-truc.html) — hai cửa vào, 6 tầng, các cổng chặn, và 9 lỗi đã từng xảy ra thật
- **Đặc tả một trang:** [spec.md](spec.md) — 7 mục: vấn đề, người dùng, làm gì, không làm gì, dữ liệu, xong là gì, dễ hỏng ở đâu
- **Tài liệu kỹ thuật đầy đủ:** [docs/ARCHITECTURE_FOR_OPTIMIZATION.md](docs/ARCHITECTURE_FOR_OPTIMIZATION.md) — cho kỹ sư nhận bàn giao

```
Từ khoá ──► Discover (Apify) ──► Scrape (Apify) ──► Classify (Claude Haiku)
                                                         │
                                          ┌──────────────┴──────────────┐
                                          ▼                             ▼
                                   Report (report.md)          Brief (Claude Opus)
                                                               10 ý tưởng + comment gốc
                                          │                             │
                                          └──────────────┬──────────────┘
                                                         ▼
                                    Lưu: ổ đĩa Railway → Google Drive → usage_log.csv
```

**Hạ tầng:** Streamlit trên Railway, không có cơ sở dữ liệu (cố ý — CSV đủ cho dưới 100 lần/tháng). Khoá Apify và Anthropic nằm trong biến môi trường Railway, `.env` không có trong git.

## Trong mã nguồn có gì

| Đường dẫn | Là gì |
|---|---|
| `webapp.py` | Giao diện web Streamlit — cổng mật khẩu, hạn mức, chạy pipeline, xem lịch sử |
| `tiktok_insight_miner/` | Lõi: `scraper.py` · `classifier.py` · `reporter.py` · `suggester.py` · `selection.py` · `cli.py` |
| `weekly_agent.py` + `agent_config.json` | Agent định kỳ, chạy liền 5 khâu cho nhiều job |
| `niche_configs/` | Hồ sơ từng ngách: nhân vật, chỗ đau, giọng viết |
| `output/` | Kết quả từng lần chạy — gitignore |
| `tests/` | 90 test, chạy `python -m pytest tests/` |
| `docs/` | Kiến trúc, vận hành, bàn giao, SOP |

## Lịch sử bản

Xem mục **Changelog** trong [CLAUDE.md](CLAUDE.md). Mốc chính: v0.3 web nội bộ · v0.4 tự tìm video · **v0.5 agent định kỳ**.

---
## Cài đặt

```bash
# Yêu cầu Python 3.11+
cd tiktok-insight-miner
pip install -e .
```

Tạo file `.env` từ template:

```bash
cp .env.example .env
# Sửa APIFY_TOKEN và ANTHROPIC_API_KEY
```

Cần:
- **Apify token**: https://console.apify.com/account/integrations
- **Anthropic API key**: https://console.anthropic.com/settings/keys

## Dùng bằng dòng lệnh (CLI)

### Discover — tự tìm video (bỏ khâu tìm tay)

Không cần tự lên TikTok lướt tìm bài. Nhập từ khóa hoặc kênh đối thủ → tự lấy list video đáng mine (đã lọc bỏ bài ít comment, sort theo view):

```bash
# Theo từ khóa (chỉ giữ video ≥5 comment, view ≥30k)
tim discover --keyword "kinh doanh 2026" --min-comments 5 --min-views 30000 -o urls.txt

# Quét kênh đối thủ
tim discover --profile cafef_official --profile thuethucchien -o urls.txt

# Nhiều từ khóa + hashtag + chỉ bài mới 30 ngày
tim discover --keyword "khởi nghiệp" --hashtag khoinghiep --newest-days 30 -o urls.txt
```

Rồi `tim run --urls-file urls.txt ...`. Hoặc gộp 1 phát bằng `--discover` (xem dưới).

### All-in-one

```bash
# Discover → scrape → classify → report → brief (một lệnh)
tim run --keyword "kinh doanh 2026" --min-comments 10 --with-angles --niche kinh-doanh -o output/kinh-doanh/

# Scrape + classify + report (từ URL có sẵn)
tim run --urls "https://www.tiktok.com/@username/video/1234567890" --max-comments 200

# All 4 stages (kèm content angle brief từ Opus 4.7)
tim run --urls-file urls.txt --max-comments 200 --with-angles -o ./output/run-X

# Multiple videos
tim run --urls-file urls.txt --max-comments 200 -o ./output/run-2026-05-03
```

### Từng stage

```bash
# 1. Scrape
tim scrape --urls-file urls.txt --max-comments 200 -o output/raw.json

# 2. Classify
tim classify -i output/raw.json -o output/classified.json

# 3. Report (insight summary)
tim report -i output/classified.json -o output/report.md

# 4. Suggest (content angle brief — chỉ chạy được sau classify)
tim suggest -i output/classified.json -o output/brief.md --num 10
```

### Options

```
tim run [OPTIONS]
  --keyword TEXT           Từ khóa search (lặp được) → auto-discover video
  --profile TEXT           Kênh đối thủ @username (lặp được) → auto-discover
  --hashtag TEXT           Hashtag (lặp được) → auto-discover
  --min-views INT          Bỏ video dưới ngưỡng view (default 0)
  --min-comments INT       Bỏ video dưới ngưỡng comment (default 1)
  --newest-days INT        Chỉ giữ video trong N ngày gần đây
  --urls TEXT              TikTok video URL (có thể lặp nhiều lần)
  --urls-file PATH         File chứa URLs, mỗi dòng 1 URL
  --max-comments INT       Số comment tối đa mỗi video (default 100)
  --output-dir PATH        Folder output (default ./output)
  --model TEXT             Override ANTHROPIC_MODEL từ .env
  --batch-size INT         Comments per API call (default 20)
  --top-n INT              Top quotes hiển thị mỗi bucket trong report (default 10)
```

## Output structure

```
output/
├── raw_comments.json        # raw data từ Apify
├── classified.json          # comments + bucket + summary + confidence
└── report.md                # báo cáo markdown
```

## Sample report

```markdown
# TikTok Comment Insights

**Videos analyzed**: 3
**Total comments**: 547
**Generated**: 2026-05-03 14:23

## 📊 Distribution

| Bucket | Count | % |
|---|---:|---:|
| praise | 234 | 42.8% |
| question | 142 | 26.0% |
| desire | 78 | 14.3% |
| pain | 52 | 9.5% |
| objection | 23 | 4.2% |
| other | 18 | 3.3% |

## 😣 Pain (52)

**Top quotes:**

1. "shop ơi hàng giao chậm quá em đợi 2 tuần rồi" — @user123 (45 likes)
   *Insight: Frustration về thời gian giao hàng dài*

...
```

## Cost estimate

Với `claude-opus-4-7` (mặc định), batch size 20:
- ~500 comments → ~25 API calls → ~$0.30-0.50

Đổi sang `claude-haiku-4-5` (set `ANTHROPIC_MODEL` trong `.env`):
- ~500 comments → ~$0.05-0.10

Apify cost: ~$0.30-1.00 cho 1000 comments tùy plan.

## Troubleshooting

- **Apify timeout**: Tăng `--max-comments` từ từ. Một số video viral có 100K+ comment, scrape lâu.
- **Cache không hit**: Log `cache_read_input_tokens=0` ở batch 2+ → có thể system prompt chứa timestamp/UUID. Check `classifier.py`.
- **Vietnamese encoding**: Output file UTF-8 mặc định. Nếu mở Excel bị mojibake, dùng "Import Data" với encoding UTF-8.
