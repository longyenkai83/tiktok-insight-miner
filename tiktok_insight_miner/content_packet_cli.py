"""Explicit packet build/validation; no model, Writer or network call."""
import json
from pathlib import Path

from pydantic import ValidationError

from .content_packet_builder import build_packet
from .content_packet_store import load_packet, packet_preview, save_packet
from .content_packet_validator import validate_current
from .content_selection import SelectedAnglesEnvelope, load_selection, load_tree
from .governance_store import load_reviews, load_verified


INPUT_FLAGS=('verified_insights','content_tree','selection','reviews','selection_ledger')


def packet_inputs(args):
    return dict(verified=load_verified(args.verified_insights),tree=load_tree(args.content_tree),
        selected=SelectedAnglesEnvelope.model_validate_json(Path(args.selection).read_text(encoding='utf-8')),
        reviews=load_reviews(args.reviews),ledger=load_selection(args.selection_ledger))


def run_packet(args):
    try:
        if args.command=='build-content-packet':
            if Path(args.output).exists(): raise ValueError('immutable_packet_choose_new_path')
            current=packet_inputs(args)
            packet=build_packet(**current,angle_id=args.angle_id,project_goal=args.project_goal,
                                previous=load_packet(args.previous) if args.previous else None)
            # Re-read authoritative state after assembly; abort on concurrent changes.
            save_packet(packet,args.output,**packet_inputs(args))
            print(json.dumps(dict(packet_id=packet.packet_id,revision=packet.packet_revision,
                                  snapshot='PASS',current_authorization='PASS')))
            return
        packet=load_packet(args.packet)
        provided=[bool(getattr(args,k)) for k in INPUT_FLAGS]
        if any(provided) and not all(provided): raise ValueError('all_current_inputs_required')
        if all(provided): validate_current(packet,**packet_inputs(args))
        print(json.dumps(dict(packet_id=packet.packet_id,snapshot='PASS',
            current_authorization='PASS' if all(provided) else 'NOT_CHECKED_OFFLINE')))
        if args.preview: print(packet_preview(packet))
    except (OSError,ValueError) as exc:
        code='schema_or_provenance_invalid' if isinstance(exc,ValidationError) else str(exc)
        raise SystemExit('Packet validation FAIL: '+code) from None


def add_packet_commands(sub):
    build=sub.add_parser('build-content-packet',help='V2: portable snapshot from current human-selected angle')
    validate=sub.add_parser('validate-content-packet',help='V2: snapshot integrity; supply all ledgers to check current authorization')
    for parser in (build,validate):
        for flag in INPUT_FLAGS: parser.add_argument('--'+flag.replace('_','-'),required=parser is build)
        parser.set_defaults(func=run_packet)
    build.add_argument('--angle-id',required=True)
    build.add_argument('--project-goal',choices=['CONTENT','BOTH'],default='CONTENT')
    build.add_argument('--previous')
    build.add_argument('-o','--output',required=True)
    validate.add_argument('packet')
    validate.add_argument('--preview',action='store_true')
