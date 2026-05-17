# Insight Mining Framework — TikTok Comment → Content Angle

> **Phiên bản**: v1.0 (2026-05-17)
> **Tác giả**: Tuấn + Claude
> **Mục đích**: framework chuẩn hóa cách biến comment audience TikTok/FB/YT thành content angle có chiều sâu psychology + cultural fit Vietnamese.
> **Áp dụng**: làm reference cho suggester.py, manual review brief, và onboarding niche mới.

---

## 0. Triết lý

- **EM (Em-cluster framework) là Operating System**: backbone phân tích, build từ data thật, có VN cultural fit.
- **SKILL (mental models Cialdini/Kahneman/Fogg) là Library**: 12 model curated, dùng làm checklist phòng blind spot.
- **Không phải cái nào thay thế cái nào** — combine để vừa systematic vừa contextual.

**Anti-pattern**:
- ❌ Nhồi 70 model SKILL.md vào prompt → analysis paralysis + token waste
- ❌ Em pick model theo trực giác mà không có checklist → miss insight quan trọng
- ❌ Bỏ qua cultural concept VN → brief sẽ generic như Western copywriter

---

## 1. Five Audience Persona Clusters (Backbone — em-framework)

Đây là 5 cluster tâm lý em phát hiện qua phân tích 401 cmt niche "xây kênh TikTok". **Có thể khái quát cho mọi niche** nếu re-map keyword.

| # | Cluster | Trạng thái tâm lý | Comment đại diện | Tone-of-voice phù hợp |
|---|---|---|---|---|
| 1 | **Entrepreneurial Despair** | Làm chủ kiệt sức, muốn bỏ cuộc | "làm chủ lao đao", "kinh doanh nhà nghỉ ế", "đống bùn lầy" | Empathy first, KHÔNG tip ngay. Validate cảm xúc trước, đưa lối thoát sau |
| 2 | **Procrastination Trap** | Đợi đủ điều kiện hoàn hảo mới dám làm | "đợi giỏi hơn", "5 năm dậm chân", "chần chừ" | Confrontational nhẹ: "Bạn không đợi đủ — bạn đang sợ". Đập niềm tin "perfect-then-start" |
| 3 | **Viral-No-Convert** | Có view không có đơn → khủng hoảng niềm tin | "4-5 video lên xu hướng nhưng k chuyển đổi", "chạy ads xong flop" | Technical + tactical. Audience ĐÃ biết content, thiếu conversion. Dùng số liệu, framework, A/B |
| 4 | **Authentic Trend Fatigue** | Biết "phải authentic" nhưng không biết kể chuyện gì | "biết là trend rồi nhưng không biết kể chuyện bản thân" | Post-authentic: dạy CÁCH AUTHENTIC không nhạt. KHÔNG lặp lại "hãy chân thực" |
| 5 | **Macro Despair** | Bất lực xã hội/kinh tế ("nghèo cả nước") | "Người nghèo còn nước mắt đâu mà khóc", "chế độ", "nhà nước phạt" | Emotional positioning, KHÔNG bridge sang tip. Đứng cùng nỗi đau, không "fix" nó |

**Quy tắc dùng**:
- Mỗi brief 10 angle → phân bổ 1-2 angle / cluster (không lệch về 1 cluster duy nhất).
- Nếu data thiếu cluster nào → ghi nhận `_missing_cluster: [name]` để biết tuần sau scrape thêm.
- Cluster mới phát hiện ngoài 5 này → add vào file `niche_configs/<slug>_personas.md` riêng.

---

## 2. Twelve Mental Models Curated (Library — from SKILL.md)

Đã loại 58/70 models không relevant cho task comment → angle (pricing, decoy, AIDA funnel, growth hacking...).

