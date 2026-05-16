# 🎯 Chị Hiền 30-Day Content Strategy v2

> **Brand**: Trịnh Nhi Hiền · **Niche**: kinh-doanh-27-45
>
> **Generated**: 2026-05-10 · v2.0
> **Status**: spec chính cho 30 bài đầu — chờ brand owner duyệt trước khi sinh insight options.
>
> **Vai trò**: single source of truth cho app sinh nội dung 30 bài đầu. App KHÔNG được sinh bài nếu không có đủ thông tin từ file này. Brand owner KHÔNG duyệt nếu app sinh ngoài spec này.

---

## 1. Purpose — Vì sao reset từ D1 v2

### 1.1 Vấn đề của v1

D1–D15 v1 đã được viết và polish nhiều lần. Chất lượng từng bài tốt, nhưng phát sinh 3 vấn đề khi nhìn ở tầng strategy:

1. **Phân bố layer lệch**: 14 ngày đầu (D1–D14) dồn hết vào Inner Clarity / Behavior / Role Burden. Đến D15 mới chạm Identity. Money / System / Brand / Marketing không xuất hiện trước D22+. Với audience là phụ nữ kinh doanh đang muốn xây thu nhập, phân bố này quá nặng về nội tâm và quá ít về thực tiễn.
2. **Topic bị bó cứng**: tránh hoàn toàn business / marketing / fanpage / brand trong 30 bài đầu để giữ "trust building". Nhưng audience cần biết Chị Hiền có hiểu thị trường, có quan sát người mua, có tư duy hệ thống — không chỉ biết về cảm xúc.
3. **App khó vận hành**: v1 được viết tay từng bài + audit retroactive. App không có spec đủ rõ để sinh bài tự động + pass guardrails ngay từ đầu.

### 1.2 Giải pháp v2

Reset từ D1, mở rộng topic sang 6 cụm (Market / Self-Worth / Brand / Money / System / Freedom), nhưng **kiểm soát ý định** ở 4 tầng trust-building (Context / Insight / Belief Shift / Small Action). Cụm theo logic narrative arc audience dễ theo.

### 1.3 Vai trò của D1–D15 v1

D1–D15 v1 **không xoá**, **không move trong bước này**. Dùng làm:

- **Voice samples**: cách Chị Hiền nói thật ở tầng nội tâm (D1, D6, D8, D9)
- **Audit history**: 5 lần polish v1 chứng minh các pattern fail (vd "chắc không ai đỡ kịp" → lửng củng; "Có một kiểu mệt..." → AI tone)
- **Expression samples**: các câu neo đã pass review nhiều lần (*"Cuối cùng vẫn phải là mình thôi"*, *"Mình buông ra thì mọi thứ sẽ rối"*, *"Bạn hay hỏi người khác cần gì..."*)
- **Failure examples**: hook bị flag "Sai stage", cấu trúc lặp pattern → training negative cho app

D1–D15 v1 KHÔNG dùng làm **hard calendar** cho v2. V2 không kế thừa thứ tự / topic / hook của v1.

---

## 2. Core Principle

> **"Chủ đề được mở. Ý định của bài bị kiểm soát."**

### 2.1 Chủ đề được mở

30 bài đầu được phép nói về:

- Kinh doanh
- Marketing
- Fanpage
- Content
- Xây thương hiệu cá nhân
- Thị trường 2026
- Khách hàng thay đổi
- Dòng tiền / cảm giác an toàn
- Hình ảnh cá nhân
- Gia đình
- Nội tâm
- Nghỉ ngơi
- Thói quen gồng
- Tự do
- Hệ thống nhẹ
- Thiền định / quan sát nội tâm

### 2.2 Ý định bị kiểm soát — chỉ ở 4 tầng

| Tầng | Định nghĩa | Ví dụ |
|---|---|---|
| **Context** | Bối cảnh — gọi tên thay đổi của thị trường, hành vi, môi trường | *"Người mua 2026 đã thay đổi cách quyết định mua."* |
| **Insight** | Gọi tên cơ chế / điều người đọc đang mắc / mệt / kẹt | *"Bạn không thiếu năng lực — bạn thiếu rõ ràng về chính mình."* |
| **Belief Shift** | Đổi cách nhìn về 1 từ / khái niệm / hành vi | *"Hệ thống không phải để kiểm soát hơn — là để bớt gồng."* |
| **Small Action** | 1 bước nhỏ ≤ 5 phút, hướng nội, audience làm được hôm nay | *"Hỏi mình: việc đầu tiên hôm nay là việc của ai?"* |

### 2.3 KHÔNG nói ở tầng

- **Sales / Offer / Pitch**: không bán khoá, sản phẩm, chương trình
- **Inbox / Lead magnet**: không kéo inbox, không cho gì để nhận resource
- **Funnel / Pricing tutorial**: không dạy cách bán, dựng pipeline
- **Automation / System tutorial sâu**: không demo Zapier / Make / Notion / chatbot
- **Cam kết kết quả**: không hứa "trong 30 ngày bạn sẽ..."
- **Case study phóng đại**: không "khách của tôi tăng X% sau Y tháng"
- **Business mechanics quá sâu**: không bóc tách P&L, conversion rate, CAC/LTV

---

## 3. Global Constraints — 30 bài đầu

