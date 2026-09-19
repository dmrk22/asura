"""daari_core.geo — great-circle distance for proximity ranking.

Pure: stdlib only (math). No I/O, no clock, no randomness (core.md). Callers
(e.g. `match._constraint_fit`'s successors) pass plain lat/lon tuples; this
module never geocodes anything — Nominatim lookups are the API lane's job.
"""

from __future__ import annotations

import math

EARTH_RADIUS_KM = 6371.0088


def _validate(point: tuple[float, float]) -> None:
    lat, lon = point
    if not (-90.0 <= lat <= 90.0):
        raise ValueError(f"latitude out of range: {lat!r}")
    if not (-180.0 <= lon <= 180.0):
        raise ValueError(f"longitude out of range: {lon!r}")


def haversine_km(a: tuple[float, float], b: tuple[float, float]) -> float:
    """Great-circle distance in km between two (lat, lon) points in degrees."""
    _validate(a)
    _validate(b)
    lat1, lon1 = math.radians(a[0]), math.radians(a[1])
    lat2, lon2 = math.radians(b[0]), math.radians(b[1])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * EARTH_RADIUS_KM * math.asin(math.sqrt(h))
