"""Run intentionally from repo root: python -m tests.fixtures.export_content_packet_contract."""
import json
from pathlib import Path
from tests.fixtures.content_packet_fixture import synthetic_packet
from tiktok_insight_miner.content_packet_models import ContentIntelligencePacket

if __name__=='__main__':
    root=Path(__file__).resolve().parents[2]/'contracts'
    (root/'fixtures').mkdir(parents=True,exist_ok=True)
    (root/'content-intelligence-packet.schema.json').write_text(json.dumps(ContentIntelligencePacket.model_json_schema(),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (root/'fixtures/synthetic-content-intelligence-packet.json').write_text(synthetic_packet().model_dump_json(indent=2)+'\n',encoding='utf-8')
