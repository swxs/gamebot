# -*- coding: utf-8 -*-
# @File    : Helper_productor.py
# @AUTH    : swxs
# @Time    : 2019/6/27 16:37

import os
import sys
from fnmatch import fnmatch
from importlib import import_module
from commons import log_utils

logger = log_utils.get_logging("common.Productor")

class NoModule(Exception):
    pass


class Productor(object):
    def __init__(
        self,
        base_module: object,
        start_dir: str,
        pattern: str = '*.py',
        top_level_dir: str = None,
        temp_module: object = None,
        root_dir: str = None,
    ):
        self._productor = {}
        self._path = {}

        self.base_module = base_module
        self.temp_module = temp_module
        self.start_dir = start_dir
        self.pattern = pattern
        if top_level_dir is None:
            self.top_level_dir = self.start_dir
        else:
            self.top_level_dir = top_level_dir
        if root_dir is None:
            self.root_dir = os.path.dirname(os.path.abspath(__file__))
        else:
            self.root_dir = root_dir

    def __getitem__(self, item):
        return self._get_module(item, root_path=None)

    def __delitem__(self, key):
        del sys.modules[self._path[key]]
        del self._productor[key]
        del self._path[key]

    def __contains__(self, item):
        return item in self._productor

    def _get_module(self, item, root_path=None):
        """
        从__getitem__改造而来
        :param item:
        :param root_path: 后面加了要限制文件夹权限的需求后添加了root_path，可以动态修改加载的root文件夹
        :return:
        """
        if item not in self._productor:
            self.discover(root_path=root_path)

        if item in self._productor:
            return self._productor[item]
        else:
            if self.temp_module:
                return self.temp_module
            else:
                raise NoModule

    def _load_module(self, module, module_path):
        try:
            name = getattr(module, "name")
        except Exception:
            name = getattr(module, "__name__")
        self._productor[name] = module
        self._path[name] = module_path

    def _match_path(self, path, full_path, pattern):
        # override this method to use alternative matching strategy
        return fnmatch(path, pattern)

    def _path_2_modulepath(self, path=''):
        if path:
            path = path.replace('\\', '/').replace(self.root_dir.replace('\\', '/'), '')
            if path.startswith('/'):
                path = path[1:]
            path = path.replace('.py', '').replace('.PY', '')
            if set('.#~') & set(path):
                return None
            path = path.replace('/', '.').strip()
            if path:
                return path
        return None

    def discover(self, root_path=None):
        if root_path:
            top_level_dir = root_path
        elif self.top_level_dir:
            top_level_dir = os.path.abspath(self.top_level_dir)
        else:
            top_level_dir = None

        if top_level_dir and os.path.isdir(os.path.abspath(top_level_dir)):
            for root, dirs, files in os.walk(top_level_dir):
                for file_name in files:
                    full_path = os.path.join(root, file_name)
                    if self._match_path(file_name, full_path, self.pattern):
                        try:
                            module_path = self._path_2_modulepath(full_path)
                            module = import_module(module_path)
                            for name in dir(module):
                                obj = getattr(module, name)
                                if (
                                    isinstance(obj, type)
                                    and issubclass(obj, self.base_module)
                                    and getattr(obj, "__module__") == module_path
                                ):
                                    self._load_module(obj, module_path)
                        except Exception as e:
                            logger.exception(e, f"full_path: {full_path}")
        else:
            pass
