"""本次运行的启动参数。来自 DAG 的 build_setup()，不读 dotenv。"""


class SetupError(ValueError):
    """build_setup() 不符合编写合同。"""


def _as_int(value, key: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise SetupError(f"{key} 必须是整数")
    return value


def resolve_setup(raw: dict, dag: str) -> dict:
    """补上省略值并拒绝非法启动参数。保留 packages 与其它业务键。"""
    if not isinstance(raw, dict):
        raise SetupError("build_setup() 必须返回 dict")

    data = dict(raw)
    packages = data.pop("packages", {})
    if not isinstance(packages, dict):
        raise SetupError("packages 必须是 dict")

    name = data.get("name")
    if not isinstance(name, str) or name.strip() == "":
        raise SetupError("name 必须是非空字符串")
    data["name"] = name

    if "number" not in raw or raw.get("number") is None:
        number = 1
    else:
        number = _as_int(raw.get("number"), "number")
        if number < 1:
            raise SetupError("number 小于 1 时拒绝启动")
    data["number"] = number

    pix = data.get("pix", "")
    if not isinstance(pix, str):
        raise SetupError("pix 必须是字符串")
    data["pix"] = pix

    if "dashboard_port" not in raw or raw.get("dashboard_port") is None:
        port = 8765
    else:
        port = _as_int(raw.get("dashboard_port"), "dashboard_port")
        if port < 1 or port > 65535:
            raise SetupError("dashboard_port 必须在 1 到 65535 之间")
    data["dashboard_port"] = port

    if "dashboard_open" not in raw or raw.get("dashboard_open") is None:
        dashboard_open = False
    else:
        dashboard_open = raw.get("dashboard_open")
        if not isinstance(dashboard_open, bool):
            raise SetupError("dashboard_open 必须是布尔值")
    data["dashboard_open"] = dashboard_open

    data["dag"] = dag
    data["packages"] = packages
    return data
