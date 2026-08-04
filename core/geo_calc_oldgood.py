import math
from geopy.distance import geodesic
from core.kml_reader import read_route_from_kml


def calculate_bearing(lat1, lon1, lat2, lon2):
    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)
    dlon = math.radians(lon2 - lon1)

    x = math.sin(dlon) * math.cos(lat2)
    y = (
        math.cos(lat1) * math.sin(lat2)
        - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
    )

    return math.atan2(x, y)


def destination_point(lat, lon, distance_m, bearing):
    R = 6371000
    lat1 = math.radians(lat)
    lon1 = math.radians(lon)

    lat2 = math.asin(
        math.sin(lat1) * math.cos(distance_m / R)
        + math.cos(lat1) * math.sin(distance_m / R) * math.cos(bearing)
    )

    lon2 = lon1 + math.atan2(
        math.sin(bearing) * math.sin(distance_m / R) * math.cos(lat1),
        math.cos(distance_m / R) - math.sin(lat1) * math.sin(lat2),
    )

    return math.degrees(lat2), math.degrees(lon2)


def point_at_distance(route, D, from_end=False):
    if from_end:
        route = list(reversed(route))

    acc = 0.0

    for i in range(len(route) - 1):
        lat1, lon1 = route[i]
        lat2, lon2 = route[i + 1]

        seg_len = geodesic((lat1, lon1), (lat2, lon2)).meters

        if acc + seg_len < D:
            acc += seg_len
        else:
            remain = D - acc
            bearing = calculate_bearing(lat1, lon1, lat2, lon2)
            return destination_point(lat1, lon1, remain, bearing)

    raise ValueError("Khoảng cách D vượt quá chiều dài tuyến")


def calculate_points(kml_file, D):
    route = read_route_from_kml(kml_file)
    p_start = point_at_distance(route, D, from_end=False)
    p_end = point_at_distance(route, D, from_end=True)
    return p_start, p_end
