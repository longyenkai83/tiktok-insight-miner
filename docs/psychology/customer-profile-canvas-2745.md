# Customer Profile Canvas — Phụ nữ Kinh doanh 27-45 (Chị Hiền)

> **Phiên bản**: v1.0 (2026-05-17)
> **Phương pháp**: Strategyzer Value Proposition Canvas — Customer Profile (Pains → Gains → Jobs)
> **Method tổng**: 4 bước Liệt kê → Sắp xếp → Lựa chọn → Thực thi cho mỗi component
> **Áp dụng**: input cho content calendar, product offer, brand positioning

## 0. Setup

**Audience target**: Phụ nữ Việt Nam 27-45, làm chủ/co-founder doanh nghiệp nhỏ (online shop, dịch vụ, F&B, beauty, coaching). 60% đã lập gia đình có con 0-12 tuổi. Thu nhập 20-200tr/tháng, cash-flow không ổn. Tự học marketing qua TikTok-FB-khóa học online.

**Data sources** (đã verify):
- [niche_configs/kinh-doanh-27-45.json](../../niche_configs/kinh-doanh-27-45.json) — 9 main_problems + persona
- [niche_configs/kinh-doanh-27-45_meta_pains.md](../../niche_configs/kinh-doanh-27-45_meta_pains.md) — 5 pain ẨN
- [output/.../brief report.md](../../output/kinh-doanh-27-45/test%20t%C3%A2m%20l%C3%AD%2017-5/brief%20report.md) — brief v1.1 production
- [docs/psychology/sample-brief-fanpage-2745-v1.md](sample-brief-fanpage-2745-v1.md) — sample human-grade
- 700+ comments thật từ 8 videos đã scrape

**Tone**: peer-level (chị/em/mình), KHÔNG guru, KHÔNG infantile.

---

# PHẦN A — CUSTOMER PAINS (Nỗi đau khách hàng)

## A.1 LIỆT KÊ — 28 pains thô (không filter, có source)

### Nhóm operational/business

| # | Pain | Source signal | Strength |
|---|---|---|:---:|
| P01 | Kinh doanh ế ẩm, doanh thu giảm, khách không quay lại | comment "chi kinh Doanh nhà nghỉ giờ cũng ế" (6 likes) + niche config KINH_DOANH_KIET_SUC | Cao |
| P02 | Chạy ads xong content vẫn flop, không ra đơn | "Em làm mkt cũng thấy tiktok... chạy ads xong nd cứ flop" (12 likes) | Cao |
| P03 | 3 tuần lên xu hướng nhưng không chuyển đổi ra đơn | "E xây kênh 3 tuần có 4-5 video lên xu hướng. Mà e k chuyển đổi ra đơn được" (7 likes) | Cao |
| P04 | Một mình gánh tất cả việc (delegate không được) | niche config sub_problem | Cao |
| P05 | Cash-flow tháng nào lo tháng đó | niche config TIEN_BAC_BINH_YEN | Trung |
| P06 | Sợ mất kênh sau 1-2 năm build | "Lập kênh thành công chỉ sợ bị mất kênh" (5 likes) | Trung |
| P07 | Bị chê content "lý thuyết quá" | "ly thuyết quá" (14 likes) | Trung |

### Nhóm emotional/psychological

| # | Pain | Source signal | Strength |
|---|---|---|:---:|
| P08 | Tự ti, không thấy mình có giá trị để chia sẻ | "em nghĩ mãi chưa thấy mình có gì giúp được cho người khác" (10 likes) + niche config GIA_TRI_BAN_THAN | **Rất cao** |
| P09 | Không biết kể câu chuyện bản thân (đời "bình thường") | "biết là trend chân thực rồi nhưng không biết kể câu chuyện bản thân thế nào" (11 likes) | **Rất cao** |
| P10 | Chần chừ 5+ năm vì đợi "đủ giỏi" | "Từ 2020 mình... 5 năm vẫn dậm chân... đợi mình giỏi hơn" (9 likes) | Cao |
| P11 | Hoang mang khi bắt đầu, bắt đầu sai nhiều lần | "hoang mang và nhìu lần bắt đầu sai .và h nản" (56 likes ở dataset cũ) | Cao |
| P12 | Xem lại video của mình thấy chán, xóa nhiều lần | "xem lai video của mình còn thấy chán" (9 likes) + "làm hơn nửa năm ko viral, chạnh lòng và xóa nhiều video" (3 likes) | Cao |
| P13 | Nghe hiểu nhưng không làm được | "Nghe hiểu mà vẫn k làm gì được đành vui thôi" (19 likes ở dataset cũ) | Trung |

