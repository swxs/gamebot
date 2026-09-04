import json
import http.client
import socket

import pytest

from gamebot.dag import Group, Node
from gamebot.dashboard import StateHub, build_snapshot, serialize_graph, start_dashboard


def _setup(group, extra=None):
    vars = {"k": 0}
    if extra:
        vars.update(extra)
    group.setup(vars)


def test_serialize_graph_linear():
    group = Group(name="main")
    with group as group:
        a = Node("a", lambda ctx: True)
        b = Node("b", lambda ctx: True)
        group >> a >> b

    data = serialize_graph(group)
    assert data["root"] == "main"
    ids = {n["id"] for g in data["groups"] for n in g["nodes"]}
    assert ids == {"main.a", "main.b"}
    assert {"from": "main.a", "to": "main.b"} in data["edges"]


def test_serialize_graph_nested():
    main = Group(name="main")
    with main as main:
        sub = Group(name="sub")
        with sub as sub:
            inner = Node("inner", lambda ctx: True)
            sub >> inner
        end = Node("end", lambda ctx: True)
        main >> sub
        inner >> end

    data = serialize_graph(main)
    sub_group = next(g for g in data["groups"] if g["name"] == "sub")
    assert sub_group["parent"] == "main"
    ids = {n["id"] for g in data["groups"] for n in g["nodes"]}
    assert "sub.inner" in ids
    assert "main.end" in ids
    assert all("__start" not in n["id"] for g in data["groups"] for n in g["nodes"])


def test_build_snapshot_vars_active():
    root = Group(name="root")
    with root as root:
        sub = Group(name="sub")
        with sub as sub:

            def write(ctx):
                ctx.set("x", 2)
                return True

            sub >> Node("inner", write)
        root >> sub

    _setup(root, {"x": 1})
    next(iter(root))
    snap = build_snapshot(root, turn=0)
    assert snap["vars"]["x"] == 1
    assert snap["vars_active_group"] == "sub"
    assert snap["vars_active"]["x"] == 2
    assert snap["current"] == "sub.inner"


class _FakePkg:
    pass


def test_build_snapshot_packages():
    group = Group(name="g")
    with group as group:
        group >> Node("a", lambda ctx: True)
    group.setup({"packages": {"desktop": _FakePkg()}})
    snap = build_snapshot(group)
    assert snap["packages"]["desktop"] == "_FakePkg"


def test_state_hub_publish():
    hub = StateHub()
    q = hub.subscribe()
    hub.publish({"turn": 0})
    assert q.get(timeout=1)["turn"] == 0
    hub.publish({"turn": 1})
    assert q.get(timeout=1)["turn"] == 1
    assert hub.snapshot()["turn"] == 1


def _free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def test_dashboard_http_endpoints():
    group = Group(name="main")
    with group as group:
        group >> Node("a", lambda ctx: True)

    hub = StateHub()
    graph = serialize_graph(group)
    hub.publish(build_snapshot(group))
    port = _free_port()
    start_dashboard(hub, graph, port=port)

    def fetch(path):
        conn = http.client.HTTPConnection("127.0.0.1", port, timeout=2)
        conn.request("GET", path)
        resp = conn.getresponse()
        return resp.read()

    body = fetch("/api/graph")
    assert json.loads(body)["root"] == "main"
    snap = json.loads(fetch("/api/snapshot"))
    assert snap["dag"] == "main"
    html = fetch("/")
    assert b"gamebot dashboard" in html


def test_dashboard_port_busy():
    group = Group(name="main")
    hub = StateHub()
    graph = serialize_graph(group)
    port = _free_port()
    start_dashboard(hub, graph, port=port)
    with pytest.raises(RuntimeError, match="端口"):
        start_dashboard(StateHub(), graph, port=port)