| # | Constraint | Áp ở | Hệ quả nếu vi phạm |
|---|---|---|---|
| 1 | Không Sales/Offer pattern (P25 trong Hook Pattern Bank) | Toàn bộ 30 bài | App reject |
| 2 | Không CTA inbox / tư vấn / lead magnet / mua ngay / scarcity | CTA mọi bài | App reject |
| 3 | Không bịa trải nghiệm cá nhân Chị Hiền | Toàn bộ | App reject — chỉ dùng quan sát chung |
| 4 | Không hook/mở bài family *"Có một..."* / *"Có những..."* | Câu hook + câu mở bài | App reject (write_rules v2.3 III.2.b) |
| 5 | Câu phải thuận miệng tiếng Việt | Hook / câu neo / CTA / cảm xúc mạnh | App flag REVIEW |
| 6 | Không quá nhiều câu ngắn / caption hoá | Body | Brand owner check |
| 7 | Văn xuôi có dòng chảy tự nhiên | Body | Brand owner check |
| 8 | Mỗi bài 1 insight chính | Spec bài | App reject nếu detect >1 insight |
| 9 | Insight thật thắng topic | Spec bài | Nếu insight yếu → topic phải đổi |
| 10 | Voice 5 chất: Ấm / Rõ / Đẹp / Sâu / Vững / Thực tế | Toàn bộ | Brand owner audit |
| 11 | Expression Bank chỉ polish, không copy máy móc | Bước Language Polish | App flag nếu match cụm bank >2 lần |

---

## 4. 6-Cluster Narrative Arc

### Cluster A — Market Reality (D1–D5)

| Field | Value |
|---|---|
| **Role** | Mở bằng *bối cảnh ngoài* trước khi soi *bên trong*. Hạ phòng thủ. Audience dễ nhận "thị trường đã đổi" hơn "bạn thiếu rõ ràng". |
| **Allowed topics** | Người mua thay đổi · content thật vs nhiều · sự chú ý ngắn · quyền lực mua · 1 câu thật |
| **Allowed depth** | Quan sát thị trường + hành vi cụ thể của khách (vd: lướt qua quảng cáo trong 1s, đọc 5 comment trước khi inbox) |
| **Not allowed** | Strategy bán hàng · funnel · ad copy · SEO · tutorial độ dài bài · tutorial hook viral · pricing · objection handling · copywriting framework |
| **Risk flags** | Drift sang "cách viết content bán" · "kỹ thuật viết content" · "bán bằng nói thật" bị hiểu như tactic mới · Slogan-y nếu không có cảnh thật |

---

### Cluster B — Self-Worth của người phụ nữ trong kinh doanh (D6–D10)

| Field | Value |
|---|---|
| **Role** | Bridge từ Market sang người làm nghề. Sau khi audience đồng ý "thị trường đã đổi", chuyển sang *"vậy mình ở đâu trong cái đổi đó?"*. |
| **Allowed topics** | Năng lực vs rõ ràng · chuyên môn thật vs cách nói · càng học càng rối · không cần trở thành người khác · Caregiver/Guide identity nhẹ |
| **Allowed depth** | Quan sát 5 năm chuyên môn vs 5 phút giới thiệu mình · tách "giỏi nghề" khỏi "giỏi nói về nghề" · cost của học không bù self-clarity |
| **Not allowed** | Personal branding template · Personal branding tutorial · recommend course / book · slogan "yêu bản thân" · bịa trải nghiệm cá nhân của Chị Hiền |
| **Risk flags** | Quá self-help nếu không có "bạn" cụ thể · "anti-education" nếu sắc quá · Sáo nếu không có chi tiết · Bịa câu chuyện cá nhân |

---

### Cluster C — Content / Fanpage / Thương hiệu cá nhân (D11–D15)

| Field | Value |
|---|---|
| **Role** | Audience đã rõ về mình → nói về "mình thể hiện ra như thế nào". Không tutorial xây fanpage — nói về **cách audience nhìn brand của mình**. |
| **Allowed topics** | Fanpage là nơi audience hiểu mình · bài đầu tiên thật vs hay nhất · xây kênh vs biểu diễn · audience follow lý do gì · view nhiều vs đúng người |
| **Allowed depth** | Tầng nhận diện brand · phân biệt 2 mode · mirror principle · phân biệt reach vs fit |
| **Not allowed** | Tutorial post frequency · editorial calendar tutorial · "algorithm hack" · phân tích insights kỹ thuật · "viral content" tactic |
| **Risk flags** | Drift sang "post strategy" · khuyến khích "đăng đại" nếu không neo "thật" · câu hỏi gắt nếu không có Caregiver tone · "niche down tactic" misread |

---

### Cluster D — Money Safety / Dòng tiền / Cảm giác an toàn (D16–D20)

| Field | Value |
|---|---|
| **Role** | Sau brand → thu nhập. Không tutorial tài chính — nói về **cảm giác mất an toàn** và quan hệ với tiền. **Đây là cụm rủi ro cao nhất** — drift sang "làm giàu" rất dễ. |
| **Allowed topics** | Tiền là quyền chọn · self-worth & income ceiling · bấp bênh không hết khi thu nhập tăng · 1 tháng không lo tiền · tiền không cứu cảm giác đủ |
| **Allowed depth** | Cảm giác tự do qua thu nhập · Income mirror self-image · tách thu nhập khỏi cảm giác an toàn · câu hỏi nhìn lại · tách 2 layer (giải quyết việc / cảm giác) |
| **Not allowed** | Pricing · số tiền cụ thể · hứa "tăng thu nhập" · tutorial financial planning · pitch giải pháp · "tiền không quan trọng" sai narrative · "làm giàu nhanh" tone |
| **Risk flags** | "Làm giàu nhanh" risk · Self-help cliché · "Chống lại làm giàu" misread · Triggering nếu không có Caregiver · Quá triết lý |

