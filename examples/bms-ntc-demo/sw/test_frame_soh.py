"""上位機單元測試 — 虛構範例（fictional）。"""

import struct

import pytest

from soh_demo.frame import FrameError, decode_cell_temperature
from soh_demo.soh import compensate_soh


@pytest.mark.parametrize("decic, expected", [(250, 25.0), (-200, -20.0), (0, 0.0), (605, 60.5)])
def test_decode_temperature(decic, expected):
    frame = decode_cell_temperature(struct.pack("<hB", decic, 0))
    assert frame.temp_c == expected and frame.status == 0


@pytest.mark.parametrize("payload", [b"", b"\x00\x00", b"\x00\x00\x00\x00"])
def test_decode_rejects_wrong_length(payload):
    with pytest.raises(FrameError):
        decode_cell_temperature(payload)


def test_no_compensation_above_knee():
    assert compensate_soh(0.9, 25.0) == 0.9


def test_low_temperature_compensation_increases_soh_and_caps_at_one():
    assert compensate_soh(0.8, -20.0) == pytest.approx(0.8 * (1 + 0.004 * 30))
    assert compensate_soh(0.99, -40.0) == 1.0


@pytest.mark.parametrize("bad", [-0.1, 1.1])
def test_compensation_rejects_out_of_range_soh(bad):
    with pytest.raises(ValueError):
        compensate_soh(bad, 0.0)
