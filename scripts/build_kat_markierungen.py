#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import re
from html import unescape
from pathlib import Path
from typing import Any, List, Optional
from urllib.parse import urlparse, parse_qs

INPUT = "data/IST_RadlVorrangNetz_MunichWays_V20.geojson"
OUTPUT = "data/Kategorie_Markierungen.geojson"

FIELD = "munichways_measure_category_link"
MAPILLARY_LINK_FIELD = "munichways_mapillary_link"
DISTRICT_FIELD = "munichways_district_link"

ALLOWED: List[str] = [
    "Fahrrad Symbole",
    "Dooring-Schutzstreifen",
]

ALLOWED_BA = {
    "BA01", "BA02", "BA03", "BA04", "BA05",
    "BA06", "BA07", "BA08", "BA09", "BA10",
    "BA11", "BA12", "BA13", "BA14", "BA15",
    "BA16", "BA17", "BA18", "BA19", "BA20",
    "BA21", "BA22", "BA23", "BA24", "BA25",
}


def extract_link_text(value: Optional[Any]) -> Optional[str]:
    """
    Extrahiert den sichtbaren Text aus einem HTML-Link.
    Beispiele:
    <a href="...">Fahrrad Symbole </a> -> "Fahrrad Symbole"
    <a href="..."> BA22 Aubing-Lochhausen-Langwied</a> -> "BA22 Aubing-Lochhausen-Langwied"
    """
    if not isinstance(value, str):
        return None

    value = value.strip()
    if not value:
        return None

    value = unescape(value)

    m = re.search(r'>([^<]+)<', value)
    if m:
        return m.group(1).strip()

    return value.strip()


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


def is_munich_ba_district(value: Optional[Any]) -> bool:
    """
    True nur für Datensätze mit BA01 bis BA25.
    Beispiele:
    "Puchheim" -> False
    "<a ...> BA22 Aubing-Lochhausen-Langwied</a>" -> True
    """
    text = extract_link_text(value)
    if not text:
        return False

    for ba in ALLOWED_BA:
        if ba in text:
            return True

    return False


def extract_mapillary_img_id_from_link(value: Optional[Any]) -> Optional[str]:
    """
    Extrahiert pKey aus einem Mapillary-Link.
    Beispiel:
    https://www.mapillary.com/app/?pKey=1713341692468300 -> "1713341692468300"
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