---

### Cluster E — System / Cấu trúc nhẹ / Không gồng (D21–D25)

| Field | Value |
|---|---|
| **Role** | Money đi cùng System — không gồng được nữa thì cần cấu trúc. Vẫn ở tầng tư duy hệ thống, không demo tool. Phòng "khoe công nghệ" rất chặt. |
| **Allowed topics** | Cấu trúc thay sức người · hệ thống ≠ kiểm soát hơn · việc lặp 3 lần = hệ thống nhỏ · automation = khoảng trống · hệ thống tốt là cái quên đi vẫn chạy |
| **Allowed depth** | Mở khái niệm "cấu trúc" · Caregiver tone bắt buộc · khái niệm seed system · automation = freedom · definition tinh ở D25 đóng cụm |
| **Not allowed** | Demo tool / SaaS · Tutorial Notion / Trello / Asana · "đây là cách dùng tool X" · Demo chatbot / Zapier flow · Hứa "30 ngày tự động hoá" |
| **Risk flags** | "Khoe tool" risk · Quá technical nếu drift · "Process porn" · "Khoe công nghệ" · Vision quá ở D25 |

---

### Cluster F — Freedom / Identity / Bền vững (D26–D30)

| Field | Value |
|---|---|
| **Role** | Đóng phase trust-building bằng vision dài hạn. Mở identity *"bạn xứng đáng có công việc bạn sống cùng được lâu dài"*. **Chuẩn bị audience** cho phase Sales sau D30, nhưng D26–D30 **không pitch**. |
| **Allowed topics** | Tự do = quyền chọn việc nào trước · công việc sống cùng được lâu · nhỏ mà thật cũng đẹp · phiên bản tin được nhiều hơn · không cần trở thành ai khác |
| **Allowed depth** | Identity choice · Vision sustainable work · Permission để chọn nhỏ · Vision Future Self · câu neo brand đóng phase |
| **Not allowed** | "Quit your job" narrative · Pitch coaching · Pitch chương trình tiếp theo · Anti-scale extreme · Hứa "trong 30 ngày bạn sẽ..." · Mở pitch sale ngay sau D30 |
| **Risk flags** | Sáo · Pitch-y nếu không neo vào hành vi · Triggering với người tham vọng · "Vision board" cliché · Mất trust nếu pitch sale ngay sau D30 |

---

## 5. 30-Day Table

> **Cột giải thích**:
> - **Intent**: 1 trong 4 (Context / Insight / Belief Shift / Small Action)
> - **Allowed Depth**: bài được phép đào sâu đến đâu
> - **Not Allowed**: ranh đỏ cụ thể của bài
> - **Hook Direction**: hint pattern, không phải hook full (để app generate)
> - **Risk Flag**: rủi ro app cần check trước khi pass

### Cluster A — Market Reality

| Day | Topic | Angle | Core Insight | Intent | Allowed Depth | Not Allowed | Hook Direction | Small Action | Risk |
|---|---|---|---|---|---|---|---|---|---|
| **D1** | Người mua thay đổi | Belief về niềm tin của khách | Người mua 2026 không tin pitch — họ tin sự thật được nói tử tế | Context | Quan sát thị trường + 1 hành vi cụ thể (vd lướt qua quảng cáo trong 1s) | Strategy bán hàng / funnel / ad copy | Behavior shift: *"Khách của bạn đã đổi cách quyết định mua. Bạn đã đổi cách nói chưa?"* | Đọc 5 comment thật trên 1 fanpage cùng ngành — không phán xét | Drift sang "cách viết content bán" |
| **D2** | Content thật vs content nhiều | Re-frame "đăng đều" | Audience không cần thêm content. Họ cần content thật. | Belief Shift | Cảm giác fatigue khi xem content template | Tutorial cách viết hook viral | Truth Layering: *"Bạn không thiếu nội dung để đăng. Bạn thiếu một câu thật để bắt đầu."* | Đọc lại bài đăng cuối — câu nào là thật của bạn, câu nào là copy template? | Drift sang "kỹ thuật viết content" |
| **D3** | Sự chú ý ngắn lại | Bối cảnh consume content | Người ta lướt nhanh hơn, ở lại ít hơn — không cần dài, cần có lực | Context | Quan sát hành vi đời thường (lướt feed bữa sáng) | Tutorial độ dài bài / SEO | Question: *"Bài đăng cuối của bạn — bạn có đọc lại nó không?"* | 30 giây đọc lại 1 bài cũ của mình, đo cảm giác | Quá technical |
| **D4** | Khách tự research trước khi mua | Belief về quyền lực mua | Khách hôm nay biết nhiều hơn bạn nghĩ. Bán bằng pitch là đứng sai vai. | Belief Shift | Quan sát: khách hỏi 5 câu trước khi inbox lần đầu | Pricing strategy / objection handling | Behavior Mirror: *"Bạn vẫn đang chuẩn bị câu chốt sale. Khách của bạn đã chuẩn bị 5 câu hỏi."* | Liệt kê 3 câu khách hay hỏi mình — không trả lời, chỉ liệt kê | "Bán bằng nói thật" có thể bị hiểu như tactic mới |
| **D5** | 1 câu thật bằng 100 câu hay | Câu neo cụm A | Một câu thật dừng người ta lại lâu hơn 100 câu hay | Insight | Mở khái niệm "câu thật" — không định nghĩa cứng | Copywriting framework | Truth Layering: *"Bạn không cần viết hay hơn. Bạn cần viết thật hơn."* | Viết 1 câu thật về việc mình đang làm — không cần đăng | Slogan-y nếu không có cảnh thật đi kèm |

