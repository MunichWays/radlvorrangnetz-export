#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from pathlib import Path
from typing import Any, List, Optional

from helpers_munichways import (
    extract_link_text,
    extract_mapillary_img_id_from_link,
    is_munich_ba_district,
)

INPUT = "data/IST_RadlVorrangNetz_MunichWays_V20.geojson"
OUTPUT = "data/Kategorie_Markierungen.geojson"

FIELD = "munichways_measure_category_link"
MAPILLARY_LINK_FIELD = "munichways_mapillary_link"
DISTRICT_FIELD = "munichways_district_link"

ALLOWED: List[str] = [
    "Fahrrad Symbole",
    "Dooring-Schutzstreifen",
]


def clean_category(value: Optional[Any]) -> Optional[str]:
    """
    Gibt genau eine bereinigte Kategorie zurück - oder None.
    """
    text = extract_link_text(value)
    if not text:
        return None

    for category in ALLOWED:
        if text == category:
            return category

    return None


def main() -> None:
    in_path = Path(INPUT)
    out_path = Path(OUTPUT)

    data = json.loads(in_path.read_text(encoding="utf-8"))

    features = data.get("features", [])
    kept = []

    for feature in features:
        if feature.get("type") != "Feature":
            continue

        props = feature.get("properties") or {}

        cleaned_category = clean_category(props.get(FIELD))
        if not cleaned_category:
            continue

        if not is_munich_ba_district(props.get(DISTRICT_FIELD)):
            continue

        props[FIELD] = cleaned_category

        props["mapillary_img_id"] = extract_mapillary_img_id_from_link(
            props.get(MAPILLARY_LINK_FIELD)
        )

        kept.append(feature)

    out = dict(data)
    out["features"] = kept

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(out, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"Input features: {len(features)}")
    print(f"Output features: {len(kept)}")
    print(f"Written to: {out_path}")


if __name__ == "__main__":
    main()
