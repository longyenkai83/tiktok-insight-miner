# Operation Manual — Insight Miner trên Railway

> **Phiên bản**: v1 (2026-05-17)
> **Mục đích**: hướng dẫn vận hành Insight Miner sau khi deploy lên Railway. Cho anh + nhân viên + sau này cho người mới onboard.
> **Đối tượng**: anh Tuấn (admin) + nhân viên (user)
> **State sau deploy**:
> - Web URL: `https://insight.lenguyenkhang.com` (Railway-hosted, 24/7)
> - Storage: Railway Volume `/app/output` + Google Drive (backup)
> - Handoff: tự động qua Google Drive → CoWork pull

---

## 1. Architecture tổng quan

```
┌─────────────────────────────────────────────────────────────┐
│  USERS (anh + nhân viên + chị Hiền)                         │
│  ▼ Browser                                                  │
│  https://insight.lenguyenkhang.com                          │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼ Cloudflare DNS (only, no proxy)
┌─────────────────────────────────────────────────────────────┐
│  RAILWAY CLOUD (24/7)                                       │
│  - Service: web (Streamlit container)                       │
│  - Volume: /app/output (persistent storage)                 │
│  - Build: Dockerfile từ GitHub auto-deploy                  │
└────┬───────────────────────────────────────────┬────────────┘
     │ Pipeline run                              │ Snapshot Drive API
     ▼                                           ▼
[Output files]                          [Google Drive]
- raw_comments.json                     tiktok-miner-shared/
- classified.json                        insights-packs/
- report.md, brief.md                     kinh-doanh-27-45/
                                            insights-pack_v1.md
                                            v2.md, v3.md ...
                                                      │
                                                      ▼
                                              [CoWork chị Hiền]
                                              MCP Drive pull
                                              skill `pull-insights-from-miner`
```

---

## 2. Workflow vận hành hàng ngày

### 2.1 Anh / nhân viên — chạy pipeline (5 phút)

1. Mở **https://insight.lenguyenkhang.com**
2. Login với password (anh set khi deploy)
3. Sidebar: nhập **tên/mã NV** (vd `tuan`, `nv_minh`)
4. Niche slug: `kinh-doanh-27-45` (luôn cố định cho audience chị Hiền)
5. Chọn nguồn data:
   - **Tab Scrape TikTok**: paste 3-5 URL TikTok → tool tự lấy comment
   - **Tab Paste comment**: paste comment FB/YT/group (mỗi dòng 1 cái)
6. Bấm **Chạy pipeline** → đợi 2-5 phút
7. Section 3. Kết quả: download files (report, brief, classified) nếu muốn lưu local
8. Section 4. Upload Drive: tick insight muốn dùng → bấm Upload
9. Drive cloud có file `insights-pack_v<N>.md` mới

### 2.2 Chị Hiền — pull insight về CoWork

Sau khi anh báo "có batch mới":
1. Mở session CoWork
2. Nói: *"Pull insights kinh-doanh-27-45"* hoặc *"Lấy insight mới về"*
3. CoWork skill `pull-insights-from-miner` chạy → đọc Drive folder → save vào `WORK AREAS/Marketing/<project>/inputs/`
4. Chị Hiền chọn 1 insight → trigger Content Proposal Protocol → viết bài

---

## 3. Cost monitoring

### 3.1 Railway

- Dashboard: https://railway.com → project → tab **Usage**
- Cost: ~$5-15/tháng tuỳ traffic
- Trial: $5 free credit + 30 ngày → sau đó cần Hobby Plan ($5/tháng)

### 3.2 Apify (TikTok scrape)

- Dashboard: https://console.apify.com → Billing
- Cost: ~$0.001/comment + ~$0.05/scrape session
- ~$5-15/tháng cho ~10-30 runs/tháng

### 3.3 Anthropic Claude

