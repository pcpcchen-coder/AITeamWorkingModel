"""契約測試：解碼端常數必須與介面契約 protocol.yaml 一致 — 虛構範例（fictional）。"""

from pathlib import Path

import yaml

from soh_demo import frame

ICD = Path(__file__).resolve().parents[1] / "knowledge" / "interfaces" / "protocol.yaml"


def _frame_spec():
    spec = yaml.safe_load(ICD.read_text(encoding="utf-8"))
    assert spec["byte_order"] == "little"
    (ct,) = [f for f in spec["frames"] if f["name"] == "cell_temperature"]
    return ct


def test_frame_id_and_length_match_icd():
    ct = _frame_spec()
    assert int(ct["id"], 16) == frame.FRAME_ID
    assert ct["length"] == frame.FRAME_LENGTH


def test_field_layout_matches_icd():
    fields = {f["name"]: f for f in _frame_spec()["fields"]}
    temp, status = fields["temp_decic"], fields["status"]
    assert (temp["offset"], temp["type"], temp["scale"]) == (frame.TEMP_OFFSET, "int16", frame.TEMP_SCALE)
    assert (status["offset"], status["type"]) == (frame.STATUS_OFFSET, "uint8")
    assert status["values"][frame.STATUS_OK] == "ok"
