"""Human angle selection with append-only JSON history; shared atomic/lock primitives."""
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator, model_validator

from .content_route_engine import checked_tree
from .content_route_models import ContentTree
from .governance_engine import value_hash
from .governance_store import atomic_json, file_lock
from .pattern_models import artifact_hash
from .signal_models import StrictModel


class SelectionAction(StrictModel):
    request_id: str = Field(min_length=1, max_length=100)
    tree_hash: str
    angle_id: str
    angle_hash: str
    decision: Literal["selected", "rejected", "deferred"]
    reviewer_id: str = Field(min_length=1, max_length=120)
    human_attested: Literal[True]
    rationale: str = Field(default="", max_length=8000)

    @field_validator("request_id", "reviewer_id")
    @classmethod
    def nonblank(cls, value):
        if not value.strip():
            raise ValueError("request and reviewer must not be blank")
        return value


class SelectionEvent(StrictModel):
    selection_event_id: str
    previous_event_id: str | None
    sequence: int = Field(ge=1)
    action: SelectionAction
    selected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


def selection_event_id(event):
    data = event.model_dump(mode="json")
    data.pop("selection_event_id")
    return "SEL-" + value_hash(data)


class SelectionLedger(StrictModel):
    schema_version: Literal["v2.content-selection-history.1"] = "v2.content-selection-history.1"
    trees: list[ContentTree] = Field(min_length=1)
    events: list[SelectionEvent] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_history(self):
        from .angle_correction import supersessions, PRODUCER
        trees = {artifact_hash(t): t for t in self.trees}
        if len(trees) != len(self.trees):
            raise ValueError("duplicate tree snapshot")
        indexes = {h: n for n, h in enumerate(trees)}
        for i, tree in enumerate(self.trees):
            corrections = [b for b in tree.batches if b.producer == PRODUCER]
            if not corrections:
                if i and supersessions(self.trees[i-1]):
                    raise ValueError('cannot_drop_owner_correction_history')
                continue
            if not i:
                raise ValueError('correction_requires_historical_selection')
            old_tree = self.trees[i-1]
            if tree.batches[:len(old_tree.batches)] != old_tree.batches:
                raise ValueError('correction_history_must_be_append_only')
            for b in tree.batches[len(old_tree.batches):]:
                if b.producer != PRODUCER:
                    continue
                r = b.payload['owner_correction']
                prior_events = [e for e in self.events if indexes[e.action.tree_hash] < i]
                prefix = SelectionLedger.model_construct(trees=self.trees[:i], events=prior_events)
                selected = selection_projection(prefix)
                if (artifact_hash(prefix) != r['previous_selection_hash'] or
                        not any(s.angle_id == r['previous_angle_id'] and
                                s.selection_event_id == r['previous_selection_event_id'] for s in selected)):
                    raise ValueError('owner_correction_selection_lineage_mismatch')
        previous, requests, position = None, set(), 0
        for n, event in enumerate(self.events, 1):
            a = event.action
            if a.tree_hash not in trees or indexes[a.tree_hash] < position:
                raise ValueError("unknown or historical selection tree")
            position = indexes[a.tree_hash]
            angle = next((a2 for a2 in trees[a.tree_hash].angles if a2.angle_id == a.angle_id), None)
            if angle is None or artifact_hash(angle) != a.angle_hash:
                raise ValueError("stale or unknown angle")
            if a.decision == 'selected' and a.angle_id in supersessions(trees[a.tree_hash]):
                raise ValueError('superseded_angle_cannot_be_selected')
            if event.sequence != n or event.previous_event_id != previous or event.selection_event_id != selection_event_id(event):
                raise ValueError("broken selection history chain")
            if event.selected_at.tzinfo is None or a.request_id in requests:
                raise ValueError("invalid selection timestamp or duplicate request")
            requests.add(a.request_id)
            previous = event.selection_event_id
        return self


class SelectedAngle(StrictModel):
    angle_id: str
    angle_hash: str
    tree_hash: str
    project_id: str
    run_id: str
    verified_insight_id: str
    topic_id: str
    content_opportunity_id: str
    selection_event_id: str
    reviewer_id: str
    selected_at: datetime
    selection_rationale: str
    truth_type: Literal["PROPOSED"] = "PROPOSED"
    status: Literal["selected"] = "selected"


def selection_projection(ledger):
    from .angle_correction import supersessions
    tree = ledger.trees[-1]
    h = artifact_hash(tree)
    latest = {e.action.angle_id: e for e in ledger.events if e.action.tree_hash == h}
    return [SelectedAngle(angle_id=a.angle_id, angle_hash=artifact_hash(a), tree_hash=h,
        project_id=a.project_id, run_id=a.run_id, verified_insight_id=a.verified_insight_id,
        topic_id=a.topic_id, content_opportunity_id=a.content_opportunity_id,
        selection_event_id=e.selection_event_id, reviewer_id=e.action.reviewer_id,
        selected_at=e.selected_at, selection_rationale=e.action.rationale)
        for a in tree.angles if a.angle_id not in supersessions(tree)
        and (e := latest.get(a.angle_id)) and e.action.decision == "selected"]