| # | Model | Khi dùng (trigger trong data) | Cách apply vào angle |
|---|---|---|---|
| 1 | **Jobs To Be Done** | Comment cho biết audience hire video để làm gì | Mỗi angle xác định "job" cụ thể: học, validate, copy success, vent emotion |
| 2 | **Pratfall Effect** | Có objection "lý thuyết quá", "ai cũng biết rồi" | Creator admit yếu → tăng trust. "Tôi từng sai khi nghĩ X" |
| 3 | **Mimetic Desire** | "Xin vía", "trộm vía", "mong khám kênh", "ai có cách như chị" | Show người-giống-họ đã thành công. KHÔNG show celebrity |
| 4 | **Curse of Knowledge** | Audience nói "biết rồi nhưng không biết áp dụng", "hiểu nhưng không làm" | Break-down siêu cụ thể, ví dụ + template. KHÔNG dùng thuật ngữ chuyên môn |
| 5 | **Zeigarnik Effect** | "Không biết bắt đầu từ đâu", "dậm chân tại chỗ" = open loop | Hook mở loop: "Cái khó nhất không phải X mà là Y..." |
| 6 | **Peak-End Rule** | Top quote likes cực cao (>100) | Quote phải là PEAK của video, lặp lại ở END. KHÔNG bridge sang tip ngay |
| 7 | **Loss Aversion** | "Đợi 5 năm chưa làm" = sợ mất gì? (thường: thể diện) | Frame "cái mất khi không bắt đầu" mạnh hơn "cái được khi làm" |
| 8 | **Mere Exposure (Pattern Frequency)** | Cụm từ lặp ≥3 lần trong comments | Đây là format gợi ý: làm series, không 1 video lẻ |
| 9 | **Social Proof / Bandwagon** | Praise cao likes (≥30), "Bài học: ..." UGC | Repost UGC trong video. "Đây là 5 bài học audience tôi tự rút ra" |
| 10 | **Confirmation Bias** | Audience đã tin trend X | Build trên niềm tin sẵn có, KHÔNG argue ngược. "Chân thực là trend đúng — và đây là 3 cách làm nó không nhạt" |
| 11 | **BJ Fogg (B = MAP)** | "Nghe hiểu mà k làm được" | Audience không thiếu Motivation, thiếu Ability + Prompt. Đưa template, checklist, action trigger |
| 12 | **Goal-Gradient Effect** | "3 tuần lên xu hướng nhưng k ra đơn", "gần đích" | "Bạn chỉ thiếu 1 bước cuối: ..." — đẩy ngưỡng activation |

**Quy tắc dùng**:
- Mỗi angle PHẢI map vào ≥1 model. Tốt nhất 1 model chính + 1 model phụ.
- Nếu angle không map được model nào → red flag, có thể là angle generic không có psychology backing.

---

## 3. Four Vietnamese Cultural Concepts (THIẾU 100% trong SKILL.md)

Đây là 4 concept Western marketing science KHÔNG có. **Tử huyệt nếu bỏ qua với audience VN**.

| # | Concept | Comment match | Marketing application |
|---|---|---|---|
| 1 | **Vía Culture / Magical Thinking** | "xin vía", "trộm vía", "vía lên xu hướng", "cho em xin chút may mắn" | 2 hướng angle: (a) Validate + reframe — "Tôi không tin vía, tôi tin 3 thứ này"; (b) Lean in — "Đây là vía thật: nó tên là chuẩn bị" |
| 2 | **Face / Thể diện** | "tự ti", "xấu hổ", "ngại lộ mặt", "sợ người quen thấy" | Face-saving framing: "Tôi cũng từng ngại — đây là cách quay không lộ mặt mà vẫn viral" |
| 3 | **Collectivism / Tag Culture** | "@username cùng xem", "tag bạn vào", "ai cũng như mình không" | Format reply-video, tag-friend CTA. KHÔNG dùng CTA cá nhân "Comment if you...". Dùng "Tag bạn nào cũng đang...". |
| 4 | **Hierarchy "Anh-Chị-Em-Cô-Chú"** | "Tôi có thể học được không ạ" (cô chú lớn tuổi xưng "tôi"), "anh ơi", "chị ơi", "em mới bắt đầu" | Mỗi angle xác định audience-age-segment dùng đại từ phù hợp. Cô chú 50+ ≠ em gái 20+ ≠ chị 35+ |

