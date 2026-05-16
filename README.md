# TikTok Insight Miner

CLI Python quét comment TikTok → phân loại bằng Claude → xuất **báo cáo insight + content angle brief**.

Phân loại comment thành 7 bucket: **pain** / **desire** / **question** / **objection** / **praise** / **mention** / **other**. Dùng cho research thị trường, content angle discovery, viral hook mining.

**v0.2** thêm **content angle suggester** (`suggest` command): Claude Opus 4.7 generate 10 video idea hoàn chỉnh (hook + script outline + CTA) ground vào top insight thực, biến tool từ "research" thành "content brief actionable".

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

## Usage

### All-in-one

```bash
# Scrape + classify + report
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
