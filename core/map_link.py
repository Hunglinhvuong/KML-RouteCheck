# core/map_link.py
import math

def calc_center_zoom(p1, p2):
    lat1, lon1 = p1
    lat2, lon2 = p2

    center_lat = (lat1 + lat2) / 2
    center_lon = (lon1 + lon2) / 2

    # Khoảng cách xấp xỉ (km)
    dist = math.sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2) * 111

    # Ước lượng zoom
    if dist < 0.2:
        zoom = 17
    elif dist < 0.5:
        zoom = 16
    elif dist < 1:
        zoom = 15
    elif dist < 2:
        zoom = 14
    elif dist < 5:
        zoom = 13
    else:
        zoom = 12

    return center_lat, center_lon, zoom
