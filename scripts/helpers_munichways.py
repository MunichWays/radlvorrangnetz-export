#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from html import unescape
from typing import Any, Optional
from urllib.parse import urlparse, parse_qs

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
    <a href="..."> BA22 Aubing-Lochhausen-Langwied</a> -> "BA22 Aubing-Lochhausen-Langwied"
    "Puchheim" -> "Puchheim"
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


def is_munich_ba_district(value: Optional[Any]) -> bool:
    """
    True nur für Datensätze mit BA01 bis BA25.
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
