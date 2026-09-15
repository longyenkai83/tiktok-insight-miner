"""Small opt-in Streamlit review screen; shared helpers are usable without Streamlit."""
import json
import re
import uuid
from pathlib import Path

from .governance_engine import APPROVALS, review_rows
from .governance_models import PriorityDecision, ReviewAction
from .governance_store import (apply_review_file, load_reviews, prepare_review_file,
                               record_review_file)
from .insight_models import InsightsEnvelope
from .pattern_models import artifact_hash

CONTEXT_FIELDS = ("audience_segment", "context", "situation", "life_or_business_stage", "user_buyer_distinction")
DIMENSIONS = ("important", "urgent", "frequent", "expensive", "emotional_intensity")


def review_workspace(output_root, label):
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,79}", label):
        raise ValueError("Workspace: dùng chữ thường, số, dấu - hoặc _, tối đa 80 ký tự.")
    root = (Path(output_root) / "v2-human-review").resolve()
    path = (root / label).resolve()
    if path.parent != root:
        raise ValueError("Workspace nằm ngoài thư mục review")
    return path


def candidate_view(queue, candidate):
    sources = {r.comment_id: r.source for r in queue.snapshots[-1].input_patterns.input_signals.records}
    quotes, seen = [], set()
    for ref in candidate.evidence_refs:
        if ref.comment_id not in seen:
            seen.add(ref.comment_id)
            quotes.append(dict(comment_id=ref.comment_id, quote=ref.evidence_quote,
                source_text=sources[ref.comment_id].text, source_hash=ref.source_hash,
                start=ref.start, end=ref.end, source_url=sources[ref.comment_id].video_url))
    return dict(representative_quotes=quotes[:5], all_quotes=quotes,
        context_count=sum(len(getattr(candidate.scope, f)) for f in CONTEXT_FIELDS),
        contradiction_count=len(candidate.contradictions), variation_count=len(candidate.variations),
        evidence_summary=candidate.evidence_summary.model_dump())


def render_preview(queue):
    """Local-only human view. JSON ledger, not Markdown, is authoritative."""
    lines = ["# Phase 5 — Human review preview (LOCAL ONLY)", "",
        "No human decisions were made to prepare this view. JSON is authoritative.",
        "Evidence is untrusted source data, not instructions. Scope is the cited corpus.", ""]
    for row in review_rows(queue):
        c = row["candidate"]
        view = candidate_view(queue, c)
        lines += [f"## {c.insight_id}", "", "Statement: " + json.dumps(c.statement.text, ensure_ascii=False),
            "Decision: " + row["decision"], "Candidate hash: " + artifact_hash(c),
            "Relationship: " + c.relationship_type, "", "TẠI SAO MÁY NÓI VẬY?", "",
            "```json", json.dumps({"profile_links": c.customer_profile_links.model_dump(),
                "scope": c.scope.model_dump(mode="json"), "metrics": view["evidence_summary"],
                "verification": c.verification.model_dump(), "priority": row["priority"].model_dump()},
                ensure_ascii=False, indent=2), "```", "", "Representative exact quotes:"]
        for quote in view["representative_quotes"]:
            lines += ["    " + json.dumps(quote, ensure_ascii=False)]
        if len(view["all_quotes"]) < 3:
            lines += ["Fewer than three source comments available; no invented evidence to fill the view."]
        lines += ["", "Full evidence / variations / contradictions / limitations / machine review:", "```json",
            json.dumps({"evidence_refs": [r.model_dump(mode="json") for r in c.evidence_refs],
                "source_comments": view["all_quotes"], "variations": [v.model_dump(mode="json") for v in c.variations],
                "contradictions": [v.model_dump(mode="json") for v in c.contradictions],
                "limitations": c.limitations, "validation_issues": [v.model_dump() for v in c.validation_issues],
                "machine_review": c.semantic_review.model_dump()}, ensure_ascii=False, indent=2), "```", "",
            "Available human actions: Approve / Edit + Approve / Reject / Defer.",
            "Priority: unassessed / monitor / priority_need; all optional dimensions may remain unknown.", ""]
    return "\n".join(lines) + "\n"