### Nhóm social/face culture

| # | Pain | Source signal | Strength |
|---|---|---|:---:|
| P14 | Sợ người quen / đồng nghiệp / gia đình thấy mình "diễn" trên video | niche config sub_problem "sợ comment tiêu cực, screenshot drama" + "sợ gia đình biết" | **Rất cao** |
| P15 | Ngại lộ mặt, ngại nghe giọng mình | "giọng thì ko hay nên chẳng dám nói giọng thật" (dataset cũ) | Cao |
| P16 | "Dưới 1K follow" — xấu hổ khi xin mẫu/cộng tác | "ưu điểm: rất muốn xin mẫu Nhược điểm: DƯỚI 1K FL" (7 likes) | Trung |
| P17 | So sánh với KOL khác → nản | niche config sub_problem GIA_TRI_BAN_THAN | Trung |

### Nhóm time/life poverty (đặc trưng 27-45)

| # | Pain | Source signal | Strength |
|---|---|---|:---:|
| P18 | Có ≤30 phút/ngày liên tục (job + con + nhà + chồng) | meta_pains #1 + comment "lười làm video, viết thì được" (25 likes) | **Rất cao** |
| P19 | Tối kiệt sức → scroll thay vì làm việc quan trọng | niche config KY_LUAT_THOI_QUEN | Cao |
| P20 | Không có "me time" buổi sáng (lo con) | niche config sub_problem | Trung |

### Nhóm meta/reputation (ẨN — face culture)

| # | Pain | Source signal | Strength |
|---|---|---|:---:|
| P21 | **Reputation risk** — đã có 10+ năm sự nghiệp, sợ output kém ảnh hưởng identity cũ | meta_pains #2 | **Rất cao** |
| P22 | **Mid-career pivot anxiety** — sợ "muộn", sợ vứt 10-15 năm | meta_pains #3 + "có quá muộn không" lặp ≥3 lần | **Rất cao** |
| P23 | **Identity reconstruction** — không biết là "kế toán" hay "creator" | meta_pains #4 | Cao |
| P24 | **AI displacement fear** — chuyên môn 12 năm bị AI thay 60% task | meta_pains #5 (không có comment công khai) | **Rất cao** (ẩn) |
| P25 | **Regret aversion** — sợ thử rồi fail công khai sau 35 | meta_pains #3 | Cao |

### Nhóm macro/societal

| # | Pain | Source signal | Strength |
|---|---|---|:---:|
| P26 | Bất lực kinh tế ("Người nghèo còn nước mắt đâu mà khóc") | dataset 401 cmt — 293 likes | **Rất cao** |
| P27 | "Đi làm thuê khoẻ hơn làm chủ" — hối hận pivot lên làm chủ | dataset cũ — 34 likes | Cao |
| P28 | TikTok bão hoà: "100 người bán, 10 người mua" | brief v1.1 — 33 likes | Trung |

---

## A.2 SẮP XẾP — Pain matrix theo Strategyzer

### Cột 1: theo loại (Functional / Emotional / Social / Risk)

| Loại | Count | Top items |
|---|:---:|---|
| **Functional** (operational) | 7 | P01, P02, P03, P04, P05, P06, P07 |
| **Emotional** (cảm xúc) | 6 | P08, P09, P10, P11, P12, P13 |
| **Social** (face culture) | 4 | P14, P15, P16, P17 |
| **Time/Life** | 3 | P18, P19, P20 |
| **Meta/Hidden** (ẩn) | 5 | P21, P22, P23, P24, P25 |
| **Macro/Societal** | 3 | P26, P27, P28 |

### Cột 2: theo intensity (Extreme / Severe / Moderate)

| Intensity | Pains |
|---|---|
| **EXTREME** (rất cao + lan rộng) | P08 (tự ti giá trị), P09 (không biết kể chuyện), P14 (sợ người quen thấy), P18 (time poverty), P21 (reputation risk), P22 (mid-career), P24 (AI displacement), P26 (macro despair) |
| **SEVERE** (cao + cụ thể) | P01, P02, P03, P04, P10, P11, P12, P15, P19, P23, P25, P27 |
| **MODERATE** | P05, P06, P07, P13, P16, P17, P20, P28 |

### Cột 3: theo độ "có thể nói công khai"

| Visibility | Pains |
|---|---|
| **Nói công khai dễ** (có trong comment) | P01-P03, P06-P15, P18-P20, P26-P28 |
| **Khó nói công khai** (face culture) — chỉ ra trong tư vấn 1-1 | P21, P22, P23, P25 |
| **CỰC khó nói** (sĩ diện cao) | **P24 (AI displacement)** — chưa bao giờ thấy comment công khai |