- Dashboard: https://console.anthropic.com → Usage
- Cost: ~$0.0003/comment classify (Haiku) hoặc $0.001/comment (Opus)
- ~$3-10/tháng cho ~500-2000 comments/tháng

### 3.4 Google Drive

- Free 15GB. Insight pack chỉ ~30KB/file → 500+ files = 15MB → đủ dùng nhiều năm.

### Tổng: ~$10-30/tháng (~250-750k VNĐ)

---

## 4. Manage users + quota

### 4.1 Set/update WEBAPP_PASSWORD

Railway → service `web` → tab Variables → tìm `WEBAPP_PASSWORD` → Edit → đổi value → Save.

→ Railway auto-redeploy với password mới (1-2 phút).

→ Anh báo nhân viên password mới.

### 4.2 Quota mỗi user

Default: 20 runs/24h/user.

Đổi: Railway Variables → `MAX_RUNS_PER_USER_PER_DAY` = số mới → Save.

### 4.3 Audit ai chạy gì

File `usage_log.csv` (trong Railway Volume `/app/output/usage_log.csv`):
- timestamp, user, niche, num_urls, num_comments, status, cost_est

Cách xem:
- Tab Variables không có file viewer — phải Railway CLI hoặc download.
- Hoặc xem sidebar "10 runs gần nhất" trên web (chỉ thấy 10 mới nhất).

---

## 5. Update code (khi em fix bug / thêm feature)

### 5.1 Anh push code lên GitHub

```powershell
cd D:\Projects\tiktok-insight-miner
git add .
git commit -m "Mô tả thay đổi"
git push
```

→ Railway tự detect commit mới + rebuild (~3-5 phút).

### 5.2 Verify deploy success

Railway dashboard → tab Deployments → đợi deployment mới status **Active** xanh.

→ Sau đó hard refresh web (Ctrl+Shift+R).

### 5.3 Rollback nếu deploy lỗi

Railway → Deployments → tìm deployment cũ Active → click ⋮ → **Redeploy** (rollback về version cũ).

---

## 6. Troubleshooting

### 6.1 Web không load (502/503)

1. Railway dashboard → service `web` → Deployments → latest deployment status?
2. Nếu Failed → click Build Logs / Deploy Logs xem lỗi
3. Common causes: env var thiếu, Dockerfile sai, port collision

### 6.2 "GitHub Repo not found"

→ Railway lost access. Vào https://github.com/settings/installations → Configure Railway App → đảm bảo `tiktok-insight-miner` trong list.

### 6.3 Section 4 không hiện

- Niche slug không có config → chỉ `kinh-doanh-27-45` work
- Hoặc env vars `INSIGHTS_PACK_DRIVE_FOLDER_ID` / `GDRIVE_SERVICE_ACCOUNT_JSON` thiếu

### 6.4 Upload Drive fail

1. Check service account email đã share Drive folder với role Editor
2. Check `GDRIVE_SERVICE_ACCOUNT_JSON` env var trên Railway có đúng JSON content không
3. Check Railway logs có error gì khi user click Upload

### 6.5 Pipeline timeout (>5 phút)

- Apify quota hết → check Apify dashboard
- Anthropic quota hết → check Anthropic dashboard
- Quá nhiều comments (>500) → giảm `Max comments / video` trong sidebar

### 6.6 Domain `insight.lenguyenkhang.com` không load

1. Cloudflare DNS check CNAME `insight` → DNS only (không proxy)
2. Verify CNAME target = đúng URL Railway (vd `vqqo6m1h.up.railway.app`)
3. Đợi DNS propagate (5-15 phút sau khi đổi)
4. Test với `https://dnschecker.org/#CNAME/insight.lenguyenkhang.com`

### 6.7 Container restart → mất data

Check Volume đã attach chưa:
- Railway dashboard → service `web` → có icon volume `web-volume` không?
- Volume mount path = `/app/output`
- Nếu KHÔNG có → tạo volume + attach (xem [DEPLOY_RAILWAY.md](DEPLOY_RAILWAY.md) section 9.11)