**Quy tắc dùng**:
- Mỗi brief PHẢI có ≥1 angle sử dụng ≥1 VN concept.
- Đại từ trong hook + CTA PHẢI match age segment chính trong data (đo qua comment patterns).

---

## 4. Pipeline 3-Stage Architecture

```
INPUT: classified.json (comment đã phân bucket)
    │
    ▼
┌─────────────────────────────────────────────────┐
│ STAGE 1 — Niche Persona Mapping                 │
│ Em-framework: 5 cluster + tension detection     │
│                                                  │
│ Logic:                                           │
│ 1. Đọc top 30 insight (mọi bucket, sort likes)  │
│ 2. Map mỗi insight vào 1/5 cluster              │
│ 3. Phát hiện tension (cluster mâu thuẫn nhau)   │
│ 4. Đếm vocab frequency → lexicon mining         │
│                                                  │
│ Output: {clusters: [...], tensions: [...],      │
│          lexicon: [...]}                         │
└─────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────┐
│ STAGE 2 — Mental Model Mapping                  │
│ Library: 12 SKILL models + 4 VN concepts        │
│                                                  │
│ Logic:                                           │
│ 1. Mỗi cluster → match 1-2 model phù hợp        │
│ 2. Mỗi tension → match 1 model (Pratfall hay    │
│    Confirmation Bias)                            │
│ 3. Check ≥1 VN cultural concept được dùng       │
│                                                  │
│ Output: angle_blueprints[10]                    │
│   = [{cluster, primary_model, secondary_model,  │
│       vn_concept, target_insight}, ...]         │
└─────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────┐
│ STAGE 3 — Angle Generation                      │
│ Constraint-driven generation                    │
│                                                  │
│ Constraints PER ANGLE:                          │
│ - Hook chứa ≥1 cụm nguyên văn từ lexicon       │
│ - CTA dùng đại từ phù hợp age segment           │
│ - Type angle match cluster (vd Despair →        │
│   empathy, không phải tip)                      │
│ - Demand: target_likes ≥10 hoặc frequency ≥3   │
│                                                  │
│ Output: brief.md (10 angle có psychology depth) │
└─────────────────────────────────────────────────┘
```

---

## 5. Lexicon Mining Rules

Tự build "từ điển ngôn ngữ audience" cho mỗi niche. Đây là **vocab grounding** — khắc phục lỗi brief generic.

### 5.1 Tự động extract

Từ top 30 insight (pain + desire + question + objection + praise_high_likes):

- **Emotional words** (cảm xúc): "hoang mang", "nản", "bế tắc", "lao đao", "tự ti", "ngại", "bùn lầy", "dậm chân"
- **Action words** (hành động audience đang làm): "đợi", "thử", "chạy ads", "lên xu hướng", "tag bạn", "xin vía"
- **Identity markers** (cách audience tự gọi mình): "em", "tôi", "mình", "tui", "chị" + nghề ("kinh doanh nhà nghỉ", "spa", "shop nhỏ")
- **Pain phrases** (cụm than thở nguyên văn): "không biết bắt đầu từ đâu", "5 năm vẫn dậm chân", "làm hoài mà không lên"
- **Praise phrases** (cụm khen audience tự dùng): "tâm đắc nhất", "key point", "bài học mình rút ra"

### 5.2 Quy tắc dùng trong generation

- Hook PHẢI chứa **≥1 cụm nguyên văn** từ lexicon (không paraphrase).
- Script outline NÊN dùng **≥2 emotional words** từ lexicon.
- CTA NÊN dùng **đại từ + identity marker** từ lexicon.

**Ví dụ sai vs đúng**:

| Sai (paraphrase) | Đúng (lexicon-grounded) |
|---|---|
| "Bạn đổ tiền chạy ads mà view vẫn lẹt đẹt?" | "Bạn chạy ads xong nội dung vẫn **flop**?" |
| "Đời mình nhạt thì kể gì?" | "Em **biết là trend rồi nhưng không biết kể câu chuyện bản thân thế nào**" |
| "Tôi từng hoang mang giống bạn" | "Em cũng từng **dậm chân 5 năm vì đợi mình giỏi hơn**" |

---

## 6. Anti-Patterns — KHÔNG làm trong brief

Tool có thể tự generate, nhưng cần loại bỏ ở stage post-processing hoặc thêm rule prompt:

| # | Anti-pattern | Tại sao tệ | Cách detect |
|---|---|---|---|
| 1 | **CTA commercial / offer / promo** | Tool là insight content, không phải sales | Hook chứa "miễn phí", "ưu đãi", "tư vấn 1-1", "slot", "deadline 48h" |
| 2 | **Hook generic copywriter** | Không dùng lexicon → ROI insight = 0 | Hook không chứa cụm nào từ lexicon |
| 3 | **Pain → tip bridge ngay** (cluster 1 & 5) | Despair/Macro Despair cần empathy first | Script outline beat 2 là "Giải pháp..." khi cluster là Despair |
| 4 | **Tip cũ audience đã biết** | "Hãy chân thực, gần gũi" → cluster Authentic Trend Fatigue đã biết | Angle target cluster 4 nhưng vẫn dạy "chân thực" |
| 5 | **Angle ground vào comment 0 likes + 1 voice** | Không phải pattern, là cá thể | target_likes < 5 AND theme không lặp |
| 6 | **Đại từ sai segment** | "Bạn" với cô chú 60+ = mất face | Hook dùng "bạn" nhưng comment gốc là "tôi" / "cô" |
| 7 | **Confidence đảo ngược** | Tip kỹ thuật 0.95, insight tâm lý macro 0.88 | Re-rank: insight likes cao + cluster Macro/Despair → confidence ≥0.9 |

---

## 7. Template Prompt cho suggester.py

```text
[SYSTEM]
Bạn là chuyên gia tâm lý học hành vi marketing cho audience Việt Nam.

Quy trình 3-stage:

STAGE 1 — PERSONA MAPPING (silent reasoning):
Đọc top 30 insight. Map mỗi insight vào 1/5 cluster:
1. Entrepreneurial Despair — làm chủ kiệt sức
2. Procrastination Trap — đợi đủ điều kiện
3. Viral-No-Convert — view không ra đơn
4. Authentic Trend Fatigue — biết trend nhưng không biết kể
5. Macro Despair — bất lực xã hội/kinh tế

Phát hiện tension (cluster nào mâu thuẫn): vd "khen bài học" + "chê lý thuyết quá".

STAGE 2 — MENTAL MODEL MAPPING (silent):
Mỗi cluster → match 1-2 model trong 12 curated models:
[Jobs To Be Done, Pratfall, Mimetic Desire, Curse of Knowledge,
 Zeigarnik, Peak-End, Loss Aversion, Mere Exposure,
 Social Proof, Confirmation Bias, BJ Fogg, Goal-Gradient]

Mỗi brief PHẢI có ≥1 angle dùng VN cultural concept:
[Vía Culture, Face, Collectivism/Tag, Hierarchy đại từ]

STAGE 3 — ANGLE GENERATION (output):
Generate ĐÚNG {N} angle. MỖI ANGLE PHẢI có:
- target_insight: quote NGUYÊN VĂN từ 1 comment
- target_likes: likes của comment đó
- cluster: 1/5 cluster (string)
- primary_model: 1 model chính (string)
- vn_concept: optional (string hoặc null)
- hook: PHẢI chứa ≥1 cụm nguyên văn từ comment gốc
- script_outline: 3-5 beat
- cta: dùng đại từ phù hợp age segment

QUY TẮC CỨNG:
1. KHÔNG generate angle dạng commercial/offer/promo
2. KHÔNG paraphrase hook — phải dùng vocab gốc
3. Cluster Despair/Macro → empathy-first, KHÔNG tip bridge ngay
4. Cluster Authentic Trend Fatigue → KHÔNG lặp lại "hãy chân thực"
5. target_likes < 5 AND theme không lặp → SKIP angle này
6. Confidence reweight: cluster Macro + likes ≥50 → confidence ≥0.9

[USER]
Đây là {N} top insight đã sort theo likes:
{insights_block}

Top vocab từ lexicon (PHẢI dùng nguyên văn ≥1/angle):
{lexicon_block}

Generate {N} angle theo schema.
```