---

## A.3 LỰA CHỌN — Top 10 priority pains

**Công thức ưu tiên**: Intensity × (Frequency hoặc Demand signal) × Pain-Reliever-Mappability

| Rank | Pain | Intensity | Demand | Mappable | Tổng |
|:---:|---|:---:|:---:|:---:|:---:|
| 🥇 1 | P08 — Tự ti "không có gì để chia sẻ" | Extreme | 10+ comments + dataset cũ | Cao | **9.5** |
| 🥇 2 | P09 — Không biết kể chuyện bản thân | Extreme | 11+ likes + lặp ≥3 | Cao | **9.3** |
| 🥇 3 | P18 — Time poverty (không phải lười) | Extreme | 25+ likes + meta | Cao | **9.2** |
| 🥇 4 | P22 — Mid-career pivot anxiety | Extreme | Lặp ≥3 "muộn" | Cao | **9.0** |
| 🥇 5 | P21 — Reputation risk | Extreme | Meta + comments "sợ đăng" | Cao | **8.8** |
| 🥈 6 | P14 — Sợ người quen thấy | Extreme | Niche config + face culture | Trung | **8.5** |
| 🥈 7 | P26 — Macro despair (nghèo/khó kinh tế) | Extreme | 293 likes peak | Thấp (chỉ emotional positioning) | **8.3** |
| 🥈 8 | P02 — Chạy ads xong content flop | Severe | 12+ likes | Cao | **7.8** |
| 🥈 9 | P03 — Viral không ra đơn | Severe | 7+ likes + pattern | Cao | **7.5** |
| 🥉 10 | P24 — AI displacement fear | Extreme | 0 (ẩn) | Cao (Bold angle) | **7.3** |

---

## A.4 THỰC THI — Pain Reliever cho top 10

| Rank | Pain | Pain Reliever (sản phẩm/content/framework giảm đau) | Format gợi ý |
|:---:|---|---|---|
| 1 | P08 Tự ti | **Curse of Knowledge audit** — bài tập 3 cột (TASK / câu hỏi khách hay hỏi / lỗi người mới mắc). Reframe: "chị quá quen với chuyên môn nên không thấy giá trị" | Video 90s + workbook PDF |
| 2 | P09 Không biết kể chuyện | **3 prompt đào câu chuyện đời thường**: (a) Khách hỏi gì hôm nay (b) Sai lầm 5 năm trước (c) Đơn khó nhất tuần. Bộ 20 prompt DM | Video 60s + DM workflow |
| 3 | P18 Time poverty | **Hệ thống content cho ≤30 phút/ngày**: 3 block 10 phút (T2-3-4 ghi ý / T5 quay / CN dựng) + 1-góc-quay 1-outfit 1-template | Video 90s + content calendar template |
| 4 | P22 Mid-career pivot | **Sunk cost reframe**: "10-15 năm KHÔNG mất khi pivot — đó là chất liệu authority" + Minimum Viable Test 30 ngày ẩn danh | Series 3 video + case studies |
| 5 | P21 Reputation risk | **30 ngày ẩn danh protocol**: kênh phụ không tag bạn bè, không share FB cá nhân → sau 30 ngày unmask nếu work | Video 60s + checklist setup |
| 6 | P14 Sợ người quen thấy | Kết hợp P21 + face-saving frame: "Hướng nội không phải bug, là feature — 3 công thức không cần lộ mặt" | Video 90s + 3 video mẫu |
| 7 | P26 Macro despair | **Emotional positioning ONLY** — không bridge tip. "Tôi từng đứng đó. Cho phép mình khóc. 1 điều giúp tôi không vỡ vụn" | Video 60s, không CTA bán |
| 8 | P02 Ads flop | **3 diagnose**: (a) authentic deficit (b) hook 3s yếu (c) CTA mơ hồ. Format A/B before-after | Video 90s + audit template |
| 9 | P03 Viral no convert | **Bridge bio-pinned-CTA**: 3 lỗi conversion bio + pinned + caption. Audit checklist | Video 90s + bio template |
| 10 | P24 AI displacement | **Phân tách chuyên môn 3 phần**: 60% TASK (AI thay) + 30% JUDGMENT (AI chưa) + 10% RELATIONSHIP (AI không). Cite MIT Sloan 2024 | Video 120s — Bold angle, có thể viral lớn |

---

# PHẦN B — CUSTOMER GAINS (Lợi ích mong muốn)

## B.1 LIỆT KÊ — 24 gains thô

### Functional gains

