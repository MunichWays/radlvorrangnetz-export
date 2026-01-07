#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

INPUT = "data/IST_RadlVorrangNetz_MunichWays_V20.geojson"
OUTPUT = "data/Status_Umsetzung_Radentscheid.geojson"

FIELD = "munichways_status_implementation"

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
    Gibt genau einen bereinigten Status zurück (oder None).
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

        if cleaned:
            # Feld bereinigen (1:1 sonst unverändert)
            props[FIELD] = cleaned
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
