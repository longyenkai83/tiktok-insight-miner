"""Snapshot integrity is distinct from current authorization; consumers need both."""
from .content_route_models import GroundedScene
from .pattern_models import artifact_hash
from .signal_models import validate_source_span


def validate_snapshot(packet):
    from .content_packet_builder import evidence_refs, external_requirements, language_for, packet_identity, representatives
    if packet.created_at.tzinfo is None: raise ValueError('packet_time_requires_timezone')
    if (packet.packet_revision == 1) != (packet.supersedes_packet_id is None): raise ValueError('invalid_packet_revision')
    if packet.packet_id == packet.supersedes_packet_id: raise ValueError('packet_cannot_supersede_itself')
    if packet.packet_id != packet_identity(packet.model_dump(mode='json')): raise ValueError('packet_content_hash_mismatch')
    truth, strategy, lineage, selection = packet.customer_truth, packet.content_strategy, packet.lineage, packet.selection
    vi = truth.verified_insight
    if lineage.verified_insight_hash != artifact_hash(vi): raise ValueError('verified_insight_hash_mismatch')
    if lineage.source_candidate_id != vi.source_candidate_id or lineage.pattern_ids != vi.support_pattern_ids:
        raise ValueError('invalid_customer_lineage')
    if not (lineage.verified_insight_id == vi.verified_insight_id == selection.verified_insight_id): raise ValueError('insight_lineage_mismatch')
    if not (lineage.angle_id == selection.angle_id == strategy.angle.angle_id and
            lineage.topic_id == selection.topic_id == strategy.topic.topic_id and
            lineage.content_opportunity_id == selection.content_opportunity_id == strategy.opportunity.content_opportunity_id):
        raise ValueError('strategy_lineage_mismatch')
    if lineage.content_tree_hash != selection.tree_hash or lineage.angle_hash != selection.angle_hash:
        raise ValueError('selection_lineage_mismatch')
    if packet.project.project_id != selection.project_id or packet.project.research_run_id != selection.run_id:
        raise ValueError('project_lineage_mismatch')
    refs = list(evidence_refs(vi.model_dump(mode='json')))
    sources = {s.source_record_id:s for s in truth.source_snapshots}
    if len(sources) != len(truth.source_snapshots) or set(sources) != {r.source_record_id for r in refs}:
        raise ValueError('source_snapshot_set_mismatch')
    for r in refs:
        s = sources[r.source_record_id]
        validate_source_span(s,r.source_record_id,r.source_hash,r.start,r.end,r.evidence_quote)
        if r.comment_id != s.comment_id: raise ValueError('comment_id_mismatch')
    if lineage.comment_ids != sorted({r.comment_id for r in refs}) or lineage.source_hashes != sorted({s.snapshot_hash for s in sources.values()}):
        raise ValueError('source_lineage_mismatch')
    if packet.project.source_route_context != sorted({s.platform for s in sources.values() if s.platform}):
        raise ValueError('invented_source_route')
    if truth.language_bank != language_for(vi) or truth.representative_quotes != representatives(vi):
        raise ValueError('unsupported_customer_language_or_quote')
    if packet.external_evidence_requirements != external_requirements(strategy): raise ValueError('external_requirements_mismatch')
    for name in ('need_moment','current_struggle','desired_future'):
        scene = getattr(strategy.value_scene,name)
        if isinstance(scene,GroundedScene):
            r=scene.evidence_ref
            if r not in vi.evidence_refs or scene.text != r.evidence_quote or scene.truth_type != r.truth_type:
                raise ValueError('unsupported_value_scene')
            roles={'need_moment':('context.','behavior.trigger'),'current_struggle':('pains.','behavior.'),'desired_future':('gains.',)}
            if not r.signal_path.startswith(roles[name]): raise ValueError('unsupported_value_scene_role')
    return packet


def validate_current(packet, verified, tree, selected, reviews, ledger):
    from .content_packet_models import ContentIntelligencePacket
    from .content_packet_builder import snapshot_fields
    packet = ContentIntelligencePacket.model_validate(packet.model_dump())
    expected = snapshot_fields(verified,tree,selected,reviews,ledger,packet.lineage.angle_id,packet.project.project_goal)
    if any(getattr(packet,k) != v for k,v in expected.items()): raise ValueError('packet_is_stale_or_upstream_mismatched')
    return packet


def validate_revision(packet, previous):
    from .content_packet_models import ContentIntelligencePacket
    packet=ContentIntelligencePacket.model_validate(packet.model_dump())
    previous=ContentIntelligencePacket.model_validate(previous.model_dump())
    if packet.supersedes_packet_id != previous.packet_id or packet.packet_revision != previous.packet_revision+1:
        raise ValueError('broken_packet_revision_chain')
    if (packet.project.project_id,packet.project.research_run_id) != (previous.project.project_id,previous.project.research_run_id):
        raise ValueError('unrelated_packet_revision')
    return packet
