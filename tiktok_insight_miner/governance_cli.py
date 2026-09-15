"""Independent explicit human commands; preparing/applying never approves."""
import json
from pathlib import Path

from .governance_engine import review_rows
from .governance_models import PriorityDecision, ReviewAction
from .governance_store import (apply_review_file, load_reviews, prepare_review_file,
                               record_review_file)
from .insight_engine import load_insights_json
from .pattern_models import artifact_hash


def run_governance(args):
    try:
        if args.command == "prepare-insight-review":
            if Path(args.insights).resolve() == Path(args.output).resolve():
                raise ValueError("review queue must not overwrite source insights")
            queue = prepare_review_file(load_insights_json(Path(args.insights)), Path(args.output))
        elif args.command == "record-insight-review":
            queue = load_reviews(Path(args.reviews))
            priority = PriorityDecision(priority_status=args.priority,
                **{field: getattr(args, field) for field in ("important", "urgent", "frequent", "expensive", "emotional_intensity")})
            action = ReviewAction(request_id=args.request_id, candidate_insight_id=args.candidate_id,
                candidate_hash=args.candidate_hash, reviewer_id=args.reviewer,
                human_attested=args.confirm_human, decision=args.decision, edited_statement=args.statement,
                rationale=args.rationale, priority=priority)
            queue = record_review_file(Path(args.reviews), action, expected_history_hash=artifact_hash(queue))
        else:
            result = apply_review_file(Path(args.reviews), Path(args.output))
            print(f"Verified Insights: {len(result.verified_insights)}; no automatic decisions -> {args.output}")
            return
        print(json.dumps({"history_hash": artifact_hash(queue), "review_events": len(queue.events),
            "candidates": [{"candidate_id": r["candidate"].insight_id,
                "candidate_hash": artifact_hash(r["candidate"]), "decision": r["decision"]}
                for r in review_rows(queue)]}, indent=2))
    except (OSError, ValueError) as exc:
        # ValidationError may embed private source values. Only safe custom ValueError details.
        from pydantic import ValidationError
        message = "schema/integrity validation failed; inspect local input" if isinstance(exc, ValidationError) else str(exc)
        raise SystemExit("Human review error: " + message) from None


def add_governance_commands(sub):
    prepare = sub.add_parser("prepare-insight-review", help="Prepare pending queue; never approve")
    prepare.add_argument("--insights", required=True)
    prepare.add_argument("-o", "--output", required=True)
    record = sub.add_parser("record-insight-review", help="Record an explicit human decision")
    record.add_argument("--reviews", required=True)
    record.add_argument("--candidate-id", required=True)
    record.add_argument("--candidate-hash", required=True, help="Exact hash shown by prepare-insight-review")
    record.add_argument("--request-id", required=True, help="Unique action ID; reuse only for exact retries")
    record.add_argument("--reviewer", required=True)
    record.add_argument("--confirm-human", action="store_true", required=True,
                        help="Attest this is the human's explicit decision, not an AI decision")
    record.add_argument("--decision", choices=["approved", "edited_and_approved", "rejected", "deferred"], required=True)
    record.add_argument("--statement", help="Edited statement, only for edited_and_approved")
    record.add_argument("--rationale", required=True)
    record.add_argument("--priority", choices=["unassessed", "monitor", "priority_need"], default="unassessed")
    for field in ("important", "urgent", "frequent", "expensive", "emotional_intensity"):
        record.add_argument("--" + field.replace("_", "-"), choices=["high", "medium", "low", "unknown"], default="unknown")
    apply = sub.add_parser("apply-insight-review", help="Project recorded approvals; never approve")
    apply.add_argument("--reviews", required=True)
    apply.add_argument("-o", "--output", required=True)
    for parser in (prepare, record, apply):
        parser.set_defaults(func=run_governance)
