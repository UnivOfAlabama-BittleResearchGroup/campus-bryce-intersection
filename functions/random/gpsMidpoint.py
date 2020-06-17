import math


def midpoint(x1, y1, x2, y2):

    lat1 = math.radians(x1)
    lon1 = math.radians(x2)
    lat2 = math.radians(y1)
    lon2 = math.radians(y2)

    bx = math.cos(lat2) * math.cos(lon2 - lon1)
    by = math.cos(lat2) * math.sin(lon2 - lon1)
    lat3 = math.atan2(math.sin(lat1) + math.sin(lat2), \
           math.sqrt((math.cos(lat1) + bx) * (math.cos(lat1) \
           + bx) + by**2))
    lon3 = lon1 + math.atan2(by, math.cos(lat1) + bx)

    return [round(math.degrees(lat3), 6), round(math.degrees(lon3), 6)]


if __name__ == "__main__":

    x = [-87.582325, 33.033782]
    y = [-87.530096, 33.162133]

    print(midpoint(x[0], y[0], x[1], y[1]))