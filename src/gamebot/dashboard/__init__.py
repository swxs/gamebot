"""CLI dashboard — 本地浏览器状态面板。"""

from gamebot.dashboard.serialize import build_snapshot, serialize_graph
from gamebot.dashboard.server import StateHub, start_dashboard

__all__ = ["StateHub", "build_snapshot", "serialize_graph", "start_dashboard"]
