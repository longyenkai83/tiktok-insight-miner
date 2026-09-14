# 01 — ARCHITECTURE

## CURRENT STATE — chỉ mô tả baseline đã audit

Theo baseline định danh tại [00-PROJECT-OS.md](00-PROJECT-OS.md):

- Miner dùng classifier bảy bucket; dữ liệu classified rẽ sang report/brief/strategy và bank/selection. Strategy hiện không cấp insight có kiểu cho bank/selection.
- `selected_angles.json` thực tế chứa record comment được chọn, không phải hợp đồng Angle V2.
- Hai đường xuất pack Markdown khác nhau; có mất/truncate trường và pha trộn config. Bridge sang Reelo hiện qua file/Drive, chưa có typed Content Intelligence Packet.
- `strict_grounding` hiện chủ yếu ràng buộc prompt, chưa bảo đảm quote/likes đối chiếu nguồn. Một số tầng dùng persona/meta-pain/config thiếu phân biệt truth type.
- Reelo có các skill viết và kiểm nội dung; quy tắc chống bịa và rubric số liệu còn mâu thuẫn. Không có cơ sở để coi mọi đầu ra hiện tại là đã qua cổng bằng chứng V2.

Đây là gap cần thiết kế giải quyết trong tương lai, không phải lỗi được phép sửa ở Phase 0. Tài liệu không chứng nhận hành vi production ngoài snapshot audit.

## TARGET — kiến trúc được yêu cầu

```text
Source → Audience / Role / Context → Customer Signals → Pattern → Evidence
→ Insight → Topic → Angle → Human Selection → Content Intelligence Packet
→ Reelo Writer → Unified Agent
```

| Tầng | Trách nhiệm và đầu ra | Ranh giới |
|---|---|---|
| Source | Snapshot comment và nguồn gốc ổn định | Không suy ra persona hoặc ý định mua từ danh tính |
| Audience / Role / Context | Ghi nhận/giả thuyết về bối cảnh, nhóm người và vai trò hệ sinh thái | Chưa biết thì unknown; phân biệt lời tự nhận và suy luận |
| Customer Signals | Tách nhiều biểu hiện Jobs/Pains/Gains, bối cảnh, hành vi, ngôn ngữ | Không ép một comment vào một bucket duy nhất |
| Pattern | Nhóm signal có quan hệ và ghi phạm vi mẫu, số nguồn phân biệt | Không coi lượt like hoặc nhiều signal cùng comment là nhiều người đồng ý |
| Evidence | Đóng gói bằng chứng hỗ trợ/phản bác, quote và nguồn | Không tạo bằng chứng mới để khớp kết luận |
| Insight | Diễn giải có giới hạn và truy vết; tách giả thuyết cần kiểm chứng | Không trộn đề xuất offer hoặc meta-pain thành observed truth |
| Topic | Đề xuất chủ đề từ insight đủ điều kiện | Không bỏ qua Insight để đi từ config tới nội dung |
| Angle | Đề xuất góc tiếp cận cho Topic, tham chiếu claim được dùng | Chưa phải bài viết hoàn chỉnh, không thêm customer truth |
| Human Selection | Người thật duyệt Angle và phiên bản nền tảng bằng chứng | Máy được gợi ý, không được tự ghi phê duyệt của người |
| Content Intelligence Packet | Hợp đồng có kiểu, có version, đủ ngữ cảnh và bằng chứng | Không dùng pack Markdown tự do hoặc selected_angles làm schema chuẩn |
| Reelo Writer | Tạo nội dung theo packet và trả trace claim | Tự do diễn đạt trong giới hạn claim; không tự bịa quote/số/case |
| Unified Agent | Điều phối, quản lý trạng thái, dừng ở gate và ghi lineage | Không tự lấp dữ liệu thiếu hoặc vượt quyền human review |

## Dòng bằng chứng và Customer Profile

Source reference phải được gắn ngay khi ghi nhận Audience/Role/Context và Signals. Evidence layer nằm sau Pattern là bước tổng hợp và kiểm chứng bằng chứng, không có nghĩa tới đó mới lưu provenance. Đường truy vết tối thiểu của insight DERIVED:

`Insight → Evidence → SourceRecord → external source comment`.

Pattern và Signal là các nút giải thích trung gian, cũng phải phân giải tới cùng source snapshot. Một Insight có thể chứa nhiều claim khác truth type; không được dùng nhãn của cả object che sự khác biệt này.

Customer Profile là view tổng hợp Jobs / Pains / Gains + Context từ các claim có nhãn. Với B2B, vai trò có thể khác giữa người dùng, người trả tiền, người quyết định, người ảnh hưởng, người triển khai và người bị ảnh hưởng. Đây là ví dụ vai trò, không phải phân loại đã xác minh cho một audience. Một người có thể có nhiều vai trò theo ngữ cảnh; comment tag tên người khác không tự chứng minh vai trò influencer.

Phân loại ý nghĩa signal thường là DERIVED; phần text nguyên văn tự nó là OBSERVED. Giả thuyết thiếu bằng chứng được giữ riêng để nghiên cứu, không đi vào customer facts của Writer.

## Ranh giới triển khai

V2 là thiết kế độc lập với tên file, regex, enum, model, UI và score của V1. Không mặc định kế thừa `ContentAngle`, `selected_angles`, auto-top, số từ trong hook, layout Drive hoặc production fallback. Mọi adapter/migration cần mapping mất mát, version và review riêng.

Lựa chọn database hay file, API hay artifact, thuật toán clustering/ranking, model, CLI và UI chưa được chốt. Không triển khai adapter, schema executable, validator, prompt, migration hoặc feature flag trong Phase 0. [05-ROADMAP.md](05-ROADMAP.md) chỉ mô tả hướng đi sau review.
