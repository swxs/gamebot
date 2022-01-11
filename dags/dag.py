# %load ../DAG.py
# DAG
import time
import uuid
import copy
import contextvars
from collections import deque

__diagrams = contextvars.ContextVar("diagrams")


def getdiagram():
    try:
        return __diagrams.get()
    except LookupError:
        return None


def setdiagram(diagram):
    __diagrams.set(diagram)


class DAG:
    def __init__(self, name=None, diag=None):
        if name:
            self.name = name
        else:
            self.name = str(uuid.uuid4()).replace("-", "")

        self.handler = None
        self.hwnd = None

        self.dags = dict()
        self.nodes = dict()
        self.selectors = dict()

        self.start = self.add_node(Node("__start", None, diag=self))

        self.current_selector_list = []
        self.current = self.start

        # 对于最顶层节点self.diag is None, 否则为其父节点
        if diag:
            self.diag = diag
        else:
            self.diag = getdiagram()
        # 对于最顶层节点， level = 0, 否则为其深度
        self.level = self.diag.level + 1 if self.diag else 0
        # 父节点追加一下子节点的初始节点，可有可无
        if self.diag:
            self.diag.add_dag(self)

    def setup(self, handler, hwnd):
        self.handler = handler
        self.hwnd = hwnd
        for id_, dag in self.dags.items():
            dag.setup(handler, hwnd)

    def __enter__(self):
        setdiagram(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.diag:
            setdiagram(self.diag)
        else:
            setdiagram(None)

    def __iter__(self):
        return self

    def __next__(self):
        need_block_sub = False
        if self.current.diag.level > self.level:
            try:
                return next(self.current.diag)
            except StopIteration as e:
                need_block_sub = True

        # 找到所有可以触发的子节点
        next_list = [
            (selector_list, node) for (selector_list, node) in self.current.next_list if self.level <= node.diag.level
        ]
        if not next_list:
            self.current = self.start
            raise StopIteration(f"当前图:{self.name}[{self.level}]结束!")

        has_next_node = False
        while not has_next_node:
            end_node_list = []
            for selector_list, node in next_list:
                if need_block_sub and node.diag != self:
                    end_node_list.append(node)
                    continue

                # 子循环节点则使用其初始节点代替判断
                if node.func is None:
                    real_selector_list, real_node = node.next_list[0]
                else:
                    real_selector_list, real_node = selector_list, node

                for selector in real_selector_list:
                    if not selector.func(self.handler, self.hwnd):
                        break
                else:
                    result = real_node.func(self.handler, self.hwnd)
                    if result:
                        node.diag.current = real_node
                        self.current = node
                        has_next_node = True
                        break

            if len(end_node_list) == len(next_list):
                self.current = self.start
                raise StopIteration("")
        return self.current.name

    def clear(self):
        pass

    def __rshift__(self, other):
        if isinstance(other, DAG):
            print(f"{self.name}: {self.start.name} rshift {other.name}.{other.start.name}")
            other.diag.connect(self.start, other.start)
            return other
        elif isinstance(other, Node):
            print(f"{self.name}: {self.start.name} rshift {other.name}")
            other.diag.connect(self.start, other)
            return other
        elif isinstance(other, Selector):
            print(f"{self.name}: {self.start.name} rshift {other.name}")
            other.diag.forward(other)
            return self

    def __rrshift__(self, other):
        pass

    def __lshift__(self, other):
        if isinstance(other, DAG):
            print(f"{self.name}: {self.start.name} lshift {other.name}.{other.start.name}")
            other.diag.connect(other.start, self.start)
            return other
        elif isinstance(other, Node):
            print(f"{self.name}: {self.start.name} lshift {other.name}")
            other.diag.connect(other, self.start)
            return other
        elif isinstance(other, Selector):
            print(f"{self.name}: {self.start.name} lshift {other.name}")
            other.diag.forward(other)
            return self

    def __rlshift__(self, other):
        pass

    def add_dag(self, dag):
        self.dags[id(dag)] = dag
        return dag

    def add_node(self, node):
        self.nodes[id(node)] = node
        return node

    def add_selector(self, selector):
        self.selectors[id(selector)] = selector
        return selector

    def connect(self, start, to):
        start.next_list.append((self.current_selector_list, to))
        to.prev_list.append((self.current_selector_list, start))
        self.current_selector_list = []

    def forward(self, selector):
        self.current_selector_list.append(selector)

    def order(self):
        finished_node_set = set()
        checked_node_set = set()

        ordered = list()
        _nodes = deque(copy.deepcopy(self.nodes).values())
        while _nodes:
            _node = _nodes.popleft()
            for _selector, _pnode in _node.prev_list:
                if _pnode not in finished_node_set:
                    break
            else:
                finished_node_set.add(_node)
                checked_node_set = set()
                ordered.append(_node)
                continue

            if _node in checked_node_set:
                print("有环", _node)
                break
            checked_node_set.add(_node)
            _nodes.append(_node)

        return ordered

    def __repr__(self):
        string = f"{self.name}: "
        for _, node in self.nodes.items():
            for selectors, _node in node.next_list:
                string += f"{node.diag.name}.{node.name} =="
                if selectors:
                    string += "("
                    string += ", ".join(f"{e.name}" for e in selectors)
                    string += ")"
                string += f"=> {_node.diag.name}.{_node.name}\n"

        for _, node in self.nodes.items():
            for selectors, _node in node.prev_list:
                string += f"{node.diag.name}.{node.name} <="
                if selectors:
                    string += "("
                    string += ", ".join(f"{e.name}" for e in selectors[::-1])
                    string += ")"
                string += f"== {_node.diag.name}.{_node.name}\n"

        return string

    def copy(self, name):
        copyed_dag = DAG(name=name, diag=self.diag)

        copyed_dag.dags = self.dags
        copyed_dag.nodes = self.nodes
        copyed_dag.selectors = self.selectors

        for (selector, start_node) in self.start.next_list:
            copyed_dag.connect(copyed_dag.start, start_node)

        return copyed_dag


class Node:
    def __init__(self, name, func, diag=None):
        self.name = name
        self.func = func
        if diag:
            self.diag = diag
        else:
            self.diag = getdiagram()
        self.next_list = []
        self.prev_list = []
        if self.diag:
            self.diag.add_node(self)

    def __rshift__(self, other):
        if isinstance(other, list):
            dag_or_node_list = []
            for other_ in other:
                if isinstance(other_, DAG):
                    self.diag.connect(self, other_.start)
                    dag_or_node_list.append(other_)
                elif isinstance(other_, Node):
                    self.diag.connect(self, other_)
                    dag_or_node_list.append(other_)
                elif isinstance(other_, Selector):
                    pass
            return dag_or_node_list
        else:
            if isinstance(other, DAG):
                print(f"{self.diag.name}: {self.name} rshift {other.name}.{other.start.name}")
                self.diag.connect(self, other.start)
                return other
            elif isinstance(other, Node):
                print(f"{self.diag.name}: {self.name} rshift {other.name}")
                self.diag.connect(self, other)
                return other
            elif isinstance(other, Selector):
                print(f"{self.diag.name}: {self.name} rshift {other.name}")
                self.diag.forward(other)
                return self

    def __lshift__(self, other):
        if isinstance(other, DAG):
            print(f"{self.diag.name}: {self.name} lshift {other.name}.{other.start.name}")
            self.diag.connect(other.start, self)
            return other
        elif isinstance(other, Node):
            print(f"{self.diag.name}: {self.name} lshift {other.name}")
            self.diag.connect(other, self)
            return other
        elif isinstance(other, Selector):
            print(f"{self.diag.name}: {self.name} lshift {other.name}")
            self.diag.forward(other)
            return self

    def __repr__(self):
        return f"Node({self.diag.name}.{self.name})"


class Selector:
    def __init__(self, name, func, diag=None):
        self.name = name
        self.func = func
        if diag:
            self.diag = diag
        else:
            self.diag = getdiagram()
        self.next_list = []
        self.prev_list = []
        self.diag.add_selector(self)

    def __rshift__(self, other):
        if isinstance(other, DAG):
            print(f"{self.diag.name}: {self.name} 'rshift {other.name}.{other.start.name}")
            self.diag.forward(self)
            return other
        elif isinstance(other, Node):
            print(f"{self.diag.name}: {self.name} 'rshift {other.name}")
            self.diag.forward(self)
            return other

    def __lshift__(self, other):
        if isinstance(other, DAG):
            print(f"{self.diag.name}: {self.name} 'lshift {other.name}.{other.start.name}")
            self.diag.forward(self)
            return self
        elif isinstance(other, Node):
            print(f"{self.diag.name}: {self.name} 'lshift {other.name}")
            self.diag.forward(self)
            return self

    def __repr__(self):
        return f"Selector({self.diag.name}.{self.name})"
