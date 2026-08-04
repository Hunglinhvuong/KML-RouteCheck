import os
from pathlib import Path

from utils.pathing import get_data_dir

KML_DIR = get_data_dir()


def list_routes(keyword=None):
    routes = []

    if not KML_DIR.exists() or not KML_DIR.is_dir():
        return routes

    for path in sorted(KML_DIR.iterdir()):
        if path.is_file() and path.suffix.lower() == ".kml":
            name = path.name
            if not keyword or keyword.lower() in name.lower():
                routes.append(name)

    return routes

def parse_route_name(filename):
    """
    CSG14_7. NA_HMA_QUYNH_THIEN@NA_HMA_QUYNH_XUAN.kml
    hoặc
    CSG14_7. NA_HMA_QUYNH_THIEN - NA_HMA_QUYNH_XUAN.kml

    -> ("NA_HMA_QUYNH_THIEN", "NA_HMA_QUYNH_XUAN")
    """

    # 1. Bỏ .kml
    name = os.path.splitext(filename)[0]

    # 2. Bỏ phần trước dấu chấm (lấy phần sau dấu . đầu tiên)
    if "." in name:
        name = name.split(".", 1)[1]

    # 3. Bỏ toàn bộ dấu cách
    name = name.replace(" ", "")

    # 4. Tách điểm đầu – cuối
    if "$" in name:
        start, end = name.split("$", 1)
    else:
        start = end = name

    return start, end