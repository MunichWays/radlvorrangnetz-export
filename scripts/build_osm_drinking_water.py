#!/usr/bin/env python3
"""Export publicly accessible drinking-water POIs in Upper Bavaria from OSM."""

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


DEFAULT_ENDPOINT = "https://overpass-api.de/api/interpreter"
DEFAULT_OUTPUT = "data/poi/drinking_water.geojson"

OVERPASS_QUERY = """[out:json][timeout:90];
area["boundary"="administrative"]["admin_level"="5"]["name"="Oberbayern"]->.searchArea;
(
  nwr["amenity"="drinking_water"]["drinking_water"="yes"]
    ["access"!~"^(private|no|customers|permit|delivery|destination)$"]
    (area.searchArea);
  nwr["man_made"="water_tap"]["drinking_water"="yes"]
    ["access"!~"^(private|no|customers|permit|delivery|destination)$"]
    (area.searchArea);
  nwr["amenity"="fountain"]["drinking_water"="yes"]
    ["access"!~"^(private|no|customers|permit|delivery|destination)$"]
    (area.searchArea);
);
out tags center;
"""


def fetch_overpass(endpoint: str, retries: int = 3) -> dict[str, Any]:
    """Submit the query to Overpass, retrying temporary network/server errors."""
    body = urlencode({"data": OVERPASS_QUERY}).encode("utf-8")
    request = Request(
        endpoint,
        data=body,
        headers={
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "User-Agent": "MunichWays-radlvorrangnetz-export/1.0",
        },
    )

    for attempt in range(1, retries + 1):
        try:
            with urlopen(request, timeout=120) as response:
                return json.load(response)
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError):
            if attempt == retries:
                raise
            time.sleep(5 * attempt)
    raise RuntimeError("Overpass request failed")


def element_coordinates(element: dict[str, Any]) -> tuple[float, float] | None:
    """Return longitude/latitude for a node or an Overpass center."""
    if "lon" in element and "lat" in element:
        return float(element["lon"]), float(element["lat"])
    center = element.get("center") or {}
    if "lon" in center and "lat" in center:
        return float(center["lon"]), float(center["lat"])
    return None


def to_geojson(
    overpass_data: dict[str, Any], generated_at: str | None = None
) -> dict[str, Any]:
    """Convert Overpass JSON elements to a point FeatureCollection for uMap."""
    if generated_at is None:
        generated_at = (
            datetime.now(timezone.utc)
            .isoformat(timespec="seconds")
            .replace("+00:00", "Z")
        )

    features = []
    seen: set[tuple[str, int]] = set()

    for element in overpass_data.get("elements", []):
        osm_type = element.get("type")
        osm_id = element.get("id")
        coordinates = element_coordinates(element)
        if osm_type not in {"node", "way", "relation"} or osm_id is None or not coordinates:
            continue

        key = (osm_type, int(osm_id))
        if key in seen:
            continue
        seen.add(key)

        properties = dict(element.get("tags") or {})
        properties["osm_type"] = osm_type
        properties["osm_id"] = int(osm_id)
        properties["osm_url"] = f"https://www.openstreetmap.org/{osm_type}/{osm_id}"
        features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": list(coordinates)},
                "properties": properties,
            }
        )

    features.sort(key=lambda feature: (feature["properties"]["osm_type"], feature["properties"]["osm_id"]))
    return {
        "type": "FeatureCollection",
        "properties": {"schemaVersion": 1, "generatedAt": generated_at},
        "features": features,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    output = Path(args.output)
    geojson = to_geojson(fetch_overpass(args.endpoint))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(geojson, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {output} with {len(geojson['features'])} features.")


if __name__ == "__main__":
    main()
