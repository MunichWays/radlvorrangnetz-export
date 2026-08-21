import unittest

from scripts.build_osm_bicycle_repair_stations import OVERPASS_QUERY


class BicycleRepairStationsQueryTest(unittest.TestCase):
    def test_selects_repair_stations_in_upper_bavaria(self):
        self.assertIn('["name"="Oberbayern"]', OVERPASS_QUERY)
        self.assertIn('["amenity"="bicycle_repair_station"]', OVERPASS_QUERY)

    def test_excludes_restricted_access(self):
        for value in ("private", "no", "customers", "permit", "members"):
            self.assertIn(value, OVERPASS_QUERY)


if __name__ == "__main__":
    unittest.main()
