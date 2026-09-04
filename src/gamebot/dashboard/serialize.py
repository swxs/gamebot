"""DAG 图序列化与运行时快照。"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Set

from gamebot import core
from gamebot.dag import Group, Node, resolve_entry_node


def iter_groups(root: Group):
    yield root
    for sub in root.dags.values():
        yield from iter_groups(sub)


def node_id(node: Node) -> Optional[str]:
    if node.name == "__start":
        entry = resolve_entry_node(node)
        if entry.name == "__start" or entry.func is None:
            return None
        node = entry
    elif node.func is None:
        return None
    return f"{node.diag.name}.{node.name}"


def edge_endpoint(node: Node) -> Optional[str]:
    return node_id(node)


def serialize_graph(root: Group) -> dict:
    groups_out: List[dict] = []
    seen_edges: Set[tuple] = set()
    edges_out: List[dict] = []

    for group in iter_groups(root):
        parent = group.diag.name if group.diag else None
        nodes_out = []
        for node in group.nodes.values():
            if node.name == "__start" or node.func is None:
                continue
            nid = node_id(node)
            if nid:
                nodes_out.append({"id": nid, "name": node.name})
        groups_out.append({"name": group.name, "parent": parent, "nodes": nodes_out})

        for node in group.nodes.values():
            src = edge_endpoint(node)
            if not src:
                continue
            for nxt in node.next_list:
                dst = edge_endpoint(nxt)
                if not dst or src == dst:
                    continue
                key = (src, dst)
                if key not in seen_edges:
                    seen_edges.add(key)
                    edges_out.append({"from": src, "to": dst})

    return {"root": root.name, "groups": groups_out, "edges": edges_out}


def _json_value(value: Any) -> Any:
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, (list, tuple)):
        return [_json_value(v) for v in value]
    if isinstance(value, dict):
        return {str(k): _json_value(v) for k, v in value.items()}
    text = repr(value)
    return text[:200] + ("…" if len(text) > 200 else "")


def _pending_id(root: Group) -> Optional[str]:
    for group in iter_groups(root):
        if group._pending_target is not None:
            return node_id(group._pending_target)
    return None


def build_snapshot(root: Group, turn: int = 0) -> dict:
    current = node_id(root.current)
    active_group = root.current.diag
    vars_root = {k: _json_value(v) for k, v in root._vars.items()}
    vars_active: dict = {}
    vars_active_group: Optional[str] = None
    if active_group is not root:
        vars_active_group = active_group.name
        vars_active = {k: _json_value(v) for k, v in active_group._vars.items()}

    packages = {
        name: type(pkg).__name__
        for name, pkg in sorted(root._packages.items())
    }

    number_display = core.NUMBER
    return {
        "dag": root.name,
        "turn": turn,
        "current": current,
        "pending": _pending_id(root),
        "vars": vars_root,
        "vars_active": vars_active,
        "vars_active_group": vars_active_group,
        "env": {
            "NAME": core.NAME,
            "NUMBER": number_display,
            "DAG": core.DAG,
            "PIX": core.PIX,
        },
        "packages": packages,
    }
