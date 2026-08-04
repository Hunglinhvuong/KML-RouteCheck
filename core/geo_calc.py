from geopy.distance import geodesic
from pyproj import Geod
from core.kml_reader import read_route_from_kml

# WGS84 ellipsoid (chuẩn GPS, Google Earth, QGIS)
geod = Geod(ellps="WGS84")


def point_at_distance(route, D, from_end=False):
    """
    Tìm điểm cách đầu/cuối tuyến D mét
    Nội suy geodesic CHUẨN GIS
    """

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

            # Tính azimuth thật trên ellipsoid
            az12, _, _ = geod.inv(lon1, lat1, lon2, lat2)

            # Đi đúng remain mét theo geodesic
            lon, lat, _ = geod.fwd(lon1, lat1, az12, remain)

            return lat, lon

    raise ValueError("Khoảng cách D vượt quá chiều dài tuyến")


def calculate_points(kml_file, D):
    route = read_route_from_kml(kml_file)

    p_start = point_at_distance(route, D, from_end=False)
    p_end = point_at_distance(route, D, from_end=True)

    return p_start, p_end
