"""daari_core.telemetry — pure in-process counters. No clock, no I/O."""

from daari_core import telemetry


def test_count_increments_the_right_persona_engine_pair():
    before = telemetry.snapshot().get("test_persona_a", {}).get("test_engine_a", 0)
    telemetry.count("test_persona_a", "test_engine_a")
    telemetry.count("test_persona_a", "test_engine_a")
    after = telemetry.snapshot()["test_persona_a"]["test_engine_a"]
    assert after - before == 2


def test_count_does_not_leak_across_personas_or_engines():
    telemetry.count("test_persona_b", "test_engine_b")
    snap = telemetry.snapshot()
    assert snap["test_persona_b"]["test_engine_b"] >= 1
    assert "test_engine_never_called" not in snap.get("test_persona_b", {})


def test_snapshot_shape_is_persona_to_engine_to_count():
    telemetry.count("test_persona_c", "test_engine_c")
    snap = telemetry.snapshot()
    assert isinstance(snap, dict)
    assert isinstance(snap["test_persona_c"], dict)
    assert isinstance(snap["test_persona_c"]["test_engine_c"], int)
