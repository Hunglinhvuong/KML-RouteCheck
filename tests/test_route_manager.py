import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.route_manager import list_routes, parse_route_name


def test_list_routes_filters_kml_files():
    routes = list_routes("quynh")
    assert routes
    assert all(route.lower().endswith(".kml") for route in routes)


def test_parse_route_name_handles_dollar_and_dot_formats():
    assert parse_route_name("CSG14.NA_HMA_QUYNH_THIEN$NA_HMA_QUYNH_XUAN.kml") == (
        "NA_HMA_QUYNH_THIEN",
        "NA_HMA_QUYNH_XUAN",
    )