### Cluster B — Self-Worth của người phụ nữ trong kinh doanh

| Day | Topic | Angle | Core Insight | Intent | Allowed Depth | Not Allowed | Hook Direction | Small Action | Risk |
|---|---|---|---|---|---|---|---|---|---|
| **D6** | Năng lực vs rõ ràng | False Lack | Bạn không thiếu năng lực — bạn thiếu rõ ràng về chính mình | Insight | 5 năm chuyên môn vs 5 phút giới thiệu mình | Personal branding template | False Lack: *"Bạn không thiếu năng lực. Bạn thiếu một câu rõ về điều mình đang làm."* | Viết 1 câu giới thiệu mình — không cần dài | Quá self-help nếu không có "bạn" cụ thể |
| **D7** | Chuyên môn thật vs cách nói chưa rõ | Re-frame "kém marketing" | Chuyên môn của bạn thật. Cách bạn nói về nó chưa rõ. | Belief Shift | Tách "giỏi nghề" khỏi "giỏi nói về nghề" | Personal branding tutorial | Re-frame: *"Bạn nghĩ bạn cần học marketing. Có khi bạn cần học nói về điều mình đã làm."* | Kể lại 1 việc đã làm cho khách — bằng giọng đời, không slide | Drift sang storytelling framework |
| **D8** | Càng học càng rối | Hidden Cost của học không bù self-clarity | Học nhiều không bù được việc chưa biết mình là ai | Insight | Phân biệt: kiến thức bù lỗ hổng kỹ năng vs kiến thức làm rối khi chưa biết mình | Recommend course / book | Hidden Cost: *"Mỗi khoá học bạn nhận thêm khi đầu chưa rõ — là một lớp rối mới."* | Liệt kê 3 khoá đã học — bao nhiêu cái thực sự áp dụng? | "Anti-education" nếu sắc quá |
| **D9** | Không cần trở thành phiên bản khác | Permission | Bạn không cần trở thành ai khác để bắt đầu | Belief Shift | Identity hiện tại được phép | Slogan "yêu bản thân" | Permission: *"Bạn không cần đổi tính cách để bán được hàng."* | Viết 3 việc bạn làm tự nhiên mà mọi người hay nhận xét | Sáo nếu không có chi tiết |
| **D10** | "Mình từng ở chỗ bạn" — Caregiver | Identity của Guide | Người đã đi qua một đoạn — đứng cạnh, không đứng trên | Context | Vai Guide rất nhẹ — không bịa life story | Bịa trải nghiệm cụ thể của Chị Hiền | In Medias Res: *"Có lúc mình cũng làm rất nhiều — và cũng rối."* | Hỏi mình *"mình muốn dẫn ai đi từ đâu đến đâu?"* | Bịa câu chuyện cá nhân |

### Cluster C — Content / Fanpage / Thương hiệu cá nhân

| Day | Topic | Angle | Core Insight | Intent | Allowed Depth | Not Allowed | Hook Direction | Small Action | Risk |
|---|---|---|---|---|---|---|---|---|---|
| **D11** | Fanpage là gì với audience | Re-frame chức năng | Fanpage không phải nơi đăng nhiều — là nơi audience hiểu rõ bạn là ai | Belief Shift | Tầng nhận diện brand | Tutorial post frequency | Re-frame: *"Bạn nghĩ fanpage là kênh bán. Khách của bạn xem fanpage để biết bạn là ai."* | Đọc 5 bài cũ — audience hiểu mình là ai sau khi đọc? | Drift sang "post strategy" |
| **D12** | Bài đầu tiên thật vs hay nhất | Permission để đăng thật | Bài đầu tiên không phải bài hay nhất — là bài thật nhất | Belief Shift | Cho phép bắt đầu chưa hoàn hảo | Editorial calendar tutorial | Truth Layering: *"Bạn đang đợi bài viết hoàn hảo. Audience đang đợi một câu thật."* | Viết 1 câu mở bài bằng giọng nói chuyện | Khuyến khích "đăng đại" nếu không neo "thật" |
| **D13** | Xây kênh vs biểu diễn | Question Identity | Bạn đang xây kênh hay đang biểu diễn? | Insight | Phân biệt 2 mode | Phán xét người đang biểu diễn | Question: *"Bạn đang viết để được hiểu — hay để được khen?"* | 5 phút nhìn lại 3 bài cuối — bài nào nói cho khách, bài nào nói cho ego? | Câu hỏi gắt nếu không có Caregiver |
| **D14** | Audience follow ai | Belief về lý do follow | Audience không follow vì bạn giỏi — họ follow vì họ thấy mình trong bạn | Insight | Mirror principle | "Algorithm hack" | Belief Flip: *"Bạn đang cố làm content để người ta thấy bạn giỏi. Họ ở lại vì thấy chính họ trong bạn."* | Đọc 3 comment chân thật nhất từng nhận — họ thấy gì trong bạn? | Drift sang "viral content" |
| **D15** | View nhiều vs đúng người | Re-frame metric | 1 content kéo lượt view không bằng 1 content kéo đúng người | Belief Shift | Phân biệt reach vs fit | Phân tích insights kỹ thuật | Truth Layering: *"View nhiều không cứu được bạn. Đúng người mới cứu được."* | Gọi tên 1 người audience cụ thể bạn muốn đọc bài tiếp theo | "Niche down tactic" misread |

