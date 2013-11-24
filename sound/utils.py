import math

import numpy
from numpy.matrixlib import matrix


def intersect_circles(x1, y1, x2, y2, r0, r1):
    vec1 = numpy.float64((x1, y1))
    vec2 = numpy.float64((x2, y2))
    vec_diff = vec2 - vec1
    distance_sq = (vec_diff**2).sum()
    distance = math.sqrt(distance_sq)

    if distance > (r0 + r1):
        return False, None
    elif distance < abs(r0 - r1):
        return True, None
    elif distance == 0:
        return True, None
    else:
        a = (r0**2 - r1**2 + distance_sq) / (2 * distance)
        h = math.sqrt(r0**2 - a**2)
        vec3 = vec1 + a * vec_diff / distance

        p1 = matrix([[vec3[0] + h * vec_diff[1] / distance],
                     [vec3[1] - h * vec_diff[0] / distance],
                     [1]])
        p2 = matrix([[vec3[0] - h * vec_diff[1] / distance],
                     [vec3[1] + h * vec_diff[0] / distance],
                     [1]])

        return True, (p1, p2)
