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
                launch_override=None):
    required = {'execution_workspace', 'executable', 'state_directory', 'read_files'}
    optional = {'timeout_seconds', 'max_budget_usd'}
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
                          max_budget_usd=config.get('max_budget_usd', 5.0))
    def authorize(raw):
        current_packet = ContentIntelligencePacket.model_validate(raw)
        validate_current(current_packet, **load_current())
    # Current authorization is checked before consumer intake, including duplicate requests.
    authorize(packet.model_dump(mode='json'))
    return adapter.dispatch(adapter.IntakeStore(state/'intake.sqlite'), packet.model_dump(mode='json'),
                            request_id=request_id, authorize_current=authorize,
                            launch=launch_override or host.NativeHost(cfg), parent_id=parent_id)


def run_send(args):
    try:
        config = json.loads(Path(args.reelo_config).read_text(encoding='utf-8'))
        result = send_packet(load_packet(args.packet), load_current=lambda: packet_inputs(args),
                             config=config, request_id=args.request_id, parent_id=args.parent_generation_id)
        print(result.model_dump_json(indent=2))
        if result.status not in ('DRAFT_READY', 'RUNNING', 'RECEIVED'):
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
    parser.set_defaults(func=run_send)
