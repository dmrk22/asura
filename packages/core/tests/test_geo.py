"""daari_core.geo tests: haversine distance against two known city pairs."""

from __future__ import annotations

import pytest

from daari_core import geo

GUNTUR = (16.2915, 80.4542)
VIJAYAWADA = (16.5062, 80.6480)
DELHI = (28.6139, 77.2090)
MUMBAI = (19.0760, 72.8777)


def test_guntur_to_vijayawada_is_about_30km():
    assert geo.haversine_km(GUNTUR, VIJAYAWADA) == pytest.approx(30.0, abs=3.0)


def test_delhi_to_mumbai_is_about_1150km():
    assert geo.haversine_km(DELHI, MUMBAI) == pytest.approx(1150.0, rel=0.05)


def test_distance_to_self_is_zero():
    assert geo.haversine_km(GUNTUR, GUNTUR) == 0.0


def test_symmetry():
    assert geo.haversine_km(GUNTUR, VIJAYAWADA) == pytest.approx(geo.haversine_km(VIJAYAWADA, GUNTUR))


@pytest.mark.parametrize(
    "point",
    [(91.0, 0.0), (-91.0, 0.0), (0.0, 181.0), (0.0, -181.0)],
)
def test_out_of_range_raises(point):
    with pytest.raises(ValueError):
        geo.haversine_km(point, GUNTUR)
