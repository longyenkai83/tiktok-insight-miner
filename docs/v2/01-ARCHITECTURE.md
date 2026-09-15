# 01 — ARCHITECTURE

## Phase 4.1 — accepted state semantics (DEC-042)

Phase 4 produces **INSIGHT CANDIDATES**, never Verified Insights. Automated acceptance
is `machine_accepted`; every emitted candidate remains `pending_human_review`.
`source_grounded` validates structural provenance; `evidence_support_present` means
attached supporting evidence exists; `machine_review_passed` records fallible automated
review. None certifies semantic truth. `evidence_backed` is removed from the executable
verification model. Human/market/purchase flags remain false.

**Phase 5 Human Approval is the first explicit Human Governor gate and the authoritative
semantic gate.** Only that future human process may produce a Verified Insight and set
human_verified=true. Future decisions: approved / edited_and_approved / rejected.
Human approval does not itself prove purchase, market demand, or turn DERIVED into OBSERVED.
Do not implement Phase 5 now. Keep current closed IDs, part support, semantic review,
causality/scope/demographic/solution/market checks; no extra multi-reviewer architecture.
Completion does not require perfect AI. Known semantic misses remain review inputs.

Future Source Router activates only needed routes: Social Listening, Owned Customer Voice,
Review Mining, Forum/Community/Public Discussion, Manual Research. Each route may be
enabled/disabled, run manually or scheduled independently. All converge to Normalized
Evidence → Signal → Context → Pattern → Insight Candidate; never one intelligence engine
per platform. Full route catalog and downstream paths: [11](11-BUSINESS-OS-NORTH-STAR.md).
Normalized adapter fields and null semantics: [02](02-DATA-SCHEMA.md).

## Phase 4 — Evidence + Insight Candidates

`patterns.json → revalidate Phase 1–3 provenance → closed-pattern-ID synthesis → code guards → separate semantic review → code-built evidence bundle → insights.json`.
Independent build-insights CLI. No change to legacy run or Phase 1–3 behavior.

Evidence Engine resolves patterns to exact refs and deterministic support, profile links,
scope, variants and possible counter-evidence. No model-created quotes, members or metrics.
Insight Engine synthesizes a DERIVED relationship/tension rather than renaming a label.
Single-pattern and cross-pattern candidates are allowed; different speakers do not imply
co-occurring traits, causality or hidden motivation within one person.

Source-grounded means structurally valid provenance, not correct interpretation.
Evidence support present means evidence is attached, not proven semantic support.
Machine review passed records an automated assessment, not human approval.
Output is Insight Candidates pending_human_review; human/market/purchase flags are false.
Verified Insight exists only after future Phase 5 Human Approval. No final priority ranking.

## Business OS and future integration — ACCEPTED design, not runtime

Customer Intelligence is the first sensing/understanding layer of an AI-native Business OS;
see [11-BUSINESS-OS-NORTH-STAR.md](11-BUSINESS-OS-NORTH-STAR.md). Reusable core and portable,
platform-neutral contracts support internal use → proven workflow → standardize → productize
→ distribute. Human Governor approves consequential decisions; mechanical low-risk steps
do not each require approval. No multi-tenancy or package rename in Phase 4.

Source adapters (TikTok, Facebook Page comments/inbox, Group/comments, manual paste,
CSV/Excel, future YouTube/others) → Normalized Evidence → shared engine. Continuous/daily
owned-source ingestion is separate from periodic/manual analysis. Future store is idempotent,
durable-ID-first with hash protection, NEW/PROCESSING/PROCESSED/FAILED/IGNORED and batch trace.
Do not implement that state management or YouTube now.

Future direct Reelo route: Verified Insight → Content Opportunity → Human Selection → typed
Content Intelligence Packet → direct ingestion → Writer → Critic → Output. This condensed
transport route retains existing Topic/Angle gates. Drive is legacy compatibility/backup,
not primary V2 transport; brief.md is not a contract. Preserve /nap-insight dedupe,
supersession, provenance and human approval for conflicting knowledge replacement.
No Reelo API/adapter implementation in Phase 4.

