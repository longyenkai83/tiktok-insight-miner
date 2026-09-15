"""Opt-in application service; re-read current ledgers before native Reelo dispatch."""
from __future__ import annotations

import hashlib
import importlib
import importlib.util
import json
import sys
from pathlib import Path

from .content_packet_cli import INPUT_FLAGS, packet_inputs
from .content_packet_models import ContentIntelligencePacket
from .content_packet_store import load_packet
from .content_packet_validator import validate_current


def consumer_modules(workspace: Path):
    """Load only the explicitly configured checkout's bounded consumer API.

    No sys.path mutation and no implicit import of a different installed checkout.
    Both checkouts are trusted local code, not paths supplied by packet/model data.
    """
    package = workspace.resolve()/'integrations/content_intelligence'
    if not (package/'__init__.py').is_file():
        raise ValueError('configured_reelo_consumer_missing')
    name = '_reelo_consumer_'+hashlib.sha256(str(package).encode()).hexdigest()[:16]
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, package/'__init__.py',
                                                    submodule_search_locations=[str(package)])
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return importlib.import_module(name+'.adapter'), importlib.import_module(name+'.host')


def send_packet(packet, *, load_current, config: dict, request_id: str, parent_id=None,
                launch_override=None, approval_id=None):
    required = {'execution_workspace', 'executable', 'state_directory', 'read_files'}
    optional = {'timeout_seconds', 'max_budget_usd', 'effort_level'}
    if not required <= set(config) or set(config) - required - optional:
        raise ValueError('reelo_config_requires_explicit_workspace_executable_local_state_and_read_files')
    workspace = Path(config['execution_workspace']).resolve()
    adapter, host = consumer_modules(workspace)
    state = Path(config['state_directory']).resolve()
    # State is machine local. Google Drive/OneDrive project storage is not a shared DB.
    local_root = __import__('os').environ.get('LOCALAPPDATA')
    if not local_root:
        raise ValueError('configured_local_native_host_required_on_this_machine')
    local = Path(local_root).resolve()
    if not state.is_relative_to(local):
        raise ValueError('reelo_state_must_be_under_localappdata')
    cfg = host.HostConfig(executable=Path(config['executable']), execution_workspace=workspace,
                          state_directory=state/'executions',
                          read_files=tuple(Path(p) for p in config['read_files']),
                          timeout_seconds=config.get('timeout_seconds', 600),
                          max_budget_usd=config.get('max_budget_usd', 5.0),
                          effort_level=config.get('effort_level'))
    def authorize(raw):
        current_packet = ContentIntelligencePacket.model_validate(raw)
        validate_current(current_packet, **load_current())
    if approval_id is not None:
        plans = importlib.import_module(adapter.__package__+'.creative_plan').PlanStore(state/'creative-plans.sqlite')
        assets = [dict(path=p.as_posix(), sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in cfg.read_files]
        plans.approved(approval_id, adapter.ContentIntelligenceContext(packet=adapter.ContentIntelligencePacket.model_validate(packet.model_dump(mode='json'))).model_dump(mode='json'), assets)
    # Current authorization is checked before consumer intake, including duplicate requests.
    authorize(packet.model_dump(mode='json'))
    return adapter.dispatch(adapter.IntakeStore(state/'intake.sqlite'), packet.model_dump(mode='json'),
                            request_id=request_id, authorize_current=authorize,
                            launch=launch_override or host.NativeHost(cfg, approval_id=approval_id), parent_id=parent_id)


def run_send(args):
    try:
        config = json.loads(Path(args.reelo_config).read_text(encoding='utf-8'))
        result = send_packet(load_packet(args.packet), load_current=lambda: packet_inputs(args),
                             config=config, request_id=args.request_id, parent_id=args.parent_generation_id, approval_id=args.approval_id)
        print(result.model_dump_json(indent=2))
        if result.status not in ('DRAFT_READY', 'RUNNING', 'RECEIVED', 'PLAN_PENDING_APPROVAL'):
            raise SystemExit(2)
    except (OSError, ValueError) as exc:
        # Pydantic errors can include private source text; don't dump their inputs.
        from pydantic import ValidationError
        code = 'schema_or_provenance_invalid' if isinstance(exc, ValidationError) else str(exc)
        raise SystemExit('Reelo dispatch FAIL: '+code) from None


def add_reelo_commands(sub):
    parser = sub.add_parser('send-content-packet', help='V2: current authorized packet -> configured Reelo host')
    parser.add_argument('packet')
    for flag in INPUT_FLAGS:
        parser.add_argument('--'+flag.replace('_', '-'), required=True)
    parser.add_argument('--reelo-config', required=True)
    parser.add_argument('--request-id', required=True, help='Reuse the same ID for a transport retry')
    parser.add_argument('--parent-generation-id', help='Explicit previous generation for a new creative version')
    parser.add_argument('--approval-id', help='Explicit current creative approval; omit to plan only')
    parser.set_defaults(func=run_send)
    review = sub.add_parser('review-reelo-plan', help='One local human gate: inspect or submit a review JSON')
    review.add_argument('--reelo-config', required=True)
    review.add_argument('--plan-id', required=True)
    review.add_argument('--review-file', help='Explicit human review JSON; omit to inspect plan')
    review.set_defaults(func=run_plan_review)


def run_plan_review(args):
    config = json.loads(Path(args.reelo_config).read_text(encoding='utf8'))
    adapter, _ = consumer_modules(Path(config['execution_workspace']))
    plans = importlib.import_module(adapter.__package__+'.creative_plan')
    state = Path(config['state_directory']).resolve()
    local = Path(__import__('os').environ['LOCALAPPDATA']).resolve()
    if not state.is_relative_to(local): raise ValueError('reelo_state_must_be_under_localappdata')
    store = plans.PlanStore(state/'creative-plans.sqlite')
    result = (store.review(args.plan_id, json.loads(Path(args.review_file).read_text(encoding='utf8')))
              if args.review_file else store.get(args.plan_id))
    print(json.dumps(result, ensure_ascii=False, indent=2))
