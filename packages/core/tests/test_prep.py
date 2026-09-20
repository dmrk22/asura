from datetime import date

from daari_core.prep import schedule


def test_schedule_is_bounded_and_deterministic():
    days = schedule(date(2026, 10, 10), date(2026, 10, 1), ("SQL", "mock"))
    assert len(days) == 9
    assert days[0].focus == "SQL"
    assert days[1].focus == "mock"


def test_schedule_rejects_past_interview():
    try:
        schedule(date(2026, 10, 1), date(2026, 10, 1), ())
    except ValueError:
        pass
    else:
        raise AssertionError("a same-day interview has no usable prep day")