### Cluster D — Money Safety / Dòng tiền / Cảm giác an toàn

| Day | Topic | Angle | Core Insight | Intent | Allowed Depth | Not Allowed | Hook Direction | Small Action | Risk |
|---|---|---|---|---|---|---|---|---|---|
| **D16** | Tiền là quyền chọn | Re-frame Money | Tiền không phải là con số — là quyền chọn | Belief Shift | Cảm giác tự do qua thu nhập | Pricing / số tiền cụ thể | Re-frame: *"Bạn không thiếu tiền. Bạn thiếu cảm giác mình có quyền chọn."* | Viết 3 việc bạn muốn từ chối tuần này nếu có quyền chọn | "Làm giàu nhanh" |
| **D17** | Self-worth & income ceiling | Belief về xứng đáng | Bạn không nghèo — bạn chỉ chưa thấy mình xứng đáng hơn | Insight | Income mirror self-image | Hứa "tăng thu nhập" | Self-Worth: *"Thu nhập của bạn hiếm khi vượt quá hình ảnh bạn thấy về mình."* | Hỏi *"mình đang giới thiệu mình bằng cụm gì? Cụm đó có khớp giá trị mình muốn nhận không?"* | Self-help cliché |
| **D18** | Bấp bênh không tự biến mất | Pain | Cảm giác bấp bênh không tự biến mất khi thu nhập tăng | Insight | Tách thu nhập khỏi cảm giác an toàn | Tutorial financial planning | Pain: *"Bạn nghĩ thêm 10 triệu sẽ hết lo. 10 triệu đó đã đến — và bạn vẫn lo."* | Liệt kê 3 nỗi lo về tiền — bao nhiêu cái sẽ hết nếu thu nhập gấp đôi? | "Chống lại làm giàu" misread |
| **D19** | Một tháng không lo tiền | Time Question | Bao lâu rồi bạn chưa có 1 tháng không lo tiền? | Pain | Câu hỏi nhìn lại — không pitch giải pháp | "Mình có giải pháp" | Time Pressure: *"Bao lâu rồi bạn chưa có 1 buổi sáng mở mắt mà không nghĩ về tiền?"* | Hỏi mình *"cảm giác đó trông sẽ như thế nào trong đời mình?"* | Triggering nếu không có Caregiver |
| **D20** | Tiền không cứu cảm giác đủ | Belief Layer | Tiền cứu việc, không cứu cảm giác đủ | Insight | Tách 2 layer (giải quyết việc / cảm giác) | "Tiền không quan trọng" sai narrative | Truth Layering: *"Bạn không sai khi muốn nhiều tiền hơn. Chỉ là tiền sẽ không cho bạn cảm giác đủ — cảm giác đó bạn phải tự xây."* | Viết 1 câu định nghĩa "đủ" của riêng bạn — không phải con số | Quá triết lý |

### Cluster E — System / Cấu trúc nhẹ / Không gồng

| Day | Topic | Angle | Core Insight | Intent | Allowed Depth | Not Allowed | Hook Direction | Small Action | Risk |
|---|---|---|---|---|---|---|---|---|---|
| **D21** | Cấu trúc thay sức người | False Lack | Bạn không thiếu công cụ — bạn thiếu cấu trúc nhẹ | Insight | Mở khái niệm "cấu trúc" — không demo tool | Demo tool / SaaS | False Lack: *"Bạn không thiếu app quản lý. Bạn thiếu một cấu trúc gọn 3 bước."* | Liệt kê 3 việc bạn làm lặp lại mỗi tuần — chưa cần sửa | "Khoe tool" |
| **D22** | Hệ thống ≠ kiểm soát hơn | Re-frame System | Hệ thống không phải để kiểm soát hơn — là để bớt gồng | Belief Shift | Caregiver tone bắt buộc | Tutorial Notion / Trello / Asana | Re-frame: *"Bạn nghĩ hệ thống là kiểm soát thêm. Hệ thống thật là cách bạn không phải gồng mọi thứ bằng sức người."* | Hỏi *"việc nào tuần này tôi đang làm bằng sức, có thể chuyển thành quy trình 3 bước?"* | Quá technical |
| **D23** | Việc làm 3 lần = hệ thống nhỏ | Small Action principle | Một việc bạn làm 3 lần là hệ thống nhỏ đầu tiên | Belief Shift | Khái niệm seed system | "Đây là cách dùng tool X" | Insight: *"Lần thứ 3 bạn làm cùng một việc — nó không còn là việc, nó là quy trình bạn chưa viết xuống."* | Viết 3 bước cho 1 việc bạn làm 3 lần tuần này | "Process porn" |
| **D24** | Automation = khoảng trống | Re-frame Automation | Tự động hoá không phải để khoe — là để có khoảng trống cho đời sống | Belief Shift | Khái niệm automation = freedom | Demo chatbot / Zapier flow | Re-frame: *"Bạn nghĩ automation là cho người giỏi tech. Automation thật là cách bạn lấy lại 30 phút mỗi tối."* | Liệt kê 1 việc 30 phút mỗi tối — có thể giảm xuống 5 phút không? | "Khoe công nghệ" |
| **D25** | Hệ thống tốt là cái quên đi vẫn chạy | Identity của Sage | Cấu trúc tốt là cái bạn quên đi vẫn chạy được | Insight | Đóng cụm E bằng definition tinh | Hứa "30 ngày tự động hoá" | Truth Layering: *"Bạn nghĩ làm việc tốt là làm nhiều. Có khi làm việc tốt là việc bạn đã làm hôm qua, hôm nay vẫn chạy mà bạn không phải động vào."* | Hỏi *"hôm nay tôi không làm gì, có việc nào của tôi vẫn chạy?"* | Vision quá |

