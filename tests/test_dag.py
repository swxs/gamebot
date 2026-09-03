from gamebot.dag import Group, Node


def test_linear_flow():
    group = Group(name="test")
    with group as group:
        visited = []

        def step_a(handler, hwnd):
            visited.append("a")
            return True

        def step_b(handler, hwnd):
            visited.append("b")
            return True

        a = Node("a", step_a)
        b = Node("b", step_b)
        group >> a >> b

    group.setup(None, None)
    names = list(group)
    assert names == ["a", "b"]
    assert visited == ["a", "b"]


def test_selector_blocks_transition():
    group = Group(name="test")
    with group as group:
        from gamebot.dag import Selector

        def always(handler, hwnd):
            return True

        def never(handler, hwnd):
            return False

        start = Node("start", always)
        blocked = Node("blocked", always)
        ok = Node("ok", always)

        guard = Selector("guard", never)
        group >> start >> guard >> blocked
        group >> start >> ok

    group.setup(None, None)
    names = list(group)
    assert names == ["start", "ok"]


def test_nested_group_structure():
    main = Group(name="main")
    with main as main:
        sub = Group(name="sub")
        with sub as sub:
            inner = Node("inner", lambda h, w: True)
            sub >> inner

    assert sub.level == 1
    assert inner.diag is sub
    assert any(node.name == "inner" for node in sub.nodes.values())
