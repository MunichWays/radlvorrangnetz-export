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

ALLOWED: List[str] = [
    "Fahrrad Symbole",
    "Dooring-Schutzstreifen",
]


def extract_link_text(value: Optional[Any]) -> Optional[str]:
    """
    Extrahiert den sichtbaren Text aus einem HTML-Link.
    Beispiel:
    <a href="...">Fahrrad Symbole </a> -> "Fahrrad Symbole"
    """
    if not isinstance(value, str):
        return None

    value = value.strip()
    if not value:
        return None

    # HTML entities zurückwandeln
    value = unescape(value)

    # Inhalt zwischen > ... <
    m = re.search(r'>([^<]+)<', value)
    if m:
        return m.group(1).strip()

    # Falls doch mal Klartext ohne HTML kommt
    return value.strip()


def clean_category(value: Optional[Any]) -> Optional[str]:
    """
    Gibt genau eine bereinigte Kategorie zurück (oder None).
    """
    text = extract_link_text(value)
    if not text:
        return None

    for category in ALLOWED:
        if text == category:
            return category

    return None


def extract_mapillary_img_id_from_link(value: Optional[Any]) -> Optional[str]:
    """
    Extrahiert pKey aus einem Mapillary-Link, z.B.:
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
        cleaned = clean_category(props.get(FIELD))

        if cleaned:
            # Feld bereinigen: nur noch Klartext
            props[FIELD] = cleaned

            # mapillary_img_id aus munichways_mapillary_link ergänzen
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
