"""Minimal opt-in content tree; evidence remains alongside each proposed content layer."""
import uuid
from pathlib import Path
from typing import get_args

from .content_route_engine import checked_tree, extend_content_tree, new_content_tree
from .content_route_models import AngleType
from .content_selection import (SelectionAction, apply_selection, export_selection_file, load_tree,
    prepare_selection_file, save_tree, select_angle_file)
from .governance_engine import require_verified
from .governance_store import load_reviews, load_verified
from .governance_ui import review_workspace
from .pattern_models import artifact_hash


def content_evidence_view(tree, obj):
    vi = next(v for v in tree.verified_input.verified_insights if v.verified_insight_id == obj.verified_insight_id)
    return dict(verified_insight=vi.statement.model_dump(), human_review=vi.human_review.model_dump(mode="json"),
        support_patterns=vi.support_pattern_ids, support_counts=vi.evidence_summary.model_dump(),
        context=vi.scope.model_dump(mode="json"), evidence_refs=[r.model_dump(mode="json") for r in vi.evidence_refs],
        contradictions=[c.model_dump(mode="json") for c in vi.contradictions],
        variations=[v.model_dump(mode="json") for v in vi.variations], limitations=vi.limitations)


def render_content_route(output_root, reviewer_id, *, provider=None):
    import streamlit as st

    st.header("V2 — Content Route")
    st.caption("Verified Insight → Content Opportunity → Topic → Angle → lựa chọn của người dùng.")
    st.info("Mọi góc và framing là PROPOSED. Chưa viết bài/kịch bản, chưa chuyển sang Reelo.")
    workspace = st.text_input("Human Review workspace", value="customer-intelligence", key="content_workspace")
    run_id = st.text_input("Content run", value="content-research", key="content_run")
    try:
        source_folder = review_workspace(output_root, workspace)
        # Reuse the validated local name/path policy, with separate content-route storage.
        safe_run = review_workspace(output_root, run_id).name
        folder = Path(output_root) / "v2-content-route" / workspace / safe_run
        reviews_path = source_folder / "insight_reviews.json"
        verified_path = source_folder / "verified_insights.json"
        if not reviews_path.exists() or not verified_path.exists():
            st.info("Chuẩn bị và duyệt insight tại Human Review, rồi xuất Verified Insights trước.")
            return
        reviews, verified = load_reviews(reviews_path), load_verified(verified_path)
        require_verified(verified, reviews)
        if not verified.verified_insights:
            st.info("Chưa có insight được người dùng duyệt. Không sinh content hoặc tự tạo approval.")
            return
        tree_path, selections_path = folder / "content_tree.json", folder / "content_selections.json"
        selected_path = folder / "selected_content_angles.json"
        tree = checked_tree(load_tree(tree_path), reviews) if tree_path.exists() else new_content_tree(
            verified, reviews, project_id=workspace, run_id=run_id)
        if tree.input_verified_hash != artifact_hash(verified):
            raise ValueError("upstream changed; use a new content run")
        expected_hash = artifact_hash(tree) if tree_path.exists() else None
        objective = st.text_input("Mục tiêu nội dung (tùy chọn)", max_chars=600)
        opportunity_count = st.number_input("Số Content Opportunities gợi ý", min_value=1, max_value=50, value=2)
        topic_count = st.number_input("Số Topics mỗi opportunity", min_value=1, max_value=50, value=2)
        angle_count = st.number_input("Số góc mỗi topic", min_value=1, max_value=50, value=10)
        preference = st.selectbox("Kiểu góc ưu tiên (tùy chọn)", ["Không ép kiểu", *get_args(AngleType)])
        preference = None if preference == "Không ép kiểu" else preference
        vis = {v.verified_insight_id: v for v in verified.verified_insights}
        vi_id = st.selectbox("Verified Insight", list(vis), format_func=lambda i: vis[i].statement.text)
        vi = vis[vi_id]
        st.write("Audience / Context", vi.scope.model_dump(mode="json"))
        st.write("Problem / Gain / Job", vi.customer_profile_links.model_dump())
        st.write(vi.statement.text)

        def evidence(obj, key):
            with st.expander("Insight này dựa vào đâu? — " + key):
                st.json(content_evidence_view(tree, obj))

        def generate(stage, parent, count):
            with st.spinner("Đang tạo đề xuất dựa trên insight đã duyệt..."):
                updated = extend_content_tree(tree, load_reviews(reviews_path), stage=stage, parent_id=parent,
                    count=int(count), content_objective=objective, angle_type_preference=preference, provider=provider)
                fresh_reviews = load_reviews(reviews_path)
                save_tree(updated, tree_path, fresh_reviews, expected_hash=expected_hash)
                prepare_selection_file(updated, fresh_reviews, selections_path)
            st.rerun()

        evidence(vi, "Verified Insight")
        if st.button("Tạo Content Opportunities"):
            generate("opportunities", vi_id, opportunity_count)
        opportunities = {o.content_opportunity_id: o for o in tree.content_opportunities if o.verified_insight_id == vi_id}
        if opportunities:
            oid = st.selectbox("Content Opportunity — PROPOSED", list(opportunities), format_func=lambda i: opportunities[i].statement.text)
            opportunity = opportunities[oid]
            st.write("Purpose / Customer value", opportunity.purpose, opportunity.customer_value.model_dump())
            evidence(opportunity, "Content Opportunity")
            if st.button("Mở rộng Topics"):
                generate("topics", oid, topic_count)
            topics = {t.topic_id: t for t in tree.topics if t.content_opportunity_id == oid}
            if topics:
                tid = st.selectbox("Topic — PROPOSED", list(topics), format_func=lambda i: topics[i].title.text)
                topic = topics[tid]
                st.write(topic.description.model_dump())
                evidence(topic, "Topic")
                if st.button("Bung góc"):
                    generate("angles", tid, angle_count)
                if st.button("Bung 10 góc"):
                    generate("angles", tid, 10)
                angles = {a.angle_id: a for a in tree.angles if a.topic_id == tid}
                if angles:
                    aid = st.selectbox("Angle — PROPOSED", list(angles), format_func=lambda i: angles[i].title.text)
                    angle = angles[aid]
                    st.write("Before belief — framing đề xuất", angle.belief_before.model_dump())
                    st.write("Core argument", angle.core_argument.model_dump())
                    st.write("After belief — framing đề xuất", angle.belief_after.model_dump())
                    st.write("Opening direction / Customer value", angle.opening_direction.model_dump(), angle.customer_value.model_dump())
                    st.write("Value Scene", angle.value_scene.model_dump(mode="json"))
                    st.write("Customer language — chỉ lời gốc", [r.model_dump(mode="json") for r in angle.language_bank])
                    evidence(angle, "Angle")
                    ledger = prepare_selection_file(tree, load_reviews(reviews_path), selections_path)
                    latest = [e for e in ledger.events if e.action.tree_hash == artifact_hash(tree) and e.action.angle_id == aid]
                    st.caption("Lựa chọn hiện tại: " + (latest[-1].action.decision if latest else "chưa chọn"))
                    with st.form("angle_" + artifact_hash(angle) + artifact_hash(ledger)):
                        decision = st.selectbox("Quyết định góc", ["Chọn hành động", "selected", "rejected", "deferred"])
                        rationale = st.text_area("Lý do chọn góc (tùy chọn)")
                        attested = st.checkbox("Đây là lựa chọn của tôi sau khi xem góc và bằng chứng.")
                        submitted = st.form_submit_button("Lưu lựa chọn góc")
                    if submitted:
                        if not attested or decision == "Chọn hành động":
                            st.error("Chọn hành động và xác nhận lựa chọn của người dùng.")
                        else:
                            action = SelectionAction(request_id=uuid.uuid4().hex, tree_hash=artifact_hash(tree),
                                angle_id=aid, angle_hash=artifact_hash(angle), decision=decision,
                                reviewer_id=reviewer_id, human_attested=True, rationale=rationale)
                            select_angle_file(selections_path, load_reviews(reviews_path), action,
                                              expected_history_hash=artifact_hash(ledger))
                            st.rerun()
        if tree_path.exists():
            st.download_button("Tải content_tree.json", tree.model_dump_json(indent=2), "content_tree.json", mime="application/json")
            ledger = prepare_selection_file(tree, load_reviews(reviews_path), selections_path)
            st.caption(f"{len(apply_selection(ledger, load_reviews(reviews_path)).selected_angles)} góc được chọn bởi người dùng")
            with st.expander("Lịch sử chọn góc / lỗi validation"):
                st.json([e.model_dump(mode="json") for e in ledger.events])
                st.json([i.model_dump() for i in tree.validation_issues])
            if st.button("Xuất góc đã chọn — chưa phải Content Intelligence Packet"):
                selected = export_selection_file(selections_path, selected_path, load_reviews(reviews_path))
                st.download_button("Tải selected_content_angles.json", selected.model_dump_json(indent=2),
                                   "selected_content_angles.json", mime="application/json")
    except (OSError, ValueError):
        st.error("Không thể tiếp tục: dữ liệu/approval đã thay đổi hoặc schema/ID không hợp lệ. Kiểm tra ledger hiện tại; tạo run mới nếu upstream thay đổi.")
