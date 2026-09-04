import contextvars
import copy
import logging
import types
import uuid
from collections import deque
from typing import Callable, Dict, List, Optional

logger = logging.getLogger(__name__)

__diagrams = contextvars.ContextVar("diagrams")

Hook = Callable[..., bool]


def getdiagram():
    try:
        return __diagrams.get()
    except LookupError:
        return None


def setdiagram(diagram):
    __diagrams.set(diagram)


def resolve_entry_node(node: "Node") -> "Node":
    """穿透 __start / Group 入口，取第一个 func 非空的节点。"""
    current = node
    seen = set()
    while current.func is None:
        nid = id(current)
        if nid in seen:
            raise RuntimeError(f"entry resolution cycle at {current.name!r}")
        seen.add(nid)
        if not current.next_list:
            return current
        current = current.next_list[0]
    return current


class Context:
    """节点 hook 的运行时上下文，绑定 node.diag（所属 Group）。"""

    def __init__(self, group: "Group"):
        self._group = group

    def get(self, key, default=None):
        return self._group.get(key, default)

    def set(self, key, value):
        self._group.set(key, value)

    def pkg(self, name):
        return self._group.pkg(name)

    @property
    def vars(self):
        return self._group.vars


class Group:
    def __init__(self, name: Optional[str] = None, diag=None):
        if name:
            self.name = name
        else:
            self.name = str(uuid.uuid4()).replace("-", "")

        self.dags: Dict[int, "Group"] = {}
        self.nodes: Dict[int, Node] = {}

        self._vars: dict = {}
        self._vars_template: dict = {}
        self._packages: dict = {}
        self._packages_template: dict = {}

        self.start = self.add_node(Node("__start", None, diag=self))
        self.current = self.start

        self._pending_target: Optional[Node] = None
        self._pending_post_pre_done = False

        if diag:
            self.diag = diag
        else:
            self.diag = getdiagram()
        self.level = self.diag.level + 1 if self.diag else 0
        if self.diag:
            self.diag.add_dag(self)

    def setup(self, vars: dict):
        data = copy.deepcopy(vars)
        packages = data.pop("packages", {})
        self._vars_template = data
        self._vars = copy.deepcopy(data)
        self._packages_template = copy.deepcopy(packages)
        self._packages = copy.deepcopy(packages)
        for group in self.dags.values():
            group.setup(vars)

    def pkg(self, name):
        if name in self._packages:
            return self._packages[name]
        if self.diag:
            return self.diag.pkg(name)
        raise KeyError(f"package {name!r} not found")

    def get(self, key, default=None):
        if key in self._vars:
            return self._vars[key]
        if self.diag:
            return self.diag.get(key, default)
        return default

    def set(self, key, value):
        self._vars[key] = value

    @property
    def vars(self):
        return types.MappingProxyType(self._vars)

    def _restore_vars(self):
        self._vars = copy.deepcopy(self._vars_template)
        self._packages = copy.deepcopy(self._packages_template)

    def _clear_pending(self):
        self._pending_target = None
        self._pending_post_pre_done = False

    def _run_hook(self, node: "Node", hook: Optional[Hook]) -> bool:
        if hook is None:
            return True
        return hook(Context(node.diag))

    def _run_func(self, target: "Node") -> bool:
        entry = resolve_entry_node(target)
        if entry.func is None:
            return True
        return self._run_hook(entry, entry.func)

    def _advance_to(self, target: "Node"):
        entry = resolve_entry_node(target)
        entry.diag.current = entry
        self.current = entry

    def _candidate_targets(self, need_block_sub: bool) -> List["Node"]:
        result = []
        for node in self.current.next_list:
            if self.level <= node.diag.level:
                result.append(node)
            elif need_block_sub and node.diag != self:
                continue
            else:
                result.append(node)
        return result

    def _try_pending(self) -> Optional[str]:
        if self._pending_target is None:
            return None
        if self._run_func(self._pending_target):
            name = self._pending_target.name
            self._advance_to(self._pending_target)
            self._clear_pending()
            return name
        return self.current.name

    def _try_transition(self, candidates: List["Node"]) -> Optional[str]:
        if not candidates:
            return None

        if not self._run_hook(self.current, self.current.post):
            return self.current.name

        winner = None
        for target in candidates:
            entry = resolve_entry_node(target)
            if self._run_hook(entry, entry.pre):
                winner = target
                break

        if winner is None:
            return self.current.name

        if not self._run_func(winner):
            self._pending_target = winner
            self._pending_post_pre_done = True
            return self.current.name

        self._advance_to(winner)
        self._clear_pending()
        return self.current.name

    def __enter__(self):
        setdiagram(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.diag:
            setdiagram(self.diag)
        else:
            setdiagram(None)

    def __iter__(self):
        self._restore_vars()
        self.current = self.start
        self._clear_pending()
        for group in self.dags.values():
            group.current = group.start
            group._clear_pending()
        return self

    def __next__(self):
        need_block_sub = False
        if self.current.diag is not self and self.current.diag.level > self.level:
            try:
                return next(self.current.diag)
            except StopIteration:
                need_block_sub = True

        if self._pending_target is not None:
            return self._try_pending()

        candidates = self._candidate_targets(need_block_sub)
        if not candidates:
            self.current = self.start
            raise StopIteration(f"当前图:{self.name}[{self.level}]结束!")

        result = self._try_transition(candidates)
        if result is not None:
            return result

        self.current = self.start
        raise StopIteration("")

    def __rshift__(self, other):
        if isinstance(other, Group):
            logger.debug("%s: %s rshift %s.%s", self.name, self.start.name, other.name, other.start.name)
            other.diag.connect(self.start, other.start)
            return other
        if isinstance(other, Node):
            logger.debug("%s: %s rshift %s", self.name, self.start.name, other.name)
            other.diag.connect(self.start, other)
            return other

    def __lshift__(self, other):
        if isinstance(other, Group):
            logger.debug("%s: %s lshift %s.%s", self.name, self.start.name, other.name, other.start.name)
            other.diag.connect(other.start, self.start)
            return other
        if isinstance(other, Node):
            logger.debug("%s: %s lshift %s", self.name, self.start.name, other.name)
            other.diag.connect(other, self.start)
            return other

    def add_dag(self, group):
        self.dags[id(group)] = group
        return group

    def add_node(self, node):
        self.nodes[id(node)] = node
        return node

    def connect(self, start: "Node", to: "Node"):
        start.next_list.append(to)
        to.prev_list.append(start)

    def order(self):
        finished_node_set = set()
        checked_node_set = set()
        ordered = []
        _nodes = deque(copy.deepcopy(self.nodes).values())
        while _nodes:
            _node = _nodes.popleft()
            for _pnode in _node.prev_list:
                if _pnode not in finished_node_set:
                    break
            else:
                finished_node_set.add(_node)
                checked_node_set = set()
                ordered.append(_node)
                continue

            if _node in checked_node_set:
                logger.warning("有环 %s", _node)
                break
            checked_node_set.add(_node)
            _nodes.append(_node)
        return ordered

    def __repr__(self):
        string = f"{self.name}:\n"
        for _, node in self.nodes.items():
            for _node in node.next_list:
                string += f"  {node.diag.name}.{node.name} => {_node.diag.name}.{_node.name}\n"
        return string


class Node:
    def __init__(self, name, func, pre=None, post=None, diag=None):
        self.name = name
        self.func = func
        self.pre = pre
        self.post = post
        if diag:
            self.diag = diag
        else:
            self.diag = getdiagram()
        self.next_list: List[Node] = []
        self.prev_list: List[Node] = []
        if self.diag:
            self.diag.add_node(self)

    def __rshift__(self, other):
        if isinstance(other, list):
            result = []
            for other_ in other:
                if isinstance(other_, Group):
                    logger.debug(
                        "%s: %s rshift %s.%s",
                        self.diag.name,
                        self.name,
                        other_.name,
                        other_.start.name,
                    )
                    self.diag.connect(self, other_.start)
                    result.append(other_)
                elif isinstance(other_, Node):
                    logger.debug("%s: %s rshift %s", self.diag.name, self.name, other_.name)
                    self.diag.connect(self, other_)
                    result.append(other_)
            return result
        if isinstance(other, Group):
            logger.debug(
                "%s: %s rshift %s.%s",
                self.diag.name,
                self.name,
                other.name,
                other.start.name,
            )
            self.diag.connect(self, other.start)
            return other
        if isinstance(other, Node):
            logger.debug("%s: %s rshift %s", self.diag.name, self.name, other.name)
            self.diag.connect(self, other)
            return other

    def __lshift__(self, other):
        if isinstance(other, Group):
            logger.debug(
                "%s: %s lshift %s.%s",
                self.diag.name,
                self.name,
                other.name,
                other.start.name,
            )
            self.diag.connect(other.start, self)
            return other
        if isinstance(other, Node):
            logger.debug("%s: %s lshift %s", self.diag.name, self.name, other.name)
            self.diag.connect(other, self)
            return other

    def __repr__(self):
        return f"Node({self.diag.name}.{self.name})"
