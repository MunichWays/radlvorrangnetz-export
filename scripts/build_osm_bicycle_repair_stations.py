#!/usr/bin/env python3
"""Export public bicycle repair stations in Upper Bavaria from OSM."""

import argparse
import json
from pathlib import Path

try:
    from scripts.build_osm_drinking_water import (
        DEFAULT_ENDPOINT,
        fetch_overpass,
        to_geojson,
    )
except ModuleNotFoundError:
    from build_osm_drinking_water import DEFAULT_ENDPOINT, fetch_overpass, to_geojson

DEFAULT_OUTPUT = "data/poi/bicycle_repair_stations.geojson"

OVERPASS_QUERY = """[out:json][timeout:90];
area["boundary"="administrative"]["admin_level"="5"]["name"="Oberbayern"]->.searchArea;
nwr["amenity"="bicycle_repair_station"]
  ["access"!~"^(private|no|customers|permit|delivery|destination|members)$"]
  (area.searchArea);
out tags center;
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    output = Path(args.output)
    geojson = to_geojson(fetch_overpass(args.endpoint, OVERPASS_QUERY))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(geojson, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {output} with {len(geojson['features'])} features.")


if __name__ == "__main__":
    main()
