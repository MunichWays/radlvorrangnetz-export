import unittest

from scripts.build_osm_drinking_water import to_geojson


class ToGeoJsonTest(unittest.TestCase):
    def test_converts_nodes_and_centers_and_skips_invalid_elements(self):
        source = {
            "elements": [
                {
                    "type": "node",
                    "id": 2,
                    "lat": 48.1,
                    "lon": 11.5,
                    "tags": {"amenity": "drinking_water"},
                },
                {
                    "type": "way",
                    "id": 3,
                    "center": {"lat": 48.2, "lon": 11.6},
                    "tags": {"name": "Brunnen"},
                },
                {"type": "relation", "id": 4, "tags": {}},
            ]
        }

        result = to_geojson(source)

        self.assertEqual(result["type"], "FeatureCollection")
        self.assertEqual(len(result["features"]), 2)
        node = result["features"][0]
        self.assertEqual(node["geometry"]["coordinates"], [11.5, 48.1])
        self.assertEqual(
            node["properties"]["osm_url"],
            "https://www.openstreetmap.org/node/2",
        )
        self.assertEqual(result["features"][1]["geometry"]["coordinates"], [11.6, 48.2])


if __name__ == "__main__":
    unittest.main()
