"""Explicit content generation/selection; current governance ledger always required."""
import json
from pathlib import Path
from typing import get_args

from .content_route_engine import AnthropicContent, build_content_tree
from .content_route_models import AngleType
from .content_selection import (SelectionAction, export_selection_file, load_selection, load_tree,
    prepare_selection_file, save_tree, select_angle_file)
from .governance_store import load_reviews, load_verified
from .pattern_models import artifact_hash


def run_content_route(args):
    from pydantic import ValidationError
    try:
        reviews = load_reviews(args.reviews)
        if args.command == "build-content-tree":
            if Path(args.output).exists():
                raise ValueError("output already exists; choose a new run file")
            tree = build_content_tree(load_verified(args.verified_insights), reviews,
                project_id=args.project_id, run_id=args.run_id, opportunities=args.opportunities,
                topics=args.topics, angles=args.angles, content_objective=args.objective,
                angle_type_preference=args.angle_type, provider=AnthropicContent(model=args.model))
            save_tree(tree, args.output, load_reviews(args.reviews))
            print(json.dumps({"opportunities": len(tree.content_opportunities), "topics": len(tree.topics),
                "angles": len(tree.angles), "issues": [i.model_dump() for i in tree.validation_issues]}))
            if tree.validation_issues:
                raise SystemExit(2)
            return
        tree = load_tree(args.tree)
        ledger = prepare_selection_file(tree, reviews, args.selections)
        if args.command == "select-content-angle":
            action = SelectionAction(request_id=args.request_id, tree_hash=args.tree_hash,
                angle_id=args.angle_id, angle_hash=args.angle_hash, decision=args.decision,
                reviewer_id=args.reviewer, human_attested=args.confirm_human, rationale=args.rationale)
            ledger = select_angle_file(args.selections, load_reviews(args.reviews), action,
                                       expected_history_hash=artifact_hash(ledger))
        elif args.command == "export-content-selection":
            result = export_selection_file(args.selections, args.output, load_reviews(args.reviews))
            print(f"Human-selected angles: {len(result.selected_angles)} -> {args.output}")
            return
        print(json.dumps({"tree_hash": artifact_hash(tree), "selection_history_hash": artifact_hash(ledger),
            "events": len(ledger.events), "angles": [{"angle_id": a.angle_id, "angle_hash": artifact_hash(a),
            "topic_id": a.topic_id} for a in tree.angles]}, indent=2))
    except (OSError, ValueError) as exc:
        message = "schema/provenance validation failed; inspect local artifacts" if isinstance(exc, ValidationError) else str(exc)
        raise SystemExit("Content route error: " + message) from None


def add_content_commands(sub):
    build = sub.add_parser("build-content-tree", help="V2: proposed opportunities/topics/angles; no final writing")
    build.add_argument("--verified-insights", required=True)
    build.add_argument("--reviews", required=True, help="CURRENT authoritative Phase 5 review ledger")
    build.add_argument("--project-id", required=True)
    build.add_argument("--run-id", required=True)
    build.add_argument("-o", "--output", required=True)
    for option, default in (("opportunities", 2), ("topics", 2), ("angles", 3)):
        build.add_argument("--" + option, type=int, default=default)
    build.add_argument("--objective", default="")
    build.add_argument("--angle-type", choices=get_args(AngleType))
    build.add_argument("--model")
    build.set_defaults(func=run_content_route)
    for command in ("prepare-content-selection", "select-content-angle", "export-content-selection"):
        parser = sub.add_parser(command, help="V2: explicit human angle selection")
        parser.add_argument("--tree", required=True)
        parser.add_argument("--reviews", required=True)
        parser.add_argument("--selections", required=True)
        if command == "select-content-angle":
            for name in ("angle-id", "angle-hash", "tree-hash", "request-id", "reviewer"):
                parser.add_argument("--" + name, required=True)
            parser.add_argument("--confirm-human", required=True, action="store_true")
            parser.add_argument("--decision", choices=["selected", "rejected", "deferred"], required=True)
            parser.add_argument("--rationale", default="")
        if command == "export-content-selection":
            parser.add_argument("-o", "--output", required=True)
        parser.set_defaults(func=run_content_route)
