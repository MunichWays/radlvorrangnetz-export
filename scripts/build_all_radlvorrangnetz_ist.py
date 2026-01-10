#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import re
from pathlib import Path
from typing import Any, Optional
from urllib.parse import urlparse, parse_qs

INPUT = "data/IST_RadlVorrangNetz_MunichWays_V20.geojson"
OUTPUT = "data/ALL_RadlVorrangNetz_Ist.geojson"

# Spalten (Properties) entfernen
DROP_FIELDS = {
    "munichways_net_type_plan",
    "osm_access",
}

MAPILLARY_LINK_FIELD = "munichways_mapillary_link"
MEASURE_CATEGORY_LINK_FIELD = "munichways_measure_category_link"

# Regex: Text zwischen target="_blank"> ... </a>
MEASURE_CATEGORY_RE = re.compile(r'_blank">\s*([^<]+?)\s*</a>', re.IGNORECASE)


def is_empty(v: Any) -> bool:
    """True wenn None, leerer String, nur Whitespace oder '-'."""
    if v is None:
        return True
    if isinstance(v, str):
        s = v.strip()
        return s == "" or s == "-"
    return False


def extract_mapillary_img_id_from_link(value: Any) -> Optional[str]:
    """
    Extrahiert pKey aus einem Mapillary-Link, z.B.:
    https://www.mapillary.com/app/?pKey=1713341692468300  -> "1713341692468300"
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


def extract_measure_category(value: Any) -> Optional[str]:
    """
    Extrahiert den Ankertext aus munichways_measure_category_link:
    z.B. <a ... target="_blank">Fahrrad Symbole </a> -> "Fahrrad Symbole"
    """
    if not isinstance(value, str):
        return None
    s = value.strip()
    if not s or s == "-":
        return None

    m = MEASURE_CATEGORY_RE.search(s)
    if not m:
        return None
    text = m.group(1).strip()
    return text or None


def main() -> None:
    in_path = Path(INPUT)
    out_path = Path(OUTPUT)

    data = json.loads(in_path.read_text(encoding="utf-8"))
    if data.get("type") != "FeatureCollection":
        raise ValueError(f"Erwarte FeatureCollection, bekommen: {data.get('type')}")

    features = data.get("features", [])
    kept = []

    for feature in features:
        if not isinstance(feature, dict) or feature.get("type") != "Feature":
            continue

        props = feature.get("properties") or {}

        # Fehlerhafte Datensätze raus: wenn osm_class_bicycle UND munichways_id leer
        # (betrifft aktuell osm_id 323080839, 28169808, 24042379)
        if is_empty(props.get("osm_class_bicycle")) and is_empty(props.get("munichways_id")):
            continue

        # Spalten entfernen
        for k in DROP_FIELDS:
            if k in props:
                props.pop(k, None)

        # Zusätzliche Spalten am Ende
        props["mapillary_img_id"] = extract_mapillary_img_id_from_link(props.get(MAPILLARY_LINK_FIELD))
        props["measure_category"] = extract_measure_category(props.get(MEASURE_CATEGORY_LINK_FIELD))

        kept.append(feature)

    out = dict(data)
    out["features"] = kept

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")

    print(f"Input features:  {len(features)}")
    print(f"Output features: {len(kept)}")
    print(f"Written to:      {out_path}")


if __name__ == "__main__":
    main()