| # | Gain | Source |
|---|---|---|
| G01 | Doanh thu ổn định, dòng tiền dự đoán được | niche config |
| G02 | Lên xu hướng + chuyển đổi ra đơn | brief v1.1 |
| G03 | Có thêm khách hàng "đúng tệp" | brief v1.1 angle 9 — "Cần tệp khán giả đúng" |
| G04 | Tăng follow page/kênh | "Mong khám kênh", "xin vía lên xu hướng" |
| G05 | Có template/system làm content lặp được | brief v1.1 angle 4 |
| G06 | Hiểu thuật toán platform | niche config |
| G07 | Biết viết hook giữ người xem | niche config + "Bài học: chân thực gần gũi" |

### Emotional gains

| # | Gain | Source |
|---|---|---|
| G08 | Tự tin xuất hiện trên camera | "Xin vía để được tự tin như chị" (2 likes) + niche config |
| G09 | Cảm giác "đã làm đủ" — không tự trách | niche config GIA_TRI_BAN_THAN hidden_desire |
| G10 | "Nhẹ đầu" — không lo cash flow | niche config KINH_DOANH_KIET_SUC hidden_desire |
| G11 | Tự hào khi nhìn lại tuần làm việc | niche config KY_LUAT_THOI_QUEN hidden_desire |
| G12 | Cảm giác kiểm soát được cuộc sống (vs bị cuốn) | niche config TIEN_BAC_BINH_YEN |
| G13 | Cảm giác "là chính mình" trên camera (không phải "diễn") | niche config GIA_TRI_BAN_THAN hidden_desire |

### Social gains

| # | Gain | Source |
|---|---|---|
| G14 | Được công nhận là chuyên gia trong ngành | niche config |
| G15 | Cộng đồng peer-to-peer ("ai cũng như mình") | "Có ai giống mình vừa lập nick mới" (771 likes dataset cũ) |
| G16 | Được creator authority "khám kênh" / nhận xét | "Mong shop khám kênh" lặp ≥10 |
| G17 | Brand cá nhân có authority — không cần xin xỏ | implied |

### Required (bắt buộc — phải có mới mua/dùng)

| # | Gain | Source |
|---|---|---|
| G18 | Method phải ÁP DỤNG được với time budget ≤30 phút/ngày | meta_pains |
| G19 | Method không yêu cầu thiết bị đắt (máy quay, studio) | "Bài học: không cần đầu tư quá nhiều" (209 likes) |
| G20 | Không lộ mặt vẫn work được (cho hướng nội + face culture) | "Chủ shop hướng nội k biết kể chuyện" (203 likes) |

### Desired (mong muốn — chưa cần thiết nhưng thích)

| # | Gain | Source |
|---|---|---|
| G21 | Có communities/peer support cùng trình độ | implied |
| G22 | Recurring series có lịch (thứ 5, ...) thay vì 1-shot | brief v1.1 angle 6 |

### Unexpected delights

| # | Gain | Source |
|---|---|---|
| G23 | Được khôi phục identity sau khi làm mẹ/làm vợ | meta_pains #4 |
| G24 | Được respect by peer mature (KHÔNG bị treated như Gen Z) | derived from "27-45 cứng" |

---

## B.2 SẮP XẾP — Gain matrix theo Strategyzer

### Cột 1: theo loại

| Loại | Count | Top items |
|---|:---:|---|
| **Functional gains** | 7 | G01-G07 |
| **Emotional gains** | 6 | G08-G13 |
| **Social gains** | 4 | G14-G17 |
| **Cost savings** | 2 | G18 (time), G19 (money) |
| **Identity gains** | 3 | G20, G23, G24 |
| **Process gains** | 2 | G21, G22 |

### Cột 2: theo Strategyzer scale (Required / Expected / Desired / Unexpected)

| Scale | Definition | Items |
|---|---|---|
| **REQUIRED** | Không có = không mua/dùng | G18 (time-budget fit), G19 (no expensive gear), G20 (no face required) |
| **EXPECTED** | Mặc định phải có | G01, G02, G04, G05, G06, G07, G08, G14 |
| **DESIRED** | Thích có, sẵn sàng trả thêm | G03, G09, G10, G11, G12, G13, G15, G16, G17, G21, G22 |
| **UNEXPECTED** | Bất ngờ thích thú = WOW | G23 (identity restoration), G24 (mature respect) |

---

## B.3 LỰA CHỌN — Top 10 gains cần ưu tiên đáp ứng