### Cluster F — Freedom / Identity / Bền vững

| Day | Topic | Angle | Core Insight | Intent | Allowed Depth | Not Allowed | Hook Direction | Small Action | Risk |
|---|---|---|---|---|---|---|---|---|---|
| **D26** | Tự do = quyền chọn việc nào trước | Re-frame Freedom | Tự do không phải là không làm việc — là quyền chọn việc nào trước | Belief Shift | Identity choice | "Quit your job" narrative | Re-frame: *"Tự do không phải nghỉ làm. Là quyền chọn việc nào đến lượt trước."* | Liệt kê việc đầu tiên của ngày mai — bạn chọn, hay người khác chọn? | Sáo |
| **D27** | Công việc sống cùng được lâu | Vision identity | Bạn xứng đáng có công việc bạn sống cùng được lâu dài | Belief Shift | Vision sustainable work | Pitch coaching | Permission: *"Bạn không cần một công việc giàu nhanh. Bạn xứng đáng một công việc bạn sống cùng được lâu dài."* | Hỏi *"công việc tôi muốn làm 5 năm nữa — có giống công việc tôi đang làm không?"* | Pitch-y nếu không neo vào hành vi |
| **D28** | Nhỏ mà thật cũng đẹp | Permission để chọn nhỏ | Không phải ai làm cũng cần làm to. Nhỏ mà thật cũng là công việc đẹp. | Belief Shift | Counter "scale" narrative | Anti-scale extreme | Truth Layering: *"Bạn không cần xây đế chế. Bạn được phép chọn nhỏ — nếu nhỏ là cái thật của bạn."* | Hỏi *"mình muốn làm to — vì muốn, hay vì sợ bị xem là kém?"* | Triggering với người tham vọng |
| **D29** | Phiên bản tin được nhiều hơn | Future Self | Phiên bản nhẹ hơn của bạn — không giỏi hơn, mà tin được nhiều hơn | Belief Shift | Vision Future Self | Hứa "trong 30 ngày bạn sẽ..." | Future Self: *"Phiên bản 1 năm nữa của bạn — không giỏi hơn nhiều. Chỉ là tin được nhiều hơn."* | Viết 1 câu phiên bản đó nói với mình hôm nay | "Vision board" cliché |
| **D30** | Bạn không cần trở thành ai khác | Câu neo signature đóng phase | Bạn không cần trở thành ai khác để bắt đầu | Belief Shift | Câu neo brand | Pitch chương trình tiếp theo | Permission: *"Bạn không cần trở thành ai khác để bắt đầu. Bạn chỉ cần bắt đầu — bằng đúng người bạn đang là."* | Đọc lại 1 trong 30 bài qua — bài nào chạm bạn nhất? | Mở pitch sale ngay sau D30 → mất trust |

---

## 6. App Generation Rules — 10 nguyên tắc

| # | Rule | Cách app check |
|---|---|---|
| **1** | **Topic flexible, intent constrained** | App pick topic từ list section 2.1, nhưng intent phải = 1 trong 4 (Context / Insight / Belief Shift / Small Action). Không cho phép intent = "How to" / "Pitch" / "Buy". |
| **2** | **One insight per post** | Detect số lượng insight statement trong body. Nếu >1 main insight → reject + flag tách 2 bài. |
| **3** | **Business topic must return to lived experience** | Topic kinh doanh / marketing / brand / money / system phải có ≥1 chi tiết cảm quan đời thường (cuộc gọi, comment khách, bài đăng cũ, buổi sáng mở laptop). App scan: nếu không có → flag REVIEW. |
| **4** | **Marketing topic must explain context before technique** | Bài về marketing / fanpage / brand không được pitch *"tôi giúp bạn / inbox tôi / chương trình của tôi"*. App scan banned phrases. Nếu match → reject. |
| **5** | **No offer in first 30 days** | Scan: "đăng ký", "inbox", "chỉ còn", "ưu đãi", "khoá học", "chương trình của mình", "sản phẩm của mình", "nhận tài liệu", giá cụ thể (số + đồng/triệu/k). Nếu match → reject. |
| **6** | **Vietnamese Naturalness gate** | Áp write_rules v2.2 II.5. App phải tự generate hook, đọc to, check 3 yếu tố: có "bạn"/"mình", có cảnh cụ thể, có khẩu cảm Việt. Nếu thiếu → flag REVIEW. |
| **7** | **Longer Flow Style gate** | Body phải có dòng chảy văn xuôi, không chỉ câu ngắn xen kẽ. Nếu trung bình câu < 8 chữ trên toàn bài → flag REVIEW. Nếu trung bình câu < 5 chữ → reject (caption hoá). |
| **8** | **Hook family blacklist gate** | Áp write_rules v2.3 III.2. Câu hook KHÔNG bắt đầu bằng: *"Có một..."* / *"Có những..."* / *"Trong cuộc sống..."* / *"Như chúng ta đã biết..."* / *"Hôm nay mình muốn chia sẻ..."* / *"Xin chào..."*. Nếu match → reject. |
| **9** | **Cluster milestone approval gate** | App KHÔNG sinh cụm tiếp theo nếu cụm trước chưa có milestone "approved" từ brand owner. Xem section 7. |
| **10** | **Expression Bank polish, not copy** | Áp Expression Bank v1 ở bước Language Polish. Nếu hook hoặc câu neo trùng nguyên văn cụm trong Anchor Sentence Bank → flag REVIEW (cho phép biến thể, không cho phép copy). |