class SelectedAnglesEnvelope(StrictModel):
    schema_version: Literal["v2.selected-content-angles.1"] = "v2.selected-content-angles.1"
    input_selection_hash: str
    selection_history: SelectionLedger
    selected_angles: list[SelectedAngle]

    @model_validator(mode="after")
    def replay(self):
        if self.input_selection_hash != artifact_hash(self.selection_history) or self.selected_angles != selection_projection(self.selection_history):
            raise ValueError("selected output must match explicit current human decisions")
        return self


def prepare_selection(tree, reviews, previous=None):
    tree = checked_tree(tree, reviews)
    if previous is None:
        return SelectionLedger(trees=[tree])
    old = SelectionLedger.model_validate(previous.model_dump())
    h = artifact_hash(tree)
    if h == artifact_hash(old.trees[-1]):
        return old
    if h in {artifact_hash(t) for t in old.trees}:
        raise ValueError("cannot reactivate historical content tree")
    from .angle_correction import supersessions
    if supersessions(old.trees[-1]) and tree.batches[:len(old.trees[-1].batches)] != old.trees[-1].batches:
        raise ValueError('cannot_drop_owner_correction_history')
    return SelectionLedger(trees=[*old.trees, tree], events=old.events)


def select_angle(ledger, reviews, action):
    ledger = SelectionLedger.model_validate(ledger.model_dump())
    checked_tree(ledger.trees[-1], reviews)
    action = SelectionAction.model_validate(action.model_dump())
    if action.tree_hash != artifact_hash(ledger.trees[-1]):
        raise ValueError("stale selection tree")
    prior = next((e for e in ledger.events if e.action.request_id == action.request_id), None)
    if prior:
        if prior.action == action:
            return ledger
        raise ValueError("request ID already used")
    event = SelectionEvent(selection_event_id="pending", previous_event_id=ledger.events[-1].selection_event_id if ledger.events else None,
        sequence=len(ledger.events) + 1, action=action)
    event.selection_event_id = selection_event_id(event)
    return SelectionLedger(trees=ledger.trees, events=[*ledger.events, event])


def apply_selection(ledger, reviews):
    ledger = SelectionLedger.model_validate(ledger.model_dump())
    checked_tree(ledger.trees[-1], reviews)
    return SelectedAnglesEnvelope(input_selection_hash=artifact_hash(ledger), selection_history=ledger,
                                  selected_angles=selection_projection(ledger))


def require_selected(artifact, current_selection, current_reviews):
    if not isinstance(artifact, SelectedAnglesEnvelope):
        raise ValueError("typed human-selected angles required")
    artifact = SelectedAnglesEnvelope.model_validate(artifact.model_dump())
    current = SelectionLedger.model_validate(current_selection.model_dump())
    checked_tree(current.trees[-1], current_reviews)
    if artifact.input_selection_hash != artifact_hash(current):
        raise ValueError("stale angle selection export")
    return artifact.selected_angles


def load_tree(path):
    return ContentTree.model_validate_json(Path(path).read_text(encoding="utf-8"))


def save_tree(tree, path, reviews, *, expected_hash=None):
    tree = checked_tree(tree, reviews)
    path = Path(path)
    with file_lock(path):
        if path.exists():
            old = load_tree(path)
            if expected_hash != artifact_hash(old):
                raise ValueError("content tree changed; reload before generating")
            if old.verified_input != tree.verified_input or tree.batches[:len(old.batches)] != old.batches:
                raise ValueError("cannot overwrite tree provenance/history; start a new run")
        elif expected_hash is not None:
            raise ValueError("expected content tree missing")
        atomic_json(path, tree)


def load_selection(path):
    return SelectionLedger.model_validate_json(Path(path).read_text(encoding="utf-8"))


def prepare_selection_file(tree, reviews, path):
    path = Path(path)
    with file_lock(path):
        old = load_selection(path) if path.exists() else None
        new = prepare_selection(tree, reviews, old)
        if new != old:
            atomic_json(path, new)
        return new


def select_angle_file(path, reviews, action, *, expected_history_hash):
    path = Path(path)
    with file_lock(path):
        old = load_selection(path)
        prior = any(e.action.request_id == action.request_id for e in old.events)
        if not prior and artifact_hash(old) != expected_history_hash:
            raise ValueError("angle selection history changed; reload")
        new = select_angle(old, reviews, action)
        if new.events[:len(old.events)] != old.events:
            raise ValueError("selection history must be append-only")
        if new != old:
            atomic_json(path, new)
        return new


def export_selection_file(path, output, reviews):
    path, output = Path(path), Path(output)
    if path.resolve() == output.resolve():
        raise ValueError("export cannot overwrite selection history")
    with file_lock(path):
        result = apply_selection(load_selection(path), reviews)
        with file_lock(output):
            if output.exists():
                SelectedAnglesEnvelope.model_validate_json(output.read_text(encoding="utf-8"))
            atomic_json(output, result)
        return result