| Rank | Gain | Scale | Emotional weight | Mappable | Tổng |
|:---:|---|:---:|:---:|:---:|:---:|
| 🥇 1 | G18 — Method fit ≤30 phút/ngày | Required | 9 | Cao | **9.5** |
| 🥇 2 | G20 — Không lộ mặt vẫn work | Required | 9 | Cao | **9.3** |
| 🥇 3 | G23 — Khôi phục identity (sau mẹ/vợ/pivot) | Unexpected | 10 | Trung | **9.2** |
| 🥇 4 | G09 — Cảm giác "đã làm đủ", không tự trách | Desired | 9 | Cao | **9.0** |
| 🥇 5 | G19 — Không cần thiết bị đắt | Required | 7 | Cao | **8.8** |
| 🥈 6 | G13 — Cảm giác "là chính mình" trên camera | Desired | 9 | Cao | **8.5** |
| 🥈 7 | G14 — Được công nhận là chuyên gia | Desired | 8 | Cao | **8.3** |
| 🥈 8 | G24 — Được respect by peer mature | Unexpected | 8 | Cao | **8.0** |
| 🥈 9 | G15 — Cộng đồng peer cùng trình độ | Desired | 7 | Trung | **7.8** |
| 🥉 10 | G03 — Khách "đúng tệp" (không chạy theo view) | Desired | 8 | Cao | **7.5** |

---

## B.4 THỰC THI — Gain Creator cho top 10

| Rank | Gain | Gain Creator | Format |
|:---:|---|---|---|
| 1 | G18 30-phút | "3 block 10 phút/tuần" + content calendar template (Notion/Excel) | Workbook + video tutorial |
| 2 | G20 Không lộ mặt | Bộ 5 format video không cần mặt: voice + tay sản phẩm, screen recording, slideshow, sản phẩm trên bàn, B-roll thiên nhiên | Mini-course 5 video |
| 3 | G23 Khôi phục identity | Series "Identity Reconstruction": phỏng vấn 5 chị 38+ đã pivot thành công. Format documentary mini-podcast | Podcast series 5 tập |
| 4 | G09 "Đã làm đủ" | Weekly review framework: 5 câu hỏi mỗi chủ nhật + community peer recognition | Workbook PDF + FB group ritual |
| 5 | G19 Không thiết bị đắt | Setup tổng <2 triệu: điện thoại + ring light USB + tripod 200k | Video unboxing + buying guide |
| 6 | G13 "Là chính mình" | Voice training mini-course: 5 bài tập 10 phút (không phải diễn xuất) | Mini-course 5 video |
| 7 | G14 Công nhận chuyên gia | "Authority Stacking" method: niche-deep content (KHÔNG broad) + answer 1 câu hỏi/tuần | Framework + 30-day prompts |
| 8 | G24 Respect peer mature | Brand voice: peer-level, KHÔNG infantile. Caption opening 5 dòng, KHÔNG comment-keyword CTA | Brand guideline doc |
| 9 | G15 Cộng đồng peer | FB Group "Chị làm chủ" — chỉ 35+, vào theo invitation, weekly thread | Group + moderation playbook |
| 10 | G03 Khách đúng tệp | 3 signal audience-fit: comment >2 dòng / save rate >3% / inbox personal. Audit kit | Audit checklist + template |

---

# PHẦN C — CUSTOMER JOBS (Việc khách hàng cần làm)

## C.1 LIỆT KÊ — 18 jobs thô

### Functional jobs (việc thực dụng)

| # | Job | Source |
|---|---|---|
| J01 | Xây kênh TikTok/FB từ 0 đến có khách | "Mình muốn xây kênh ạ. Hỗ trợ mình với" + niche config |
| J02 | Học cách viết hook giữ người xem 3-10s đầu | niche config + brief v1.1 |
| J03 | Học cách convert view → đơn / lead | "lên xu hướng nhưng k chuyển đổi ra đơn" |
| J04 | Tìm và định nghĩa "đúng tệp" khách hàng | brief v1.1 angle 9 |
| J05 | Xây hệ thống content lặp được (không phải lần nào cũng kiệt) | niche config + brief v1.1 angle 4 |
| J06 | Quản lý cash flow + scale doanh nghiệp lên 5+ năm | niche config KINH_DOANH_KIET_SUC |
| J07 | Bảo vệ kênh khỏi bị mất (2FA, backup) | brief v1.1 angle 5 |

### Emotional jobs (việc cảm xúc)

| # | Job | Source |
|---|---|---|
| J08 | Vượt qua imposter syndrome khi xuất hiện trên camera | niche config GIA_TRI_BAN_THAN |
| J09 | Tìm "câu chuyện bản thân" để kể (khi đời "bình thường") | brief v1.1 + dataset |
| J10 | Vượt qua chần chừ ("5 năm dậm chân") để bắt đầu | dataset |
| J11 | Giữ động lực khi 6 tháng đầu không viral | "làm hơn nửa năm không viral, chạnh lòng" |
| J12 | Reconcile identity cũ (kế toán/dược sĩ/...) với identity mới (creator) | meta_pains #4 |