---

## 7. Milestone Approval Workflow

> **Nguyên tắc**: KHÔNG để app sinh D1–D30 một mạch. Mỗi cụm 5 ngày = 1 milestone duyệt.

### 7.1 Quy trình mỗi cụm (lặp 6 lần)

```
Step 1 — App generates 5 insight options × 5 days = 25 insight candidates
       ↓
Step 2 — Brand owner approves 5 core insights (1 per day)
       ↓ [GATE: cần approve trước khi tiếp]
Step 3 — App generates 5 hook options per day (25 hooks)
       ↓
Step 4 — Brand owner / reviewer approves 1 hook per day
       ↓ [GATE: cần approve trước khi tiếp]
Step 5 — App generates 5 full drafts (Long FB Post format default)
       ↓
Step 6 — Audit gate: stage / voice / Vietnamese Naturalness / cluster constraints
       ↓ [GATE: nếu fail audit → loop back to Step 5]
Step 7 — Brand owner final approval (ký FINAL)
       ↓
Step 8 — Save 5 bài FINAL → unlock cluster tiếp theo
```

### 7.2 Quy tắc gate

| Gate | Yêu cầu để pass |
|---|---|
| **Insight gate** | 5/5 insight được brand owner approve. Không pass nếu chỉ 4/5 — phải sinh lại insight thứ 5. |
| **Hook gate** | 5/5 hook approved. Không lặp pattern (tối đa 1 cấu trúc xuất hiện 1 lần / 5 ngày / cụm). |
| **Audit gate** | Bài pass cả 10 App Generation Rules. Nếu fail 1+ rule → loop về Step 5 viết lại bài đó. |
| **Final gate** | Brand owner đọc 5 bài, ký FINAL. Cụm tiếp theo unlock. Không pass nếu brand owner flag ≥ 2 bài cần rewrite — phải rework cụm. |

### 7.3 Vai trò 3 bên

| Vai trò | Trách nhiệm |
|---|---|
| **App** | Generate insight / hook / draft. Tự audit qua 10 rules. Báo cáo flag, không tự pass. |
| **Reviewer** (anh Tuấn / nhân viên) | Audit kỹ thuật trước khi đưa brand owner: stage fit, naturalness, cluster constraints, không lặp pattern, không offer / pitch. |
| **Brand owner** (Chị Hiền) | Audit voice + insight + đời sống thật. Quyết duyệt / yêu cầu sửa / yêu cầu rewrite. Quyết unlock cụm tiếp theo. |

---

## 8. How to Use v1 Prototype

### 8.1 Mục đích sử dụng D1–D15 v1

| Use case | Cách dùng |
|---|---|
| **Voice samples** | Đọc D1, D6, D8, D9 — cách Chị Hiền nói thật ở tầng nội tâm. Lấy nhịp, không lấy nội dung. |
| **Audit history** | Đọc revision history của D9 (v1 → v1.1 → v1.2) và D15 (v1 → v1.1 → v1.2) — học các pattern fail (lửng củng / "Có một..." AI tone). |
| **Expression samples** | Trích các câu neo đã pass review nhiều lần làm reference. Có thể tái dùng trong v2 nếu khớp insight, không copy nguyên văn vào hook. |
| **Failure examples** | Hook bị flag "Sai stage" trong các bài cũ + cụm "không ai đỡ kịp" v1.1 → training negative cho app. |
| **Prototype learnings** | 7 lessons rút ra: (1) insight càng đời càng chạm, (2) hook đọc to là test cuối, (3) action ≤ 5 phút mới làm được, (4) family "Có một..." dễ thành AI, (5) nhịp 3 vế lặp nhiều bài thành công thức, (6) câu thừa nhận lớp bề mặt giảm phòng thủ, (7) bài kết stage cần câu neo mạnh. |

### 8.2 KHÔNG được dùng v1 prototype làm

- ❌ Hard calendar cho v2 (v2 có cluster + day map riêng — không kế thừa thứ tự v1)
- ❌ Topic source cho v2 (v2 mở rộng sang Market / Money / System / Brand — không bó như v1)
- ❌ Hook copy paste vào v2 (mỗi v2 hook phải sinh mới theo cluster spec)
- ❌ Action copy paste (action v2 phải khác action v1, không lặp "dừng 30s" / "1 câu hỏi giữa ngày" / "5 phút cuối ngày")

### 8.3 Vị trí lưu v1

D1–D15 v1 hiện ở: `output/kinh-doanh-27-45/4-thực-thi/week-XX-DXX-FINAL-chi-hien.md` và `week-XX-DXX-DRAFT-chi-hien.md`.

Bước tiếp theo (sau khi strategy v2 được duyệt) sẽ move sang `output/kinh-doanh-27-45/_prototype/` để tách rõ với v2 production. **Không move trong bước này.**