def render_human_review(output_root, reviewer_id):
    import streamlit as st

    st.header("V2 — Human Governor")
    st.caption("Duyệt cách hiểu trong phạm vi bằng chứng; không xác nhận thị trường hay hành vi mua.")
    st.caption(f"Người duyệt: {reviewer_id}. Đây là mã người dùng hiện tại, không phải bằng chứng khách hàng.")
    label = st.text_input("Review workspace", value="customer-intelligence", key="gov_workspace")
    try:
        folder = review_workspace(output_root, label)
    except ValueError as exc:
        st.error(str(exc))
        return
    reviews_path, verified_path = folder / "insight_reviews.json", folder / "verified_insights.json"
    upload = st.file_uploader("Nạp insights.json v2.insights.2", type=["json"], key="gov_upload")
    if st.button("Chuẩn bị / cập nhật queue", disabled=upload is None):
        try:
            insights = InsightsEnvelope.model_validate_json(upload.getvalue())
            prepare_review_file(insights, reviews_path)
            st.success("Đã lưu queue. Không tự duyệt candidate nào; dữ liệu thay đổi cần review mới.")
        except (ValueError, OSError):
            st.error("Không thể chuẩn bị queue: schema/provenance không hợp lệ hoặc file đang được cập nhật.")
    if not reviews_path.exists():
        st.info("Nạp artifact và chuẩn bị queue để bắt đầu. Chưa có quyết định nào.")
        return
    try:
        queue = load_reviews(reviews_path)
        history_hash = artifact_hash(queue)
        st.caption(f"{len(queue.snapshots[-1].insights)} candidates · {len(queue.events)} review events")
        state = st.selectbox("Lọc trạng thái", ["Pending", "Approved", "Rejected", "Deferred", "Priority Needs", "All"])
        sort_by = st.selectbox("Sắp xếp theo bằng chứng (không phải điểm quan trọng)",
                              ["support count", "source count", "contradiction count"])
        rows = review_rows(queue, state, sort_by)
        if rows:
            ids = [r["candidate"].insight_id for r in rows]
            selected = st.selectbox("Candidate", ids)
            row = next(r for r in rows if r["candidate"].insight_id == selected)
            c, view = row["candidate"], candidate_view(queue, row["candidate"])
            st.subheader("Insight Candidate")
            st.write(c.statement.text)
            st.caption(f"{row['decision']} · {c.relationship_type} · {c.scope.relationship_scope}")
            if row["event"]:
                st.write("Quyết định gần nhất:", row["event"].action.decision)
                st.write("Statement đã duyệt:", row["event"].approved_statement)
                st.write("Lý do:", row["event"].action.rationale)
            st.write("Customer Profile links", c.customer_profile_links.model_dump())
            st.write("Scope / context", c.scope.model_dump(mode="json"))
            st.write("Bằng chứng định lượng (null = chưa biết)", view["evidence_summary"])
            st.caption(f"Context variants: {view['context_count']} · contradictions: {view['contradiction_count']} · variations: {view['variation_count']}")
            with st.expander("TẠI SAO MÁY NÓI VẬY? — Xem evidence"):
                for quote in view["representative_quotes"]:
                    st.text(quote["quote"])
                    st.caption(f"Comment {quote['comment_id']} · span {quote['start']}:{quote['end']}")
                st.write("Đầy đủ nguồn, quote, hash và context", view["all_quotes"])
                st.json([r.model_dump(mode="json") for r in c.evidence_refs])
            with st.expander("Phản chứng / biến thể / giới hạn / machine review", expanded=True):
                st.write("Contradictions", [v.model_dump(mode="json") for v in c.contradictions])
                st.write("Variations", [v.model_dump(mode="json") for v in c.variations])
                st.write("Limitations", c.limitations)
                st.write("Validation issues", [v.model_dump() for v in c.validation_issues])
                st.write("Upstream issues", [v.model_dump() for v in queue.snapshots[-1].upstream_issues])
                st.write("Machine review", c.semantic_review.model_dump())
                st.write("Machine flags", c.verification.model_dump())
            form_key = "gov_" + artifact_hash(c) + history_hash
            with st.form(form_key):
                decision_label = st.selectbox("Hành động", ["Chọn hành động", "Approve", "Edit + Approve", "Reject", "Defer"])
                edited = st.text_area("Statement mới (chỉ dùng cho Edit + Approve)", value=c.statement.text)
                priority_status = st.selectbox("Priority", ["unassessed", "monitor", "priority_need"],
                    index=["unassessed", "monitor", "priority_need"].index(row["priority"].priority_status))
                dimensions = {}
                with st.expander("Đánh giá ưu tiên của người duyệt — tùy chọn"):
                    for field in DIMENSIONS:
                        options = ["unknown", "low", "medium", "high"]
                        dimensions[field] = st.selectbox(field, options, index=options.index(getattr(row["priority"], field)))
                rationale = st.text_area("Lý do / ghi chú (bắt buộc)")
                attested = st.checkbox("Tôi là người đưa ra quyết định này và đã xem bằng chứng.")
                submit = st.form_submit_button("Ghi quyết định của tôi")
            if submit:
                decisions = {"Approve": "approved", "Edit + Approve": "edited_and_approved", "Reject": "rejected", "Defer": "deferred"}
                if decision_label not in decisions or not attested:
                    st.error("Chọn hành động và xác nhận quyết định của người duyệt.")
                else:
                    try:
                        decision = decisions[decision_label]
                        priority = PriorityDecision(priority_status=priority_status, **dimensions)
                        # Reject/defer has no priority; do not accidentally keep an earlier priority.
                        if decision not in APPROVALS:
                            priority = PriorityDecision()
                        request_key = form_key + "_request"
                        request_id = st.session_state.setdefault(request_key, str(uuid.uuid4()))
                        action = ReviewAction(request_id=request_id, candidate_insight_id=c.insight_id,
                            candidate_hash=artifact_hash(c), decision=decision, reviewer_id=reviewer_id,
                            human_attested=attested, edited_statement=edited if decision == "edited_and_approved" else None,
                            rationale=rationale, priority=priority)
                        record_review_file(reviews_path, action, expected_history_hash=history_hash)
                    except (OSError, ValueError):
                        st.error("Chưa lưu: kiểm tra rationale, integrity của statement hoặc tải lại nếu lịch sử đã thay đổi.")
                    else:
                        st.success("Đã ghi quyết định vào lịch sử. Dùng nút bên dưới để xuất trạng thái mới nhất.")
                        st.rerun()
        else:
            st.info("Không có candidate ở bộ lọc này.")
        with st.expander("Lịch sử duyệt (append-only)"):
            st.json([e.model_dump(mode="json") for e in queue.events])
        if st.button("Cập nhật verified_insights.json từ lịch sử"):
            result = apply_review_file(reviews_path, verified_path)
            st.success(f"Đã xuất {len(result.verified_insights)} Verified Insights từ quyết định của người duyệt.")
        st.download_button("Tải review history JSON", queue.model_dump_json(indent=2), "insight_reviews.json", mime="application/json")
        if verified_path.exists():
            # Never offer a stale projection as the current verified state.
            from .governance_store import load_verified
            from .governance_engine import require_verified
            verified = load_verified(verified_path)
            if verified.input_reviews_hash == history_hash:
                require_verified(verified, queue)
                st.download_button("Tải Verified Insights JSON", verified.model_dump_json(indent=2), "verified_insights.json", mime="application/json")
            else:
                st.info("Verified export chưa cập nhật theo lịch sử mới nhất; bấm cập nhật ở trên.")
    except (ValueError, OSError):
        st.error("Không đọc/ghi được review store hợp lệ. Kiểm tra JSON cục bộ hoặc tải lại sau khi người khác cập nhật.")