### Social jobs (việc xã hội)

| # | Job | Source |
|---|---|---|
| J13 | Build reputation là chuyên gia trong ngành | niche config |
| J14 | Có cộng đồng peer-to-peer không bị "1 mình" | "ai cũng như mình không" |
| J15 | Được creator authority "khám kênh" / nhận xét cụ thể | "khám kênh giúp em" lặp ≥10 |
| J16 | Bảo vệ face khi pivot sang nghề mới (đặc biệt 35+) | meta_pains #3 |

### Supporting jobs (việc phụ trợ — thường bị bỏ qua)

| # | Job | Source |
|---|---|---|
| J17 | Tìm 1-2 mentor đáng tin trong 1 năm đầu | implied + "Hỗ trợ mình với" |
| J18 | Đối mặt với câu hỏi "AI có thay tôi không sau 5 năm?" | meta_pains #5 (ẩn) |

---

## C.2 SẮP XẾP — Job matrix theo Strategyzer

### Cột 1: theo loại

| Loại | Count | Items |
|---|:---:|---|
| **Functional** | 7 | J01-J07 |
| **Emotional** | 5 | J08-J12 |
| **Social** | 4 | J13-J16 |
| **Supporting** | 2 | J17, J18 |

### Cột 2: theo customer journey stage

| Stage | Jobs |
|---|---|
| **Pre-start** (chưa lập kênh) | J04, J09, J10, J12, J16, J17 |
| **Starting** (0-3 tháng) | J01, J02, J05, J08 |
| **Growing** (3-12 tháng) | J03, J11, J13, J14, J15 |
| **Scaling** (1+ năm) | J06, J07, J18 |

### Cột 3: theo độ quan trọng (Critical / Important / Nice-to-have)

| Importance | Jobs |
|---|---|
| **CRITICAL** ("không thể không hoàn thành") | J01, J05, J08, J09, J12, J16 |
| **IMPORTANT** | J02, J03, J04, J10, J11, J13, J14, J15 |
| **Nice-to-have** | J06, J07, J17, J18 |

---

## C.3 LỰA CHỌN — Top 8 jobs cần map vào content + product

| Rank | Job | Importance | Stage | Emotional weight | Tổng |
|:---:|---|:---:|---|:---:|:---:|
| 🥇 1 | J05 — Xây hệ thống content lặp được | Critical | Starting+ | 9 | **9.5** |
| 🥇 2 | J09 — Tìm câu chuyện bản thân để kể | Critical | Pre-start + Starting | 9 | **9.3** |
| 🥇 3 | J08 — Vượt imposter trên camera | Critical | Starting | 10 | **9.2** |
| 🥇 4 | J12 — Reconcile identity cũ + mới | Critical | Pre-start | 10 | **9.0** |
| 🥈 5 | J04 — Định nghĩa "đúng tệp" khách | Important | Pre-start | 8 | **8.5** |
| 🥈 6 | J03 — Convert view → đơn/lead | Important | Growing | 8 | **8.3** |
| 🥈 7 | J11 — Giữ động lực 6 tháng đầu | Important | Growing | 9 | **8.0** |
| 🥉 8 | J15 — Được khám kênh / nhận xét cụ thể | Important | Growing | 7 | **7.5** |

---

## C.4 THỰC THI — JTBD framing cho top 8

Mỗi job phrase theo **JTBD format**: "Khi [situation], tôi muốn [motivation], để [outcome]"