### 6.8 Streamlit click checkbox → section biến mất

→ Bug session_state. Em đã fix ở commit. Anh check commit log có "Fix session state" chưa. Nếu thiếu → pull em fix lại.

---

## 7. Backup strategy

| Asset | Lưu ở đâu | Backup |
|---|---|---|
| Code | GitHub repo (private) | ✅ Git history |
| Niche config | GitHub repo (`niche_configs/`) | ✅ Git history |
| Output files (raw/classified/report/brief) | Railway Volume `/app/output/` | ⚠️ KHÔNG backup auto. Anh tải về local nếu cần |
| Insight pack | Google Drive cloud | ✅ Drive auto |
| Usage log | Railway Volume `/app/output/usage_log.csv` | ⚠️ KHÔNG backup auto |
| Env vars (API keys, password) | Railway dashboard | ⚠️ Anh lưu vào notes riêng (KMS, password manager) |

**Đề xuất**: định kỳ (1 lần/tháng), anh:
1. Download `usage_log.csv` từ Railway về local
2. Export env vars (chỉ tên, không value) làm checklist

---

## 8. Scale lên thêm niche / brand mới

### 8.1 Niche mới (cùng audience kiểu)

1. Anh / em đọc [SOP_CLONE_NICHE.md](SOP_CLONE_NICHE.md)
2. Tạo `niche_configs/<niche-slug>.json` mới
3. Push GitHub → Railway tự deploy
4. Tool sẵn sàng cho niche mới

### 8.2 Brand mới (audience hoàn toàn khác)

- Audience khác → có thể cần Drive folder riêng + mapping freedom_layer riêng
- Em hỗ trợ setup (~1 giờ/brand mới)

---

## 9. Khi nào nâng cấp lên Pro

Railway Hobby ($5/tháng) đủ cho:
- 10-30 users/tháng
- ~50 runs/tháng
- 1GB volume

Cân nhắc Pro ($20/tháng) khi:
- 50+ users active
- Cần multi-region replicas
- Volume >5GB
- Need staging environment

---

## 10. Quick reference — Cheat sheet

| Action | Where / How |
|---|---|
| Login vào web | https://insight.lenguyenkhang.com + password |
| Check Railway logs | Dashboard → service `web` → Deployments → logs |
| Update password | Railway → Variables → WEBAPP_PASSWORD → edit |
| Pull latest code | Anh push GitHub → Railway auto-deploy |
| Rollback | Railway → Deployments → older deployment → Redeploy |
| Check cost | Railway Usage tab + Apify/Anthropic dashboards |
| Drive folder | https://drive.google.com/drive/folders/1S27BXGisZTNZ63EgrINDxhMTVvmrue8W |
| GitHub repo | https://github.com/longyenkai83/tiktok-insight-miner |
| Cloudflare DNS | https://dash.cloudflare.com → lenguyenkhang.com → DNS |

---

## 11. Tài liệu liên quan

- [DEPLOY_RAILWAY.md](DEPLOY_RAILWAY.md) — Playbook deploy lần đầu + lessons learned
- [SOP_CLONE_NICHE.md](SOP_CLONE_NICHE.md) — Clone niche mới
- [HANDOFF_DIAGRAM.md](HANDOFF_DIAGRAM.md) — Sơ đồ flow miner → CoWork
- [SETUP_GDRIVE_WORKFLOW.md](SETUP_GDRIVE_WORKFLOW.md) — Setup Drive (Local + API mode)
- [MAPPING_FREEDOM_LAYER.md](MAPPING_FREEDOM_LAYER.md) — Mapping cho CoWork chị Hiền

---

**Updated**: 2026-05-17 · v1 (đóng gói sau khi deploy thực tế)
**Tinh thần**: Vận hành đơn giản. Anh / nhân viên chỉ cần biết URL + password. Mọi thứ khác đã automation.
