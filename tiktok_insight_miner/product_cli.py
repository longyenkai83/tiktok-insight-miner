"""Opt-in product discovery and explicit human test decisions."""
import json
from pathlib import Path

from pydantic import ValidationError

from .governance_store import load_reviews, load_verified
from .pattern_models import artifact_hash
from .product_engine import AnthropicProducts, build_discovery
from .product_store import (ProductAction, decide_product_file, export_products, load_discovery,
    prepare_product_file, save_discovery)


def run_products(args):
    try:
        reviews = load_reviews(args.reviews)
        if args.command == 'build-product-opportunities':
            if Path(args.output).exists(): raise ValueError('choose_new_product_output')
            tree = build_discovery(load_verified(args.verified_insights), reviews,
                project_id=args.project_id, run_id=args.run_id, count=args.count, provider=AnthropicProducts(args.model))
            save_discovery(tree, args.output, load_reviews(args.reviews))
            print(json.dumps(dict(opportunities=len(tree.opportunities), issues=[i.model_dump() for i in tree.validation_issues])))
            if tree.validation_issues: raise SystemExit(2)
            return
        tree = load_discovery(args.tree)
        if Path(args.tree).resolve() == Path(args.decisions).resolve(): raise ValueError('separate_tree_and_decisions_required')
        ledger = prepare_product_file(tree, reviews, args.decisions)
        if args.command == 'select-product-opportunity':
            action = ProductAction(request_id=args.request_id, tree_hash=args.tree_hash,
                product_opportunity_id=args.opportunity_id, opportunity_hash=args.opportunity_hash,
                decision=args.decision, reviewer_id=args.reviewer, human_attested=args.confirm_human,
                rationale=args.rationale, assumption_to_test_first=args.assumption,
                assumption_importance=args.importance, riskiest_assumption=args.riskiest_assumption)
            ledger = decide_product_file(args.decisions, load_discovery(args.tree), load_reviews(args.reviews), action,
                                          expected_history_hash=artifact_hash(ledger))
        elif args.command == 'export-product-selection':
            result = export_products(args.decisions, args.output, load_discovery(args.tree), load_reviews(args.reviews))
            print(f'Opportunities selected for testing: {len(result.selected_opportunities)}')
            return
        print(json.dumps(dict(tree_hash=artifact_hash(tree), decision_history_hash=artifact_hash(ledger),
            opportunities=[dict(opportunity_id=o.product_opportunity_id, opportunity_hash=artifact_hash(o),
                assumptions=[a.assumption_id for a in tree.assumptions if a.product_opportunity_id == o.product_opportunity_id]) for o in tree.opportunities])))
    except (ValueError, OSError) as exc:
        code = 'schema_or_provenance_invalid' if isinstance(exc, ValidationError) else str(exc)
        raise SystemExit('Product discovery error: '+code) from None


def add_product_commands(sub):
    p = sub.add_parser('build-product-opportunities', help='V2: Priority Needs to proposed solutions and test plans')
    for name in ('verified-insights', 'reviews', 'project-id', 'run-id'):
        p.add_argument('--'+name, required=True)
    p.add_argument('-o', '--output', required=True)
    p.add_argument('--count', type=int, default=3)
    p.add_argument('--model')
    p.set_defaults(func=run_products)
    for name in ('prepare-product-selection', 'select-product-opportunity', 'export-product-selection'):
        p = sub.add_parser(name, help='V2: human choice for testing, never product validation')
        for flag in ('tree', 'reviews', 'decisions'): p.add_argument('--'+flag, required=True)
        if name == 'select-product-opportunity':
            for flag in ('tree-hash', 'opportunity-id', 'opportunity-hash', 'request-id', 'reviewer', 'rationale'):
                p.add_argument('--'+flag, required=True)
            p.add_argument('--confirm-human', required=True, action='store_true')
            p.add_argument('--decision', choices=['explore', 'reject', 'defer'], required=True)
            p.add_argument('--assumption')
            p.add_argument('--importance', choices=['high', 'medium', 'low', 'unknown'], default='unknown')
            p.add_argument('--riskiest-assumption', action='store_true', help='Human marks the chosen assumption as riskiest')
        if name == 'export-product-selection': p.add_argument('-o', '--output', required=True)
        p.set_defaults(func=run_products)
