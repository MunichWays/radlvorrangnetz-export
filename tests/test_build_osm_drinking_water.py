import unittest

from scripts.build_osm_drinking_water import OVERPASS_QUERY, to_geojson


class ToGeoJsonTest(unittest.TestCase):
    def test_converts_nodes_and_centers_and_skips_invalid_elements(self):
        source = {
            "elements": [
                {
                    "type": "node",
                    "id": 2,
                    "lat": 48.1,
                    "lon": 11.5,
                    "tags": {
                        "amenity": "drinking_water",
                        "drinking_water": "yes",
                        "operator": "Stadtwerke",
                    },
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

        result = to_geojson(source, generated_at="2026-08-20T03:00:00Z")

        self.assertEqual(result["type"], "FeatureCollection")
        self.assertEqual(
            result["properties"],
            {"schemaVersion": 1, "generatedAt": "2026-08-20T03:00:00Z"},
        )
        self.assertEqual(len(result["features"]), 2)
        node = result["features"][0]
        self.assertEqual(node["geometry"]["coordinates"], [11.5, 48.1])
        self.assertEqual(
            node["properties"]["osm_url"],
            "https://www.openstreetmap.org/node/2",
        )
        self.assertEqual(node["properties"]["operator"], "Stadtwerke")
        self.assertNotIn("opening_hours", node["properties"])
        self.assertNotIn("drinking_water:legal", node["properties"])
        self.assertEqual(result["features"][1]["geometry"]["coordinates"], [11.6, 48.2])

    def test_all_selectors_require_explicit_drinking_water_yes(self):
        self.assertEqual(OVERPASS_QUERY.count('["drinking_water"="yes"]'), 3)


if __name__ == "__main__":
    unittest.main()