| Rank | Job | JTBD Statement | Content/Product match |
|:---:|---|---|---|
| 1 | J05 Hệ thống content | "Khi tôi có ≤30 phút/ngày + con nhỏ, tôi muốn 1 hệ thống content lặp được, để tôi không kiệt sức và đăng đều" | **Workbook**: Content System 30-phút |
| 2 | J09 Câu chuyện bản thân | "Khi tôi muốn build authentic content nhưng đời tôi 'bình thường', tôi muốn 3 prompt cụ thể để đào câu chuyện, để tôi có cái để kể mỗi tuần" | **DM Workflow**: 20 prompt cards |
| 3 | J08 Imposter camera | "Khi tôi đứng trước camera bị khớp, tôi muốn 5 bài tập 10 phút (không phải học diễn xuất), để tôi quay được tự nhiên" | **Mini-course**: Voice & Camera 5 tập |
| 4 | J12 Identity reconcile | "Khi tôi đã có sự nghiệp 10+ năm + muốn làm creator, tôi muốn frame 'kênh là extension không phải replace', để identity cũ không bị mất" | **Workshop**: Identity Bridge 2h |
| 5 | J04 Đúng tệp | "Khi tôi đăng video chưa biết ai sẽ xem, tôi muốn 3 signal cụ thể đo audience-fit (không bằng view), để tôi biết đi đúng hướng" | **Audit kit**: 3-signal checklist |
| 6 | J03 Convert | "Khi tôi có view 50k mà 0 đơn, tôi muốn audit 3 lỗi conversion (bio + pinned + caption), để biết fix chỗ nào trước" | **Audit template**: Bridge Map |
| 7 | J11 Động lực 6 tháng | "Khi tôi làm 6 tháng chưa viral, tôi muốn benchmark thật (8-14 tháng average), để biết tôi đang đi đúng tốc độ, không phải đang fail" | **Data report**: Industry benchmark + community |
| 8 | J15 Khám kênh | "Khi tôi muốn feedback cá nhân hoá, tôi muốn 1 series public review (không phải 1-1 tốn $$$), để được nhận xét + thấy kênh khác giống mình" | **Series**: Weekly Khám Kênh livestream |

---

# PHẦN D — VALUE MAP (Synthesis Pains + Gains + Jobs)

## D.1 Pain Relievers map (top 10 pain → relievers)

Xem PHẦN A.4 — đã liệt kê đầy đủ.

## D.2 Gain Creators map (top 10 gain → creators)

Xem PHẦN B.4 — đã liệt kê đầy đủ.

## D.3 Products & Services candidates (sản phẩm chị Hiền có thể bán)

Dựa trên Pain + Gain + Job mapping, em đề xuất 5 product offer theo độ ưu tiên:

| Rank | Product | Solves | Price range | Effort build |
|:---:|---|---|---|---|
| 🥇 1 | **Content System 30-phút** (workbook + 30-day calendar template) | P18, J05, G18 | 299-499k | 2 tuần |
| 🥇 2 | **Voice & Camera 5-tập mini-course** (cho hướng nội + face culture) | P14, P15, J08, G13, G20 | 590-990k | 1 tháng |
| 🥈 3 | **Identity Bridge Workshop** (2h live cho chị 35+ pivot career) | P21, P22, J12, G23 | 1.5-2.9 triệu | 3 tuần |
| 🥈 4 | **3-Signal Audit Kit** (workbook + template + 1 video voice note) | P03, J03, J04, G03 | 199-349k | 1 tuần |
| 🥉 5 | **Weekly Khám Kênh Series** (recurring livestream + recording) | J15, G15, G21 | Free → upsell coaching | Ongoing |

---

# PHẦN E — CONTENT ROADMAP 30 NGÀY (áp dụng vào lịch viết)

## E.1 Phân bổ content theo top pains

| Tuần | Theme chính | Pains cover | Content count |
|:---:|---|---|:---:|
| Tuần 1 | **Identity & Tự ti** (mở màn — pain phổ biến nhất) | P08, P09, P14 | 4 video |
| Tuần 2 | **Time Poverty & System** | P18, P19, J05 | 4 video |
| Tuần 3 | **Mid-career & Reputation** (Bold week — đào pain ẩn) | P21, P22, P24 | 4 video |
| Tuần 4 | **Convert & Scale** (cho audience đã start) | P02, P03, J03 | 4 video |

## E.2 30 content slots — 1 dòng/slot

