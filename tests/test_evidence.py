import json

from gamebot.core.evidence import EvidenceWriter


class _NoPkgs:
    def pkg(self, name):
        raise KeyError(name)


def test_evidence_keeps_last_five_steps(tmp_path):
    writer = EvidenceWriter(str(tmp_path))
    group = _NoPkgs()
    for index in range(7):
        writer.write(group, f"step-{index}")
    steps = json.loads((tmp_path / "steps.json").read_text(encoding="utf-8"))
    assert steps == [f"step-{index}" for index in range(2, 7)]
    assert (tmp_path / "previous.png").read_bytes() == b""
    assert (tmp_path / "tree.txt").read_text(encoding="utf-8") == ""
