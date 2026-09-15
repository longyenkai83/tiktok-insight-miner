"""No AI reviewer, no auto-approval, no automatic priority scoring."""
import hashlib
import json
from .evidence_models import EvidenceBundle
from .governance_models import (HumanReview, PriorityDecision, ReviewAction, ReviewEvent,
    ReviewQueue, VerifiedInsight, VerifiedInsightsEnvelope, VerifiedStatement)
from .insight_models import InsightCandidate, InsightsEnvelope
from .insight_validator import candidate_issues
from .pattern_models import artifact_hash

APPROVALS = {"approved", "edited_and_approved"}


def value_hash(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def event_identity(event):
    data = event.model_dump(mode="json")
    data.pop("review_event_id")
    return "REV-" + value_hash(data)


def find_candidate(snapshot, candidate_id):
    found = [i for i in snapshot.insights if i.insight_id == candidate_id]
    if len(found) != 1:
        raise ValueError("candidate ID is not in the machine-accepted review queue")
    return found[0]


def validate_action(snapshot, action):
    candidate = find_candidate(snapshot, action.candidate_insight_id)
    if action.candidate_hash != artifact_hash(candidate):
        raise ValueError("stale candidate hash; review the current candidate")
    if action.decision == "edited_and_approved":
        if action.edited_statement == candidate.statement.text:
            raise ValueError("edited approval requires changed text; use approved")
        transport = InsightCandidate(insight_candidate_id=candidate.insight_id,
            support_pattern_ids=candidate.support_pattern_ids,
            relationship_type=candidate.relationship_type, concise_statement=action.edited_statement)
        # Reuse deterministic integrity guards only; no semantic reviewer and no AI veto.
        issues = [i for i in candidate_issues(transport, snapshot.input_patterns)
                  if i.code != "shallow_statement"]
        if issues:
            raise ValueError("edited statement integrity: " + ", ".join(sorted({i.code for i in issues})))
    return candidate


def validate_history(queue):
    snapshots = {artifact_hash(s): s for s in queue.snapshots}
    if len(snapshots) != len(queue.snapshots):
        raise ValueError("duplicate analysis snapshot")
    positions = {h: n for n, h in enumerate(snapshots)}
    previous, seen_requests, position = None, set(), 0
    for n, event in enumerate(queue.events, 1):
        if event.source_insights_hash not in snapshots:
            raise ValueError("review references unknown analysis snapshot")
        new_position = positions[event.source_insights_hash]
        if new_position < position:
            raise ValueError("cannot append review to superseded analysis snapshot")
        position = new_position
        if event.sequence != n or event.previous_event_id != previous or event.review_event_id != event_identity(event):
            raise ValueError("broken append-only review chain")
        if event.action.request_id in seen_requests:
            raise ValueError("duplicate review request ID")
        seen_requests.add(event.action.request_id)
        candidate = validate_action(snapshots[event.source_insights_hash], event.action)
        approved = (event.action.edited_statement if event.action.decision == "edited_and_approved"
                    else candidate.statement.text if event.action.decision == "approved" else None)
        if event.original_statement != candidate.statement.text or event.approved_statement != approved:
            raise ValueError("review text does not match original candidate and explicit human action")
        previous = event.review_event_id


def checked_queue(queue):
    return ReviewQueue.model_validate(queue.model_dump())


def prepare_review(insights, previous=None):
    insights = InsightsEnvelope.model_validate(insights.model_dump())
    if previous is None:
        return ReviewQueue(snapshots=[insights])
    queue = checked_queue(previous)
    incoming = artifact_hash(insights)
    hashes = [artifact_hash(s) for s in queue.snapshots]
    if incoming == hashes[-1]:
        return queue
    if incoming in hashes:
        raise ValueError("historical analysis cannot silently replace current revision")
    return ReviewQueue(snapshots=[*queue.snapshots, insights], events=queue.events)


def record_review(queue, action):
    queue = checked_queue(queue)
    action = ReviewAction.model_validate(action.model_dump())
    snapshot = queue.snapshots[-1]
    source_hash = artifact_hash(snapshot)
    prior = next((e for e in queue.events if e.action.request_id == action.request_id), None)
    if prior:
        if prior.action == action and prior.source_insights_hash == source_hash:
            return queue  # Explicit retry, not a second decision.
        raise ValueError("request ID already used for a different action or analysis")
    candidate = validate_action(snapshot, action)
    approved = (action.edited_statement if action.decision == "edited_and_approved"
                else candidate.statement.text if action.decision == "approved" else None)
    event = ReviewEvent(review_event_id="pending", sequence=len(queue.events) + 1,
        previous_event_id=queue.events[-1].review_event_id if queue.events else None,
        source_insights_hash=source_hash, action=action,
        original_statement=candidate.statement.text, approved_statement=approved)
    event.review_event_id = event_identity(event)
    return ReviewQueue(snapshots=queue.snapshots, events=[*queue.events, event])


def project_verified(queue):
    snapshots = {artifact_hash(s): s for s in queue.snapshots}
    current_hash = artifact_hash(queue.snapshots[-1])
    latest, revisions, predecessors, built = {}, {}, {}, {}
    for event in queue.events:
        action = event.action
        key = (event.source_insights_hash, action.candidate_insight_id)
        latest[key] = event
        if action.decision not in APPROVALS:
            continue
        candidate = find_candidate(snapshots[event.source_insights_hash], action.candidate_insight_id)
        cid = candidate.insight_id
        revisions[cid] = revisions.get(cid, 0) + 1
        vid = "VER-" + value_hash({"event": event.review_event_id, "candidate": action.candidate_hash})
        evidence = {field: getattr(candidate, field) for field in EvidenceBundle.model_fields}
        built[event.review_event_id] = VerifiedInsight(**evidence,
            verified_insight_id=vid, source_candidate_id=cid, source_candidate_hash=action.candidate_hash,
            source_insights_hash=event.source_insights_hash, revision=revisions[cid], supersedes=predecessors.get(cid),
            statement=VerifiedStatement(text=event.approved_statement,
                statement_origin="human_edited" if action.decision == "edited_and_approved" else "machine_approved"),
            relationship_type=candidate.relationship_type, support_pattern_ids=candidate.support_pattern_ids,
            human_review=HumanReview(review_event_id=event.review_event_id, reviewer_id=action.reviewer_id,
                reviewed_at=event.reviewed_at, decision=action.decision, rationale=action.rationale),
            priority=action.priority)
        predecessors[cid] = vid
    return [built[event.review_event_id] for candidate in queue.snapshots[-1].insights
            if (event := latest.get((current_hash, candidate.insight_id))) and event.action.decision in APPROVALS]


def apply_reviews(queue):
    queue = checked_queue(queue)
    return VerifiedInsightsEnvelope(input_reviews_hash=artifact_hash(queue), review_history=queue,
                                    verified_insights=project_verified(queue))


def require_verified(artifact, current_reviews):
    """Downstream boundary requires full provenance AND the current authoritative ledger.

    Callers must load current_reviews from trusted storage, not an untrusted packet.
    A standalone flag/VerifiedInsight object is insufficient, including after revocation.
    """
    if not isinstance(artifact, VerifiedInsightsEnvelope):
        raise ValueError("downstream requires v2.verified-insights.1 and human approval")
    verified = VerifiedInsightsEnvelope.model_validate(artifact.model_dump())
    current = checked_queue(current_reviews)
    if artifact_hash(current) != verified.input_reviews_hash:
        raise ValueError("stale verified artifact; rebuild against current human review history")
    return verified.verified_insights


def review_rows(queue, state="All", sort_by="support count"):
    queue = checked_queue(queue)
    source_hash = artifact_hash(queue.snapshots[-1])
    latest = {e.action.candidate_insight_id: e for e in queue.events if e.source_insights_hash == source_hash}
    rows = []
    for candidate in queue.snapshots[-1].insights:
        event = latest.get(candidate.insight_id)
        decision = event.action.decision if event else "pending"
        priority = event.action.priority if event and decision in APPROVALS else PriorityDecision()
        matches = {"All": True, "Pending": decision == "pending", "Approved": decision in APPROVALS,
            "Rejected": decision == "rejected", "Deferred": decision == "deferred",
            "Priority Needs": priority.priority_status == "priority_need"}
        if state not in matches:
            raise ValueError("unknown review filter")
        if matches[state]:
            rows.append(dict(candidate=candidate, decision=decision, event=event, priority=priority))
    def metric(row):
        c = row["candidate"]
        return {"support count": c.evidence_summary.comment_count,
                "source count": c.evidence_summary.source_count,
                "contradiction count": len(c.contradictions)}[sort_by]
    return sorted(rows, key=lambda r: (metric(r) is None, -(metric(r) or 0), r["candidate"].insight_id))
