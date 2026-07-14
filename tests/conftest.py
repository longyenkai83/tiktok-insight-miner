"""Pytest conftest — shared fixtures.

Bootstrap sys.path để test import package không cần `pip install -e .`.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root vào sys.path để tests import tiktok_insight_miner
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))
