import unittest

from scripts.build_osm_public_toilets import OVERPASS_QUERY


class PublicToiletsQueryTest(unittest.TestCase):
    def test_selects_toilets_in_upper_bavaria(self):
        self.assertIn('["name"="Oberbayern"]', OVERPASS_QUERY)
        self.assertIn('["amenity"="toilets"]', OVERPASS_QUERY)

    def test_excludes_restricted_access(self):
        for value in ("private", "no", "customers", "permit", "members"):
            self.assertIn(value, OVERPASS_QUERY)


if __name__ == "__main__":
    unittest.main()
