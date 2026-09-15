"""Packet preview from current local ledgers, with explicit PASS/FAIL and export."""
from pathlib import Path

from .content_packet_builder import build_packet, current_inputs
from .content_packet_store import load_packet, packet_preview, save_packet
from .content_packet_validator import validate_current
from .content_selection import SelectedAnglesEnvelope, load_selection, load_tree
from .governance_store import load_reviews, load_verified
from .governance_ui import review_workspace


def render_packet_preview(output_root):
    import streamlit as st
    st.header('V2 — Packet Preview')
    st.caption('REELO SẼ NHẬN ĐƯỢC GÌ? Chỉ tạo và kiểm tra packet local; chưa gửi sang Writer.')
    workspace=st.text_input('Human Review workspace',value='customer-intelligence',key='packet_workspace')
    run=st.text_input('Content run',value='content-research',key='packet_run')
    try:
        source=review_workspace(output_root,workspace)
        safe_run=review_workspace(output_root,run).name
        content=Path(output_root)/'v2-content-route'/workspace/safe_run
        destination=Path(output_root)/'v2-content-packets'/workspace/safe_run
        if not content.resolve().is_relative_to(Path(output_root).resolve()) or not destination.resolve().is_relative_to(Path(output_root).resolve()):
            raise ValueError('unsafe_workspace')
        paths=[source/'verified_insights.json',source/'insight_reviews.json',content/'content_tree.json',
               content/'content_selections.json',content/'selected_content_angles.json']
        if not all(p.exists() for p in paths):
            st.info('Cần Verified Insights, current Content Tree, lịch sử chọn góc và selected_content_angles.json đã xuất.'); return
        def inputs():
            return dict(verified=load_verified(paths[0]),reviews=load_reviews(paths[1]),tree=load_tree(paths[2]),
                ledger=load_selection(paths[3]),selected=SelectedAnglesEnvelope.model_validate_json(paths[4].read_text(encoding='utf-8')))
        state=inputs()
        if not state['selected'].selected_angles:
            st.info('Chưa có góc được người dùng chọn. Không tạo packet.'); return
        choices={s.angle_id:s for s in state['selected'].selected_angles}
        angle_id=st.selectbox('Selected Angle',list(choices))
        current_inputs(**state,angle_id=angle_id)
        goal=st.selectbox('Project goal',['CONTENT','BOTH'])
        previous_files=sorted(destination.glob('CIP-*.json')) if destination.exists() else []
        previous_path=st.selectbox('Packet trước (tùy chọn)',[None,*previous_files],format_func=lambda p:'Không có' if p is None else p.name)
        if st.button('Build Packet → Validate'):
            packet=build_packet(**state,angle_id=angle_id,project_goal=goal,
                previous=load_packet(previous_path) if previous_path else None)
            save_packet(packet,destination/(packet.packet_id+'.json'),**inputs())
            st.session_state['packet_preview_path']=str(destination/(packet.packet_id+'.json'))
        saved=st.session_state.get('packet_preview_path')
        if saved and Path(saved).parent.resolve()==destination.resolve():
            packet=load_packet(saved)
            validate_current(packet,**inputs())
            st.success('PASS — snapshot và current governance/selection hợp lệ.')
            st.write('Packet',packet.packet_id,'Revision',packet.packet_revision)
            st.subheader('ZONE A — Customer Truth (bất biến)'); st.json(packet.customer_truth.model_dump(mode='json'))
            st.subheader('ZONE B — Selected Strategy (PROPOSED)'); st.json(packet.content_strategy.model_dump(mode='json'))
            st.subheader('ZONE C — Writer permissions'); st.json(packet.creative_execution.model_dump())
            st.subheader('External evidence still required'); st.json([r.model_dump() for r in packet.external_evidence_requirements])
            st.download_button('Export packet JSON',packet.model_dump_json(indent=2),'content_intelligence_packet.json',mime='application/json')
            st.download_button('Preview Markdown — view only',packet_preview(packet),'content_packet_preview.md',mime='text/markdown')
            # Configuration is operator-owned; web users cannot choose executable or code paths.
            import os, json
            from uuid import uuid4
            configured = os.environ.get('REELO_CONFIG')
            if configured:
                from .reelo_dispatch import send_packet
                request_key = 'reelo_request_' + packet.packet_id
                if request_key not in st.session_state:
                    st.session_state[request_key] = 'UI-' + uuid4().hex
                if st.button('Send to Reelo (draft)'):
                    config = json.loads(Path(configured).read_text(encoding='utf-8'))
                    result = send_packet(packet, load_current=inputs, config=config,
                                         request_id=st.session_state[request_key])
                    st.session_state['reelo_result_' + packet.packet_id] = result.model_dump(mode='json')
                result = st.session_state.get('reelo_result_' + packet.packet_id)
                if result:
                    st.json(result)
    except (OSError,ValueError):
        st.error('FAIL — packet hoặc upstream không hợp lệ/đã cũ. Kiểm tra current ledger và xuất lại lựa chọn; không export packet này.')
