#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from pathlib import Path
from typing import Any, List, Optional
from urllib.parse import urlparse, parse_qs

INPUT = "data/IST_RadlVorrangNetz_MunichWays_V20.geojson"
OUTPUT = "data/ZIEL_RadlVorrangNetz.geojson"

FIELD = "munichways_net_type_target"
MAPILLARY_LINK_FIELD = "munichways_mapillary_link"

ALLOWED: List[str] = [
    "1_Rad-Ring",
    "4_Rad-Ring",
    "2_Rad-Schnell-Verbindung",
    "3_Rad-Vorrang-Haupt",
    "4_Rad-Vorrang",
]


def split_tokens(value: Optional[Any]) -> List[str]:
    if not isinstance(value, str):
        return []
    return [t.strip() for t in value.split(",") if t.strip()]


def clean_value(value: Optional[Any]) -> Optional[str]:
    """
    Gibt genau einen bereinigten Ziel-Netztyp zurück (oder None).
    Priorität entsprechend Reihenfolge in ALLOWED.
    """
    tokens = split_tokens(value)
    for v in ALLOWED:
        if v in tokens:
            return v
    return None


def extract_mapillary_img_id_from_link(value: Optional[Any]) -> Optional[str]:
    """
    Extrahiert pKey aus einem Mapillary-Link, z.B.:
    https://www.mapillary.com/app/?pKey=1713341692468300
    """
    if not isinstance(value, str):
        return None
    value = value.strip()
    if not value or value == "-":
        return None

    try:
        parsed = urlparse(value)
        qs = parse_qs(parsed.query)
        pkeys = qs.get("pKey") or qs.get("pkey")
        if not pkeys:
            return None
        pkey = (pkeys[0] or "").strip()
        return pkey or None
    except Exception:
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
        cleaned = clean_value(props.get(FIELD))

        if cleaned:
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