## Phase 3 — implemented, pending architect review

`signals.json + contexts.json → closed claim catalog → similarity relations → deterministic complete-link groups → patterns.json`.
Independent `build-patterns` CLI; không nối vào legacy run, classifier, Reelo hoặc hai downstream modes.

- Revalidate hai schema, hash của input signals và join comment_id/source_hash. Thiếu context record vẫn dùng signal; context orphan ghi issue và bỏ khỏi catalog.
- Candidate grouping dùng exact whitespace-normalized evidence equality và semantic relations qua interface `RelationProvider`. Adapter Anthropic chỉ so sánh claim IDs có thật, không tạo members/quotes/metrics. Không dùng embedding/dependency mới.
- Code complete-link theo thứ tự evidence ID ổn định: chỉ thêm member nếu tương thích với **mọi** member đang có, chặn merge bằng chuỗi A–B–C khi A–C chưa có support. Không gộp khác category; context phải cùng field. Subcategory mixed giữ mọi upstream path.
- Semantic relations `same_meaning`, `variation`, `contradiction` là DERIVED. Relation lỗi/unknown/self/duplicate/cross-category bị loại có issue. Contradiction không làm mất pattern; counter-ref không được tính vào support của pattern bị phản bác.
- Stage labeling bảo thủ: quote ngắn nhất trong group làm representative label, normalized_meaning chỉ chuẩn hóa whitespace. Cả hai dùng DERIVED, không tự gọi đó là phát biểu bao quát toàn group. Giữ mọi wording variant và context distribution nguyên văn; không sinh free-form customer fact.
- Singletons vẫn là candidate. Pattern không phải Insight; không importance score, Verified Insight, opportunity, topic, angle, content, experiment hoặc final segment.

Semantic adapter chia similarity requests theo category/context field; một pass riêng trên toàn catalog tìm contradiction. Transport dùng short IDs và enum scoped theo request, code chỉ map exact ID hợp lệ. Giới hạn toàn catalog: tối đa 200 accepted claims và 180,000 ký tự payload, không truncate. Vượt giới hạn/API lỗi trả exact baseline với semantic_status=error và exit 2; không giả là semantic success. `--exact-only` không gọi AI và ghi NOT_CHECKED cho phản chứng. Đây là giới hạn Phase 3 cần review cho corpus lớn.

## CURRENT STATE — chỉ mô tả baseline đã audit

Theo baseline định danh tại [00-PROJECT-OS.md](00-PROJECT-OS.md):

- Miner dùng classifier bảy bucket; dữ liệu classified rẽ sang report/brief/strategy và bank/selection. Strategy hiện không cấp insight có kiểu cho bank/selection.
- `selected_angles.json` thực tế chứa record comment được chọn, không phải hợp đồng Angle V2.
- Hai đường xuất pack Markdown khác nhau; có mất/truncate trường và pha trộn config. Bridge sang Reelo hiện qua file/Drive, chưa có typed Content Intelligence Packet.
- `strict_grounding` hiện chủ yếu ràng buộc prompt, chưa bảo đảm quote/likes đối chiếu nguồn. Một số tầng dùng persona/meta-pain/config thiếu phân biệt truth type.
- Reelo có các skill viết và kiểm nội dung; quy tắc chống bịa và rubric số liệu còn mâu thuẫn. Không có cơ sở để coi mọi đầu ra hiện tại là đã qua cổng bằng chứng V2.

Đây là gap cần thiết kế giải quyết trong tương lai, không phải lỗi được phép sửa ở Phase 0. Tài liệu không chứng nhận hành vi production ngoài snapshot audit.

## TARGET — locked architecture, DEC-024–032

