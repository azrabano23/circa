"""Invariants of the two-process alertness model."""
from circadian.model import Chronotype, alertness, alertness_curve, peak_hour


def test_alertness_bounded():
    for h in range(0, 25):
        for ct in Chronotype:
            assert 0.0 <= alertness(float(h), ct, wake_hour=7.0) <= 1.0


def test_before_waking_is_zero():
    assert alertness(5.0, Chronotype.INTERMEDIATE, wake_hour=7.0) == 0.0
    assert alertness(6.9, Chronotype.INTERMEDIATE, wake_hour=7.0) == 0.0


def test_chronotype_orders_the_peak():
    # larks peak earlier in the day than intermediates, who peak earlier than owls
    lark = peak_hour(Chronotype.LARK, wake_hour=6.0)
    mid = peak_hour(Chronotype.INTERMEDIATE, wake_hour=7.0)
    owl = peak_hour(Chronotype.OWL, wake_hour=8.0)
    assert lark < owl
    assert lark <= mid <= owl


def test_meq_mapping():
    assert Chronotype.from_meq(70) is Chronotype.LARK
    assert Chronotype.from_meq(50) is Chronotype.INTERMEDIATE
    assert Chronotype.from_meq(30) is Chronotype.OWL


def test_late_night_is_low():
    # deep night alertness should be far below the daytime peak
    night = alertness(2.0, Chronotype.INTERMEDIATE, wake_hour=7.0)
    peak_h = peak_hour(Chronotype.INTERMEDIATE, wake_hour=7.0)
    day = alertness(peak_h, Chronotype.INTERMEDIATE, wake_hour=7.0)
    assert night < day


def test_curve_starts_at_wake():
    curve = alertness_curve(Chronotype.OWL, wake_hour=9.0)
    assert curve[0][0] == 9.0