---

## 8. Quick Reference Table

| Situation | Cluster | Mental Model | VN Concept |
|---|---|---|---|
| "Người nghèo còn nước mắt đâu mà khóc" (293 likes) | 5. Macro Despair | Peak-End + Loss Aversion | (không cần — emotion đủ mạnh) |
| "5 năm dậm chân vì đợi giỏi hơn" | 2. Procrastination | Zeigarnik + Loss Aversion (sợ mất face) | Face / Thể diện |
| "Lên xu hướng nhưng k ra đơn" | 3. Viral-No-Convert | Goal-Gradient + BJ Fogg | — |
| "Bài học: chân thực" (UGC, 209 likes) | (cross-cluster — meta) | Social Proof + Mere Exposure | Collectivism |
| "Xin vía lên xu hướng" | (cross-cluster — magical) | Mimetic Desire + Confirmation Bias | Vía Culture |
| "Khám kênh giúp em" (lặp 10 lần) | (cross-cluster — service request) | Mere Exposure (frequency) | Collectivism + Hierarchy |
| "Lý thuyết quá" (objection 14 likes) | (meta — về creator) | Pratfall Effect | — |
| "Tôi có thể học được không ạ" (cô chú) | 2. Procrastination + Hierarchy | Confirmation Bias + BJ Fogg | Hierarchy (đại từ "cô chú") |

---

## 9. Versioning & Maintenance

- **v1.0 (2026-05-17)**: Initial — 5 cluster, 12 models, 4 VN concepts, từ phân tích 401 cmt niche xây kênh TikTok.
- **Cần update khi**:
  - Phát hiện cluster mới khi onboard niche khác → thêm vào section 1
  - Phát hiện anti-pattern mới trong brief production → thêm vào section 6
  - Lexicon thay đổi (audience trends shift) → re-mine từng quý

- **Niche-specific override**: file `niche_configs/<slug>_personas.md` có thể override 5 cluster mặc định cho niche cụ thể (vd niche skincare có cluster "Acne Shame" thay vì "Macro Despair").

---

## Phụ lục — Danh sách 58 models BỎ khỏi SKILL.md

(để team biết tại sao không inject toàn bộ skill)

**Pricing Psychology (5)** — không apply task này:
Charm Pricing, Rounded-Price Effect, Rule of 100, Price Relativity, Mental Accounting (Pricing).

**Foundational Thinking đa số (10)** — strategic, không tactical:
First Principles, Inversion, Occam's Razor, Pareto, Local vs Global Optima, Theory of Constraints, Opportunity Cost, Diminishing Returns, Second-Order Thinking, Barbell.

**Sales tactics (4)** — không phải content:
Door-in-the-Face, Foot-in-the-Door, Default Effect, Decoy Effect.

**Growth/Web design (8)**:
Hick's Law, AIDA Funnel, Rule of 7, Cobra Effect, Network Effects, Flywheel, Switching Costs, Critical Mass.

**Meta-thinking (5)**:
Map ≠ Territory, Survivorship Bias, Probabilistic Thinking, Exploration vs Exploitation, North Star Metric.

**Còn lại (~26)** — relevant lúc nhỏ nhưng overlap với 12 đã chọn (vd Authority Bias overlap Social Proof, Anchoring overlap Framing trong context content).

→ Tổng bỏ 58. Giữ 12. Lý do: focus + token efficiency + actionable per angle.
