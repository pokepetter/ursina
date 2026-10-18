from math import isclose

from ursina import curve
from ursina.ursinastuff import _test


def test_combine():
    passed = True
    for split in (.25, .33, .5, .75):
        pulse = curve.combine(curve.linear, curve.reverse(curve.linear), split)
        for t, expected in (
            (0, 0),
            (split / 2, .5),
            (split, 1),
            ((split + 1) / 2, .5),
            (1, 0),
        ):
            passed &= _test(isclose(pulse(t), expected, abs_tol=1e-12))
    assert passed


if __name__ == '__main__':
    test_combine()
