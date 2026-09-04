"""Package 基类与 setup 时依赖检查。"""


class Package:
    """栈级安装单元：check_deps + install_* 工厂。"""

    @classmethod
    def check_deps(cls):
        """子类覆盖：import / 环境探测；setup 时按 __package__ 去重调用。"""


def check_packages(packages: dict) -> None:
    """Group.setup 调用：对已安装 handler 的 __package__ 去重并 check_deps。"""
    seen: set[type] = set()
    for handler in packages.values():
        pkg_cls = getattr(type(handler), "__package__", None)
        if pkg_cls is None or pkg_cls in seen:
            continue
        pkg_cls.check_deps()
        seen.add(pkg_cls)
