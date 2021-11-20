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
    __name__ == "base"

    def __init__(self, name=None, diag=None):
        if name:
            self.name = name
        else:
            self.name = str(uuid.uuid4()).replace("-", "")
        self.handler = None
        self.edge = []
        self.nodes = dict()
        self.edges = dict()
        self.groups = dict()
        self.start = self.add_node(Node("__start", None, diag=self))
        self.current = self.start
        if diag:
            self.diag = diag
        else:
            self.diag = getdiagram()
        self.level = self.diag.level + 1 if self.diag else 0
        if self.diag:
            self.diag.add_group(self)
            self.diag.add_node(self.start)

    def initial(self, handler, hwnd):
        self.handler = handler
        self.hwnd = hwnd

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
        block_sub = False
        if self.current.diag.level > self.level:
            try:
                return next(self.current.diag)
            except StopIteration as e:
                block_sub = True

        next_list = [(edges, node) for (edges, node) in self.current.next_list if self.level <= node.diag.level]
        if not next_list:
            self.current = self.start
            raise StopIteration("")

        next_node = None
        while not next_node:
            time.sleep(0.5)
            end_node_list = []
            for edges, node in next_list:
                if block_sub and node.diag != self:
                    end_node_list.append(node)

                for edge in edges:
                    if not edge.func(self.handler):
                        break
                else:
                    if node.func is None:
                        node_ = node.next_list[0][1]
                    else:
                        node_ = node

                    result = node_.func(self.handler, self.hwnd)
                    if result:
                        node_.diag.current = node_
                        self.current = node_
                        next_node = node_
                        break

            if len(end_node_list) == len(next_list):
                self.current = self.start
                raise StopIteration("")
        return self.current.name

    def __rshift__(self, other):
        if isinstance(other, DAG):
            print(f"{self.name}: {self.start.name} rshift {other.name}.{other.start.name}")
            other.diag.connect(self.start, other.start)
            return other
        elif isinstance(other, Node):
            print(f"{self.name}: {self.start.name} rshift {other.name}")
            other.diag.connect(self.start, other)
            return other
        elif isinstance(other, Edge):
            print(f"{self.name}: {self.start.name} rshift {other.name}")
            other.diag.forward(other)
            return self

    def __lshift__(self, other):
        if isinstance(other, DAG):
            print(f"{self.name}: {self.start.name} lshift {other.name}.{other.start.name}")
            other.diag.connect(other.start, self.start)
            return other
        elif isinstance(other, Node):
            print(f"{self.name}: {self.start.name} lshift {other.name}")
            other.diag.connect(other, self.start)
            return other
        elif isinstance(other, Edge):
            print(f"{self.name}: {self.start.name} lshift {other.name}")
            other.diag.forward(other)
            return self

    def add_group(self, group):
        self.groups[id(group)] = group
        return group

    def add_node(self, node):
        self.nodes[id(node)] = node
        return node

    def add_edge(self, edge):
        self.edges[id(edge)] = edge
        return edge

    def connect(self, start, to):
        start.next_list.append((self.edge, to))
        to.prev_list.append((self.edge, start))
        self.edge = []

    def forward(self, edge):
        self.edge.append(edge)

    def order(self):
        finished_node_set = set()
        checked_node_set = set()

        ordered = list()
        _nodes = deque(copy.deepcopy(self.nodes).values())
        while _nodes:
            _node = _nodes.popleft()
            for _edge, _pnode in _node.prev_list:
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
            for edges, _node in node.next_list:
                string += f"{node.diag.name}.{node.name} =="
                if edges:
                    string += "("
                    string += ", ".join(f"{e.name}" for e in edges)
                    string += ")"
                string += f"=> {_node.diag.name}.{_node.name}\n"

        for _, node in self.nodes.items():
            for edges, _node in node.prev_list:
                string += f"{node.diag.name}.{node.name} <="
                if edges:
                    string += "("
                    string += ", ".join(f"{e.name}" for e in edges[::-1])
                    string += ")"
                string += f"== {_node.diag.name}.{_node.name}\n"

        return string


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
                elif isinstance(other_, Edge):
                    pass

            node_name_list = ','.join(str(n) for n in dag_or_node_list)
            print(f"{self.diag.name}: {self.name} rshift [{node_name_list}]")
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
            elif isinstance(other, Edge):
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
        elif isinstance(other, Edge):
            print(f"{self.diag.name}: {self.name} lshift {other.name}")
            self.diag.forward(other)
            return self

    def __repr__(self):
        return f"Node({self.diag.name}.{self.name})"


class Edge:
    def __init__(self, name, func, diag=None):
        self.name = name
        self.func = func
        if diag:
            self.diag = diag
        else:
            self.diag = getdiagram()
        self.next_list = []
        self.prev_list = []
        self.diag.add_edge(self)

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
        return f"Edge({self.diag.name}.{self.name})"
