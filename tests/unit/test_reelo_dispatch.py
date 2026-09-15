"""Currentness belongs to the producer, independently of consumer snapshot validation."""
import pytest

from tests.fixtures.content_packet_fixture import synthetic_state, synthetic_packet
from tiktok_insight_miner.reelo_dispatch import send_packet


def test_send_requires_all_explicit_operator_configuration():
    with pytest.raises(ValueError, match='explicit'):
        send_packet(None, load_current=lambda: {}, config={}, request_id='r')


@pytest.mark.parametrize('effort', [None, 'medium'])
def test_dispatch_reloads_authoritative_state_before_adapter(monkeypatch, tmp_path, effort):
    import tiktok_insight_miner.reelo_dispatch as module
    from types import SimpleNamespace
    state = synthetic_state()
    packet = synthetic_packet(state)
    calls = []
    class Store:
        def __init__(self, path): calls.append('store')
    def dispatch(store, raw, *, authorize_current, **kwargs):
        authorize_current(raw)
        return 'sent'
    adapter = SimpleNamespace(IntakeStore=Store, dispatch=dispatch)
    configs = []
    host = SimpleNamespace(HostConfig=lambda **kw: configs.append(kw) or kw, NativeHost=lambda cfg: None)
    monkeypatch.setattr(module, 'consumer_modules', lambda path: (adapter, host))
    monkeypatch.setenv('LOCALAPPDATA', str(tmp_path))
    config = dict(execution_workspace=str(tmp_path), executable=str(tmp_path/'claude.exe'),
                  state_directory=str(tmp_path/'state'), read_files=[])
    if effort is not None: config['effort_level'] = effort
    def load():
        calls.append('load')
        return state
    assert send_packet(packet, load_current=load, config=config, request_id='r') == 'sent'
    assert calls == ['load', 'store', 'load']
    assert configs[-1]['effort_level'] == effort
    broken = dict(state)
    broken['selected'] = state['selected'].model_copy(deep=True)
    broken['selected'].selected_angles.clear()
    calls.clear()
    with pytest.raises(ValueError):
        send_packet(packet, load_current=lambda: broken, config=config, request_id='r')
    assert 'store' not in calls
