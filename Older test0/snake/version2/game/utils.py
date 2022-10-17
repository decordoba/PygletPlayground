import math


def distance(point1=(0, 0), point2=(0, 0)):
    """Returns the distance between two points"""
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)
