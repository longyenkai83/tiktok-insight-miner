"""Minimal product review with inline customer evidence and a separate human test gate."""
import uuid
from pathlib import Path

from .governance_store import load_reviews, load_verified
from .governance_ui import review_workspace
from .pattern_models import artifact_hash
from .product_engine import checked_discovery, extend_discovery, new_discovery, priority_inputs
from .product_store import (ProductAction, apply_products, decide_product_file, export_products,
    load_discovery, prepare_product_file, save_discovery)


def why_product(tree, opportunity):
    vi = opportunity.priority_need
    # Full upstream snapshot closes Pattern -> Signal -> Source without a second workflow.
    snapshot = next(s for s in tree.verified_input.review_history.snapshots if artifact_hash(s) == vi.source_insights_hash)
    return dict(priority_need=vi.model_dump(mode='json'), support_pattern_ids=vi.support_pattern_ids,
        exact_evidence=[r.model_dump(mode='json') for r in vi.evidence_refs],
        patterns_signals_sources=snapshot.input_patterns.model_dump(mode='json'))


def render_product_discovery(output_root, reviewer_id, *, provider=None):
    import streamlit as st
    st.header('V2 — Product Discovery')
    st.info('Đề xuất để thử nghiệm, chưa xác thực sản phẩm hoặc nhu cầu mua. Không chạy thử nghiệm bên ngoài.')
    workspace = st.text_input('Human Review workspace', value='customer-intelligence', key='product_workspace')
    run_id = st.text_input('Product run', value='product-research', key='product_run')
    try:
        source = review_workspace(output_root, workspace)
        safe_run = review_workspace(output_root, run_id).name
        folder = Path(output_root) / 'v2-product-discovery' / workspace / safe_run
        # Reject symlink escapes as well as invalid workspace/run names.
        if not folder.resolve().is_relative_to(Path(output_root).resolve()): raise ValueError('unsafe_workspace')
        qp, vp = source/'insight_reviews.json', source/'verified_insights.json'
        if not qp.exists() or not vp.exists():
            st.info('Chuẩn bị Verified Insights và đánh dấu Priority Need tại Human Review trước.'); return
        reviews, verified = load_reviews(qp), load_verified(vp)
        try: eligible = priority_inputs(verified, reviews)
        except ValueError as exc:
            if str(exc) == 'human_priority_need_required':
                st.info('Chưa có Priority Need được người dùng duyệt. Không sinh Product Discovery.'); return
            raise
        tp, dp = folder/'product_discovery.json', folder/'product_decisions.json'
        tree = checked_discovery(load_discovery(tp), reviews) if tp.exists() else new_discovery(verified, reviews, project_id=workspace, run_id=run_id)
        if tree.input_verified_hash != artifact_hash(verified): raise ValueError('upstream_changed')
        expected_hash = artifact_hash(tree) if tp.exists() else None
        vis = {v.verified_insight_id: v for v in eligible}
        vid = st.selectbox('Priority Need', list(vis), format_func=lambda i: vis[i].statement.text)
        vi = vis[vid]
        st.write('Customer truth / Jobs / Pains / Gains / Context', vi.model_dump(mode='json'))
        count = st.number_input('Số phương án gợi ý', min_value=1, max_value=20, value=3)
        if st.button('Tạo phương án sản phẩm'):
            with st.spinner('Đang đề xuất phương án và kế hoạch học từ bằng chứng...'):
                updated = extend_discovery(tree, load_reviews(qp), verified_insight_id=vid, count=int(count), provider=provider)
                fresh = load_reviews(qp)
                save_discovery(updated, tp, fresh, expected_hash=expected_hash)
                prepare_product_file(updated, fresh, dp)
            st.rerun()
        opportunities = {o.product_opportunity_id: o for o in tree.opportunities if o.verified_insight_id == vid}
        if opportunities:
            oid = st.selectbox('Product Opportunity — PROPOSED', list(opportunities), format_func=lambda i: opportunities[i].opportunity_statement.text)
            o = opportunities[oid]
            st.write('Loại / Cơ chế / Tiến bộ đề xuất', o.opportunity_type, o.mechanism.model_dump(), o.customer_progress.model_dump(mode='json'))
            with st.expander('TẠI SAO MÁY ĐỀ XUẤT SẢN PHẨM NÀY?'):
                st.json(why_product(tree, o))
            st.write('Possible Value Map — PROPOSED', next(m for m in tree.value_maps if m.product_opportunity_id == oid).model_dump(mode='json'))
            assumptions = {a.assumption_id: a for a in tree.assumptions if a.product_opportunity_id == oid}
            st.write('Assumptions — HYPOTHESIS', [a.model_dump() for a in assumptions.values()])
            st.caption('Bằng chứng nhu cầu: level 1 — customer speech. Giả định giải pháp: level 0 — chưa kiểm nghiệm.')
            st.write('Experiment plans — PROPOSED', [e.model_dump(mode='json') for e in tree.experiment_plans if e.product_opportunity_id == oid])
            ledger = prepare_product_file(tree, load_reviews(qp), dp)
            with st.form('product_decision_'+artifact_hash(tree)+artifact_hash(ledger)):
                decision = st.selectbox('Quyết định thử nghiệm', ['Chọn hành động', 'explore', 'reject', 'defer'])
                assumption = st.selectbox('Giả định thử trước (tùy chọn)', [None, *assumptions], format_func=lambda i: 'Chưa chọn' if i is None else assumptions[i].observable_behavior)
                importance = st.selectbox('Mức quan trọng do người dùng đánh giá', ['unknown', 'high', 'medium', 'low'])
                riskiest = st.checkbox('Tôi đánh giá giả định đã chọn là rủi ro nhất.')
                rationale = st.text_area('Lý do quyết định')
                attest = st.checkbox('Tôi đã xem bằng chứng và đưa ra quyết định thử nghiệm này.')
                submitted = st.form_submit_button('Lưu quyết định sản phẩm')
            if submitted:
                if not attest or not rationale.strip() or decision == 'Chọn hành động':
                    st.error('Chọn hành động, nhập lý do và xác nhận quyết định của người dùng.')
                else:
                    action = ProductAction(request_id=uuid.uuid4().hex, tree_hash=artifact_hash(tree),
                        product_opportunity_id=oid, opportunity_hash=artifact_hash(o), decision=decision,
                        reviewer_id=reviewer_id, human_attested=True, rationale=rationale,
                        assumption_to_test_first=assumption, assumption_importance=importance, riskiest_assumption=riskiest)
                    decide_product_file(dp, load_discovery(tp), load_reviews(qp), action, expected_history_hash=artifact_hash(ledger))
                    st.rerun()
        if tp.exists():
            ledger = prepare_product_file(tree, load_reviews(qp), dp)
            st.caption(f'{len(apply_products(ledger, tree, load_reviews(qp)).selected_opportunities)} phương án được chọn để thử nghiệm')
            with st.expander('Lịch sử quyết định / validation issues'):
                st.json([e.model_dump(mode='json') for e in ledger.events]); st.json([i.model_dump() for i in tree.validation_issues])
            st.download_button('Tải product_discovery.json', tree.model_dump_json(indent=2), 'product_discovery.json', mime='application/json')
            if st.button('Xuất phương án được chọn để thử nghiệm'):
                selected = export_products(dp, folder/'selected_product_opportunities.json', load_discovery(tp), load_reviews(qp))
                st.download_button('Tải selected_product_opportunities.json', selected.model_dump_json(indent=2), 'selected_product_opportunities.json', mime='application/json')
    except (OSError, ValueError):
        st.error('Dữ liệu, Priority Need hoặc quyết định đã thay đổi / không hợp lệ. Kiểm tra ledger hiện tại; dùng run mới nếu upstream thay đổi.')