---

## 9. Files to Update Later

> Các file dưới đây **chưa update trong bước này**. Đề xuất update sau khi strategy v2 được duyệt + bắt đầu sinh insight options cụm A.

| File | Action đề xuất | Mức ưu tiên | Khi nào update |
|---|---|---|---|
| `README.md` (root) | Update mục 2.6 / changelog → trỏ sang strategy v2; ghi rõ D1–D15 cũ là prototype | HIGH | Ngay sau khi strategy v2 được duyệt |
| `docs/writing_methods/language_bank/chi_hien_hook_pattern_bank_v1.md` | Update **section 7** (How to use for D8–D30) → đổi sang **6-cluster v2 mapping** với pattern ưu tiên cho mỗi cluster | HIGH | Trước khi sinh hook cho cluster A |
| `output/kinh-doanh-27-45/_prototype/` (folder mới) | Move D1–D15 v1 vào, thêm `README.md` giải thích vai trò prototype | MEDIUM | Trước khi sinh D1 v2 |
| `docs/strategy/chi_hien_30day_content_strategy_v2.md` (file này) | Bump version v2.0 → v2.1 nếu có chỉnh strategy sau audit | LOW | Khi cần |
| (Tạo mới) `docs/strategy/chi_hien_30day_strategy_config.json` | Spec dạng JSON cho app dễ parse — nếu app cần config machine-readable | OPTIONAL | Khi app được code phần content generation |
| `docs/writing_methods/chi_hien_content_formula_v1.md` | **Không cần update** — formula 7 bước vẫn áp được v2 | — | — |
| `profiles/chi-hien/write_rules.md` | **Không cần update** — rules v2.3 đã đủ guardrails | — | — |
| `docs/writing_methods/language_bank/chi_hien_expression_bank_v1.md` | **Có thể update** sau cluster A đầu tiên — bổ sung Anchor / Contrast Pair nếu phát hiện cụm mới phù hợp Market / Money / System | LOW | Sau cluster A |

---

## 10. Next Step

> Sau khi file này được duyệt:

### 10.1 Việc bắt buộc (gate)

1. **Brand owner đọc strategy v2 này** và xác nhận:
   - 6 cụm có đúng narrative arc cho audience không?
   - Allowed Depth của từng cụm có đúng giới hạn không?
   - 10 App Generation Rules có đủ chặt không, hay cần thêm?
   - Bảng 30 ngày có đúng topic / insight không?
2. **Brand owner ký approval** strategy v2 → unlock bước sinh insight cluster A.

### 10.2 Việc làm ngay sau approval

1. **Sinh insight options cho Cluster A (D1–D5)** — 5 insight options × 5 days = **25 insight candidates** trước.
2. **KHÔNG sinh hook ngay**. KHÔNG sinh bài ngay.
3. Brand owner duyệt **5 core insights** (1 cho mỗi D1–D5) → mới sinh hook.

### 10.3 Việc KHÔNG làm trong bước này

- ❌ KHÔNG sinh D1–D5 ngay
- ❌ KHÔNG sinh insight cho cluster B–F (chờ cluster A xong)
- ❌ KHÔNG move D1–D15 v1 vào `_prototype/` (chờ approval)
- ❌ KHÔNG update README / Hook Pattern Bank / Expression Bank trong bước này
- ❌ KHÔNG sinh content config JSON cho app (chờ app team confirm cần format gì)

---

## 11. Summary cho brand owner đọc nhanh

| Câu hỏi | Trả lời |
|---|---|
| **30 bài đầu có nói về kinh doanh / marketing / fanpage / tiền không?** | **Có** — mở rộng so với v1. Nhưng chỉ ở 4 tầng: Context / Insight / Belief Shift / Small Action. Không pitch, không tutorial sâu. |
| **30 bài đầu có pitch sản phẩm / khoá / coaching không?** | **Không**. Tuyệt đối không. Có 11 Global Constraints chặn việc này. |
| **D1–D15 v1 cũ có bị xoá không?** | **Không**. Giữ làm prototype / training samples. Sẽ move sang `_prototype/` sau khi v2 được duyệt — không xoá. |
| **App sinh tự động được không?** | **Không sinh tự động một mạch**. Có 6 milestone duyệt (1/cluster). App generate, brand owner duyệt từng bước. |
| **Bao giờ bắt đầu sinh D1 v2?** | Sau khi: (1) strategy v2 này được duyệt, (2) sinh 25 insight options cho cluster A, (3) brand owner duyệt 5 core insights, (4) sinh hook, (5) brand owner duyệt hook → mới sinh body D1. |
| **Phase Sales bắt đầu khi nào?** | **Sau D30**. D26–D30 (cluster F) đóng phase trust-building bằng vision dài hạn — KHÔNG pitch. Sale bắt đầu D31+ với strategy riêng. |

---

**Generated**: 2026-05-10 · v2.0
**Source**: Brand Layer v2 (about.md + voice_profile.md + write_rules.md v2.3) + Hook Pattern Bank v1.2 + Content Formula v1 + Expression Bank v1 + D1–D15 v1 prototype learnings
**Target**: Single source of truth cho 30 bài đầu — app sinh nội dung + brand owner duyệt theo file này.
**Tinh thần**: Topic mở. Intent kiểm soát. Insight thật là lõi. Voice là nhạc trưởng. App là tay viết. Brand owner là nhạc trưởng cuối cùng.
