import xml.etree.ElementTree as ET


def read_route_from_kml(kml_file):
    tree = ET.parse(kml_file)
    root = tree.getroot()

    ns = {
        "kml": "http://www.opengis.net/kml/2.2",
        "gx": "http://www.google.com/kml/ext/2.2",
    }

    coords = []

    # LineString
    for ls in root.findall(".//kml:LineString/kml:coordinates", ns):
        text = ls.text.strip()
        for p in text.split():
            lon, lat, *_ = map(float, p.split(","))
            coords.append((lat, lon))

    # gx:Track
    if not coords:
        for track in root.findall(".//gx:Track", ns):
            for coord in track.findall("gx:coord", ns):
                lon, lat, *_ = map(float, coord.text.split())
                coords.append((lat, lon))

    if not coords:
        raise ValueError("Không tìm thấy dữ liệu tuyến trong KML")

    return coords
