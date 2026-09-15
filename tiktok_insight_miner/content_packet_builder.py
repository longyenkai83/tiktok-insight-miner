"""Deterministic snapshot assembly from current human-approved and human-selected state."""
from datetime import datetime, timezone

from .content_route_engine import checked_tree
from .content_route_models import ProposedText
from .content_selection import require_selected
from .governance_engine import require_verified, value_hash
from .pattern_models import EvidenceRef, artifact_hash
from .content_packet_models import (ContentIntelligencePacket, CustomerTruthZone, ExternalRequirement,
    LanguageBank, PacketAngle, PacketLineage, PacketOpportunity, PacketProject, PacketTopic, StrategyZone)


def evidence_refs(value):
    """Walk only the selected verified insight, including counter/context references."""
    if isinstance(value, dict):
        if 'evidence_id' in value and 'upstream_claim_id' in value:
            yield EvidenceRef.model_validate(value)
        else:
            for child in value.values(): yield from evidence_refs(child)
    elif isinstance(value, list):
        for child in value: yield from evidence_refs(child)


def language_for(vi):
    return LanguageBank(**{key:[r for r in vi.evidence_refs if r.signal_path == 'language.'+key]
                          for key in ('exact_phrases', 'emotional_wording', 'repeated_expressions')})


def representatives(vi):
    result, seen = [], set()
    for ref in vi.evidence_refs:
        if ref.source_record_id not in seen:
            result.append(ref); seen.add(ref.source_record_id)
        if len(result) == 5: break
    return result


def external_requirements(strategy):
    def walk(value, path):
        if isinstance(value, dict):
            if value.get('needs_external_evidence') is True and 'text' in value:
                yield ExternalRequirement(strategy_field=path, claim_needed=value['text'])
            else:
                for k, v in value.items(): yield from walk(v, path+'.'+k)
    return list(walk(strategy.model_dump(mode='json'), 'content_strategy'))


def packet_identity(data):
    return 'CIP-'+value_hash({k:v for k,v in data.items() if k != 'packet_id'})


def current_inputs(verified, tree, selected, reviews, ledger, angle_id):
    require_verified(verified, reviews)
    tree = checked_tree(tree, reviews)
    choices = require_selected(selected, ledger, reviews)
    if artifact_hash(tree) != artifact_hash(ledger.trees[-1]): raise ValueError('stale_content_tree')
    if tree.input_verified_hash != artifact_hash(verified): raise ValueError('mismatched_verified_artifact')
    selection = next((s for s in choices if s.angle_id == angle_id), None)
    if selection is None: raise ValueError('human_selected_angle_required')
    angle = next(a for a in tree.angles if a.angle_id == angle_id)
    vi = next((v for v in verified.verified_insights if v.verified_insight_id == selection.verified_insight_id), None)
    if vi is None or vi.verified_insight_id != angle.verified_insight_id: raise ValueError('mismatched_insight_angle')
    topic = next(t for t in tree.topics if t.topic_id == angle.topic_id)
    opp = next(o for o in tree.content_opportunities if o.content_opportunity_id == topic.content_opportunity_id)
    if topic.verified_insight_id != vi.verified_insight_id or opp.verified_insight_id != vi.verified_insight_id:
        raise ValueError('mismatched_strategy_lineage')
    return vi, angle, topic, opp, selection


def snapshot_fields(verified, tree, selected, reviews, ledger, angle_id, project_goal):
    vi, angle, topic, opp, selection = current_inputs(verified, tree, selected, reviews, ledger, angle_id)
    refs = list(evidence_refs(vi.model_dump(mode='json')))
    source_ids = {r.source_record_id for r in refs}
    snapshot = next(s for s in verified.review_history.snapshots if artifact_hash(s) == vi.source_insights_hash)
    sources = {r.source.source_record_id:r.source for r in snapshot.input_patterns.input_signals.records}
    if not source_ids <= sources.keys(): raise ValueError('missing_source_snapshot')
    captured = [sources[k] for k in sorted(source_ids)]
    batch = next(b for b in tree.batches if b.generation_id == angle.generation_id)
    strategy = StrategyZone(opportunity=PacketOpportunity(**opp.model_dump(include=set(PacketOpportunity.model_fields))),
        topic=PacketTopic(**topic.model_dump(include=set(PacketTopic.model_fields))),
        angle=PacketAngle(**angle.model_dump(include=set(PacketAngle.model_fields))), value_scene=angle.value_scene,
        content_objective=ProposedText(text=batch.content_objective, claim_kind='creative_framing') if batch.content_objective else None)
    return dict(project=PacketProject(project_id=tree.project_id, project_goal=project_goal, research_run_id=tree.run_id,
                    source_route_context=sorted({s.platform for s in captured if s.platform})),
        customer_truth=CustomerTruthZone(verified_insight=vi, language_bank=language_for(vi),
            representative_quotes=representatives(vi), source_snapshots=captured),
        content_strategy=strategy, external_evidence_requirements=external_requirements(strategy), selection=selection,
        lineage=PacketLineage(verified_insight_id=vi.verified_insight_id, source_candidate_id=vi.source_candidate_id,
            pattern_ids=vi.support_pattern_ids, comment_ids=sorted({r.comment_id for r in refs}),
            source_hashes=sorted({s.snapshot_hash for s in captured}), content_opportunity_id=opp.content_opportunity_id,
            topic_id=topic.topic_id, angle_id=angle.angle_id, governance_hash=artifact_hash(reviews),
            verified_artifact_hash=artifact_hash(verified), selection_hash=artifact_hash(ledger),
            selected_artifact_hash=artifact_hash(selected), content_tree_hash=artifact_hash(tree),
            verified_insight_hash=artifact_hash(vi), opportunity_hash=artifact_hash(opp), topic_hash=artifact_hash(topic),
            angle_hash=artifact_hash(angle)))


def build_packet(verified, tree, selected, reviews, ledger, *, angle_id, project_goal='CONTENT', previous=None, created_at=None):
    fields = snapshot_fields(verified, tree, selected, reviews, ledger, angle_id, project_goal)
    revision, supersedes = 1, None
    if previous is not None:
        previous = ContentIntelligencePacket.model_validate(previous.model_dump())
        if (previous.project.project_id, previous.project.research_run_id) != (tree.project_id, tree.run_id):
            raise ValueError('unrelated_previous_packet')
        if all(getattr(previous,k) == v for k,v in fields.items()): return previous
        revision, supersedes = previous.packet_revision+1, previous.packet_id
    # Construct once to compute the content address including canonical model defaults.
    data = dict(**fields, schema_version='v2.content-intelligence-packet.1', packet_revision=revision, supersedes_packet_id=supersedes,
                created_at=created_at or datetime.now(timezone.utc))
    shell = ContentIntelligencePacket.model_construct(packet_id='pending', **data)
    data['packet_id'] = packet_identity(shell.model_dump(mode='json'))
    return ContentIntelligencePacket(**data)
