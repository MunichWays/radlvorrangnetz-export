#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from pathlib import Path
from typing import Any, List, Optional

from helpers_munichways import (
    extract_mapillary_img_id_from_link,
    is_munich_ba_district,
)

INPUT = "data/IST_RadlVorrangNetz_MunichWays_V20.geojson"
OUTPUT = "data/Status_Umsetzung_Radentscheid.geojson"

FIELD = "munichways_status_implementation"
MAPILLARY_LINK_FIELD = "munichways_mapillary_link"
DISTRICT_FIELD = "munichways_district_link"

ALLOWED: List[str] = [
    "beschlossen",
    "in_Umsetzung_BAU",
    "umgesetzt_allgemein",
    "umgesetzt_nach_REM",
]


def split_tokens(value: Optional[Any]) -> List[str]:
    if not isinstance(value, str):
        return []
    return [t.strip() for t in value.split(",") if t.strip()]


def clean_status(value: Optional[Any]) -> Optional[str]:
    """
    Gibt genau einen bereinigten Status zurück - oder None.
    Priorität entsprechend Reihenfolge in ALLOWED.
    """
    tokens = split_tokens(value)
    for status in ALLOWED:
        if status in tokens:
            return status
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

        cleaned = clean_status(props.get(FIELD))
        if not cleaned:
            continue

        if not is_munich_ba_district(props.get(DISTRICT_FIELD)):
            continue

        props[FIELD] = cleaned

        props["mapillary_img_id"] = extract_mapillary_img_id_from_link(
            props.get(MAPILLARY_LINK_FIELD)
        )

        kept.append(feature)

    out = dict(data)
    out["features"] = kept

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")

    print(f"Input features: {len(features)}")
    print(f"Output features: {len(kept)}")
    print(f"Written to: {out_path}")


if __name__ == "__main__":
    main()
