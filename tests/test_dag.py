from gamebot.dag import Context, Group, Node, resolve_entry_node


def _setup(group, extra=None):
    vars = {"k": 0}
    if extra:
        vars.update(extra)
    group.setup(vars)


def test_linear_flow():
    group = Group(name="test")
    with group as group:
        visited = []

        def step_a(ctx):
            visited.append("a")
            return True

        def step_b(ctx):
            visited.append("b")
            return True

        a = Node("a", step_a)
        b = Node("b", step_b)
        group >> a >> b

    _setup(group)
    names = list(group)
    assert names == ["a", "b"]
    assert visited == ["a", "b"]


def test_pre_blocks_entry():
    group = Group(name="test")
    with group as group:
        log = []

        def on_a(ctx):
            log.append("a")
            return True

        def on_b(ctx):
            log.append("b")
            return True

        a = Node("a", on_a)
        b = Node("b", on_b, pre=lambda ctx: False)
        group >> a >> b

    _setup(group)
    it = iter(group)
    assert next(it) == "a"
    assert next(it) == "a"
    assert log == ["a"]


def test_post_blocks_exit():
    group = Group(name="test")
    with group as group:
        log = []

        def on_a(ctx):
            log.append("a")
            return True

        def on_b(ctx):
            log.append("b")
            return True

        a = Node("a", on_a, post=lambda ctx: False)
        b = Node("b", on_b)
        group >> a >> b

    _setup(group)
    it = iter(group)
    assert next(it) == "a"
    assert next(it) == "a"
    assert log == ["a"]


def test_func_pending_retry():
    group = Group(name="test")
    attempts = {"b": 0}

    with group as group:

        def on_a(ctx):
            return True

        def on_b(ctx):
            attempts["b"] += 1
            return attempts["b"] >= 2

        a = Node("a", on_a)
        b = Node("b", on_b)
        group >> a >> b

    _setup(group)
    it = iter(group)
    assert next(it) == "a"
    assert next(it) == "a"
    assert next(it) == "b"
    assert attempts["b"] == 2


def test_vars_get_set():
    group = Group(name="test")
    with group as group:
        a = Node("a", lambda ctx: ctx.set("k", ctx.get("k") + 1) or True)
        b = Node("b", lambda ctx: ctx.set("k", ctx.get("k") + 10) or True)
        group >> a >> b

    _setup(group)
    list(group)
    assert group.get("k") == 11


def test_vars_chain_shadow():
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
    list(root)
    assert root.get("x") == 1
    assert sub.get("x") == 2


def test_iter_restores_vars():
    group = Group(name="test")
    with group as group:
        a = Node("a", lambda ctx: ctx.set("k", ctx.get("k") + 1) or True)
        group >> a

    _setup(group, {"k": 0})
    list(group)
    assert group.get("k") == 1
    list(group)
    assert group.get("k") == 1


def test_nested_group():
    main = Group(name="main")
    with main as main:
        sub = Group(name="sub")
        with sub as sub:
            inner = Node("inner", lambda ctx: True)
            sub >> inner
        end = Node("end", lambda ctx: True)
        main >> sub
        inner >> end

    _setup(main)
    names = list(main)
    assert names == ["inner", "end"]


def test_parallel_pre_filter():
    main = Group(name="main")
    with main as main:
        log = []

        def on_start(ctx):
            log.append("start")
            return True

        def on_b(ctx):
            log.append("b")
            return True

        def on_c(ctx):
            log.append("c")
            return True

        start = Node("start", on_start)
        b = Node("b", on_b, pre=lambda ctx: False)
        c = Node("c", on_c, pre=lambda ctx: True)
        main >> start >> [b, c]

    _setup(main)
    names = list(main)
    assert names == ["start", "c"]
    assert log == ["start", "c"]


def test_parallel_all_pre_fail():
    group = Group(name="test")
    with group as group:
        a = Node("a", lambda ctx: True)
        b = Node("b", lambda ctx: True, pre=lambda ctx: False)
        c = Node("c", lambda ctx: True, pre=lambda ctx: False)
        group >> a >> [b, c]

    _setup(group)
    it = iter(group)
    assert next(it) == "a"
    assert next(it) == "a"


def test_resolve_entry_node():
    main = Group(name="main")
    with main as main:
        sub = Group(name="sub")
        with sub as sub:
            inner = Node("inner", lambda ctx: True, pre=lambda ctx: True)
            sub >> inner

    entry = resolve_entry_node(sub.start)
    assert entry.name == "inner"