| Ngày | Theme | Angle | Type | Format |
|:---:|---|---|---|---|
| D01 | Tự ti | Curse of Knowledge — chị không thiếu giá trị | How-to | Video 90s |
| D02 | Tự ti | 3 cột bài tập "Khách hỏi gì" | How-to | Carousel 5 slide |
| D03 | Câu chuyện | 3 prompt đào chuyện đời thường | How-to | Video 60s |
| D04 | Face | Hướng nội KHÔNG cần fix — là feature | Reframe | Video 90s |
| D05 | Câu chuyện | Demo 1 video 30s từ "khách hỏi hôm nay" | Demo | Video 30s |
| D06 | Tự ti | Case chị Linh dược sĩ 47 câu hỏi (UGC) | Social Proof | Carousel + caption dài |
| D07 | Tự ti | Live Q&A community (FB group) | Live | 30 phút |
| D08 | Time poverty | "Chị không lười — chị có 30 phút" reframe | Reframe | Video 90s + caption dài |
| D09 | System | 3 block 10 phút breakdown | How-to | Carousel |
| D10 | System | 1-góc-quay 1-outfit 1-template | How-to | Video 60s |
| D11 | System | Case chị Hằng mẹ 2 con 25p/ngày → 12k | Social Proof | Video 90s |
| D12 | System | Template content calendar (free download) | Lead magnet | Caption dài + download |
| D13 | Time poverty | Bộ kit cứng giảm decision fatigue | How-to | Video 60s |
| D14 | System | Live demo: viết video trong 25 phút | Live demo | 30 phút |
| D15 | Mid-career | "10 năm KHÔNG mất khi pivot" | Reframe | Video 90s |
| D16 | Reputation | 30 ngày ẩn danh protocol | How-to | Video 90s |
| D17 | Mid-career | Case chị Mai dược sĩ 14 năm → 22k follow | Social Proof | Carousel |
| D18 | **AI displacement** (BOLD) | Phân tách 60-30-10 chuyên môn | Bold angle | Video 120s |
| D19 | Mid-career | Sunk cost fallacy — đặt tên đúng | Reframe | Caption dài + 3 case |
| D20 | Reputation | Minimum Viable Test 30 ngày | How-to | Video 60s |
| D21 | Mid-career | Live: "Hỏi gì về pivot career" | Live | 45 phút |
| D22 | Convert | 3 lỗi bio + pinned + CTA | How-to | Carousel |
| D23 | Convert | Audit template (free) | Lead magnet | Caption dài + download |
| D24 | Convert | Case kênh A 50k view 0.3% vs kênh B 3k view 4% | Social Proof | Video 90s |
| D25 | Convert | 3 signal đúng tệp khách | How-to | Carousel |
| D26 | Scale | 3 lớp bảo vệ kênh (2FA, email list, repurpose) | How-to | Video 90s |
| D27 | Scale | Khám kênh série tập 1 | Series | Livestream 30p |
| D28 | Macro despair | "Người nghèo còn nước mắt đâu mà khóc" (emotional positioning, KHÔNG bridge tip) | Emotional Positioning | Video 60s |
| D29 | UGC | Repost 5 bài học audience tự viết | Social Proof | Carousel |
| D30 | Roadmap | Recap 30 ngày + thông báo tháng tới | Update | Caption dài + thumbnail |

---

# PHẦN F — Tóm tắt 1 trang (executive summary)

## Audience Profile

Phụ nữ Việt Nam 27-45, làm chủ doanh nghiệp nhỏ, 60% có con 0-12 tuổi, thu nhập 20-200tr/tháng cash-flow không ổn, đọc Fanpage nhiều hơn TikTok, đã thử nhiều content marketing → critical, không dễ bị clickbait.

## Top 5 Pain (đào ngay)

1. **Tự ti "không có gì để chia sẻ"** — Curse of Knowledge
2. **Không biết kể chuyện bản thân** — Authentic trend fatigue
3. **Time poverty** (KHÔNG phải lười) — Mental Accounting
4. **Mid-career pivot anxiety** — Sunk Cost + Regret Aversion
5. **Reputation risk** — Loss Aversion (đã có sự nghiệp 10+ năm)

## Top 5 Gain (cần đáp ứng)

1. **Method fit ≤30 phút/ngày** (Required)
2. **Không lộ mặt vẫn work** (Required cho hướng nội)
3. **Khôi phục identity** sau mẹ/vợ/pivot (Unexpected — WOW)
4. **Cảm giác "đã làm đủ"** (Desired — emotional)
5. **Không cần thiết bị đắt** (Required cost-saving)

## Top 5 Job (cần solve)

1. **Xây hệ thống content lặp được** (Critical)
2. **Tìm câu chuyện bản thân để kể** (Critical)
3. **Vượt imposter trên camera** (Critical)
4. **Reconcile identity cũ + mới** (Critical)
5. **Định nghĩa "đúng tệp" khách** (Important)

## 5 Product Offer Candidates (theo priority)

1. Content System 30-phút (workbook) — 299-499k
2. Voice & Camera mini-course — 590-990k
3. Identity Bridge Workshop — 1.5-2.9 triệu
4. 3-Signal Audit Kit — 199-349k
5. Weekly Khám Kênh Series — Free → upsell

## Content Roadmap

30 video / 4 tuần theme: Tự ti → Time Poverty → Mid-career → Convert+Scale

---

## Versioning

- **v1.0 (2026-05-17)**: Initial — từ niche config + meta_pains + brief v1.0 + brief v1.1 + sample human-grade
- Cần update khi: có dataset mới ≥500 cmt, có niche khác cần Canvas riêng, hoặc product offer đi vào market.