```text
Shared Customer Intelligence Engine:
Source → Normalized Evidence → Signal Extraction → Customer Context
→ Pattern Engine → Evidence Engine → Insight Candidate → Phase 5 Human Approval → Verified Insight

A. CONTENT RESEARCH MODE:
Verified Insight → Content Opportunity → Topic → Angle → Human Selection
→ Content Intelligence Packet → Reelo Writer

B. PRODUCT DISCOVERY MODE:
Verified Insight → Priority Need → Product Opportunity → Possible Value Map
  (Products & Services / Pain Relievers / Gain Creators)
→ Assumptions → Experiments → Evidence → Decision → Validated Product
```

## Lõi dùng chung

Normalized Evidence giữ source snapshot, metadata, hash và text để kiểm provenance; không biến lời tự nhận thành fact ngoài đời. Signal Extraction giữ nhiều Jobs/Pains/Gains/Behavior/Language signals trên một comment. Customer Context bổ sung candidates theo đúng năm field đã chốt, vẫn ở cấp comment. Pattern Engine mới chịu trách nhiệm clustering và tần suất xuyên corpus (Phase 3); giữ context variants, final segmentation thuộc downstream analysis.

Evidence Engine giữ support/phản chứng/scope để đi tới Verified Insight. Verified không có nghĩa model tự cho confidence cao là đúng. Priority Need phải xuất phát từ Jobs/Pains/Gains/Verified Insights có evidence, không từ offer/config tự suy nhu cầu. Chi tiết ranking và tiêu chí verification là thiết kế phase sau, chưa thực thi.

## Hai mode downstream

Content Research: Content Opportunity dẫn tới Topic/Angle, Human Selection và typed Content Intelligence Packet cho Reelo Writer. Writer sáng tạo diễn đạt, không tạo customer truth. Không dùng legacy selected_angles làm schema V2.

Product Discovery: Opportunity Area và Possible Value Map là đề xuất (PROPOSED), không phải validated demand. Value Map có Products & Services, Pain Relievers, Gain Creators. Mọi candidate cần Assumption → Experiment → Evidence → Decision trước khi gọi Validated Product. Evidence thí nghiệm giữ provenance riêng, không biến proposal thành lời khách quan sát được. Không coi phê duyệt một ý tưởng là bằng chứng nhu cầu.

Product bao gồm miễn phí hoặc trả phí: tool, checklist, template, calculator, lead magnet, workshop, service, feature, resource hoặc commercial product. V2 B2C-first; không B2B stakeholder graph/buying committee.

Project goal có thể là CONTENT / PRODUCT_DISCOVERY / BOTH trong tương lai. Router/UI/unified agent chỉ là kiến trúc tài liệu, không được cài trong Phase 2.

## Phạm vi Phase 2

`signals.json (v2.signals.1) → contexts.json (v2.contexts.1)`, độc lập CLI. Customer Identity chỉ có audience_segment, context, situation, life_or_business_stage, user_buyer_distinction (optional). Không có final segment/corpus clustering. Cùng source có thể có zero/multiple context candidates. Unknown hợp lệ, không infer identity từ topic video hoặc metadata tác giả.

Reuse source snapshot/hash, source-span validation, truth type OBSERVED/DERIVED và issues của Phase 1. Model trả field/evidence_quote/truth_type/confidence theo comment ID; code tạo claim từ exact validated source span. Không paraphrase demographics, không sinh HYPOTHESIS/PROPOSED, content hay product opportunity trong Phase 2.

## Phân biệt CURRENT STATE và thiết kế đích

Audit baseline mô tả legacy, không chứng nhận kiến trúc mới đã chạy. Kiến trúc tuyến tính cũ DEC-011 được thay bởi DEC-024/025 theo yêu cầu trực tiếp; giữ lịch sử trong DECISIONS/CHANGELOG. Phase 1 chạy độc lập; Phase 2 chỉ thêm context. Phase 3 thêm Pattern Engine độc lập; các tầng sau Pattern vẫn cần phạm vi review riêng.
