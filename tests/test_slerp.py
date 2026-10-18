from math import cos, radians, sin

from panda3d.core import LQuaterniond, LQuaternionf

from ursina import slerp
from ursina.ursinastuff import _test


def test_slerp_small_angles():
    passed = True
    for quaternion_type in (LQuaternionf, LQuaterniond):
        for angle in (.001, .01, .02):
            half_angle = radians(angle) / 2
            start = quaternion_type(1, 0, 0, 0)
            end = quaternion_type(cos(half_angle), 0, sin(half_angle), 0)
            for sign in (1, -1):
                target = end * sign
                original = tuple(target)
                for t in (0, .1, .5, 1):
                    result = slerp(start, target, t)
                    expected = quaternion_type(cos(half_angle * t), 0, sin(half_angle * t), 0)
                    passed &= _test(max(abs(a - b) for a, b in zip(result, expected, strict=True)) < 1e-7)
                    passed &= _test(abs(result.length() - 1) < 1e-7)
                passed &= _test(tuple(target) == original)
    assert passed


if __name__ == '__main__':
    test_slerp_small_angles()
