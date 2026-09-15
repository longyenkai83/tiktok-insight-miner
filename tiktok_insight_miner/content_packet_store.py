"""Immutable packet files; JSON is authoritative, preview is a read-only view."""
import json
from pathlib import Path

from .content_packet_models import ContentIntelligencePacket
from .content_packet_validator import validate_current
from .governance_store import atomic_json, file_lock


def load_packet(path):
    return ContentIntelligencePacket.model_validate_json(Path(path).read_text(encoding='utf-8'))


def save_packet(packet,path,*,verified,tree,selected,reviews,ledger):
    packet=validate_current(packet,verified,tree,selected,reviews,ledger)
    path=Path(path)
    with file_lock(path):
        if path.exists():
            existing=load_packet(path)
            if existing != packet: raise ValueError('immutable_packet_choose_new_path')
            return existing
        atomic_json(path,packet)
    return packet


def packet_preview(packet):
    packet=ContentIntelligencePacket.model_validate(packet.model_dump())
    # JSON sections avoid interpreting embedded source prose as commands or markup.
    blocks=['# REELO SẼ NHẬN ĐƯỢC GÌ?',
        f'Packet: {packet.packet_id}; revision {packet.packet_revision}; {packet.schema_version}',
        'Snapshot integrity: PASS. Current authorization requires current-ledger validation.',
        'This is a view, not the JSON contract. No Reelo call or publication has occurred.']
    for label,value in [('ZONE A — CUSTOMER TRUTH',packet.customer_truth),('ZONE B — SELECTED STRATEGY',packet.content_strategy),
                        ('ZONE C — WRITER PERMISSIONS',packet.creative_execution)]:
        blocks.extend(['\n## '+label,'```json',value.model_dump_json(indent=2),'```'])
    blocks.extend(['\n## External evidence still required','```json',json.dumps([r.model_dump() for r in packet.external_evidence_requirements],ensure_ascii=False,indent=2),'```'])
    return '\n\n'.join(blocks)+'\n'
