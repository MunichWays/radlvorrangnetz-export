#!/usr/bin/env python3
import re
from datetime import datetime, timezone

import geopandas as gpd
import pandas as pd


INPUT = "data/IST_RadlVorrangNetz_MunichWays_V20.geojson"
OUTPUT = "data/radlvorrangnetz_app_V07.geojson"

DEFAULT_MAPILLARY_ID = "211265577336913"


def coalesce_series(*series_list):
    """Return first non-null value across provided Series, row-wise."""
    out = None
    for s in series_list:
        if s is None:
            continue
        if out is None:
            out = s
        else:
            out = out.combine_first(s)
    return out


def main():
    gdf = gpd.read_file(INPUT)

    # Filter: where m20.color <> 'blue'
    if "color" in gdf.columns:
        gdf = gdf[gdf["color"] != "blue"].copy()
    else:
        # If missing, keep all
        gdf = gdf.copy()

    # Helper columns (as strings where needed)
    def s(col):
        return gdf[col] if col in gdf.columns else pd.Series([pd.NA] * len(gdf), index=gdf.index)

    osm_name = s("osm_name")
    munichways_name = s("munichways_name")
    osm_surface = s("osm_surface")
    mw_rv_route = s("munichways_mw_rv_route")
    mw_current = s("munichways_current")
    osm_smoothness = s("osm_smoothness")
    osm_highway = s("osm_highway")
    osm_class_bicycle = s("osm_class_bicycle")
    munichways_target = s("munichways_target")
    measure_cat_link = s("munichways_measure_category_link")
    mw_description = s("munichways_description")
    mw_id = s("munichways_id")
    status_impl = s("munichways_status_implementation")
    mw_links = s("munichways_links")
    mapillary_link = s("munichways_mapillary_link")
    route_link = s("munichways_route_link")

    # name = COALESCE(osm_name, munichways_name, osm_surface, NULL)
    name = coalesce_series(osm_name, munichways_name, osm_surface)

    # MW_RV_Strecke = COALESCE(munichways_mw_rv_route, '-')
    MW_RV_Strecke = mw_rv_route.fillna("-")

    # ist_situation =
    # COALESCE(munichways_current, CONCAT('Oberfläche: ', CONCAT_WS(', ', osm_surface, 'Ebenheit: ...', 'Straßentyp: ...')))
    fallback_ist = (
        "Oberfläche: "
        + osm_surface.fillna("").astype("string")
        + ", "
        + ("Ebenheit: " + osm_smoothness.fillna("").astype("string"))
        + ", "
        + ("Straßentyp: " + osm_highway.fillna("").astype("string"))
    )
    # (Wenn osm_surface etc. leer sind, bleibt es trotzdem syntaktisch wie SQL-Logik “irgendwas”)
    ist_situation = mw_current.combine_first(fallback_ist)

    # happy_bike_level CASE mapping
    # Achtung: In SQL vergleicht ihr gegen Strings '3','2',... daher hier auch als string
    cb = osm_class_bicycle.astype("string")
    happy_map = {
        "3": "3 = hervorragend = grün",
        "2": "2 = gemütlich = grün",
        "1": "1 = durchschnittlich = gelb",
        "0": "0 = keine Aussage",
        "-1": "-1 = stressig = rot",
        "-2": "-2 = sehr stressig = schwarz",
        "-3": "-3 = Unter allen Umständen vermeiden = schwarz",
    }
    happy_bike_level = cb.map(happy_map)
    happy_bike_level = happy_bike_level.fillna(
        cb.apply(lambda v: "" if pd.isna(v) else "ungültiger Wert")
    )

    # massnahmen_kategorie_link COALESCE(... default html)
    default_massnahmen_link = '<a href="https://www.munichways.de/infrastruktur-elemente/" target="_blank">alle Infrastruktur-Elemente </a>'
    massnahmen_kategorie_link = measure_cat_link.fillna(default_massnahmen_link)

    # farbe mapping
    color = s("color").astype("string")
    farbe_map = {
        "green": "grün",
        "yellow": "gelb",
        "red": "rot",
        "black": "schwarz",
        "blue": "grau",  # class:bicycle=0
    }
    farbe = color.map(farbe_map).fillna("-")

    # mapillary_img_id = COALESCE(substring(link from 'pKey=([0-9]+)'), default)::text
    def extract_pkey(val):
        if val is None or (isinstance(val, float) and pd.isna(val)) or pd.isna(val):
            return None
        m = re.search(r"pKey=([0-9]+)", str(val))
        return m.group(1) if m else None

    extracted = mapillary_link.apply(extract_pkey)
    mapillary_img_id = extracted.fillna(DEFAULT_MAPILLARY_ID).astype("string")

    # strecken_link default
    default_strecken_link = '<a href="https://www.munichways.de/unsere-radlvorrang-strecken/" target="_blank">-n/a-Alle-Wege </a>'
    strecken_link = route_link.fillna(default_strecken_link)

    # last_updated = now()
    last_updated = datetime.now(timezone.utc).isoformat(timespec="seconds")

    # Build output schema
    out = gpd.GeoDataFrame(
        {
            "cartodb_id": 0,
            "name": name,
            "strecke": pd.NA,
            "MW_RV_Strecke": MW_RV_Strecke,
            "ist_situation": ist_situation,
            "happy_bike_level": happy_bike_level,
            "soll_massnahmen": munichways_target,
            "massnahmen_kategorie_link": massnahmen_kategorie_link,
            "beschreibung": mw_description,
            "munichways_id": mw_id,
            "status_umsetzung": status_impl,
            "links": mw_links,
            "farbe": farbe,
            "mapillary_img_id": mapillary_img_id,
            "bezirk_nummer": pd.NA,
            "bezirk_name": pd.NA,
            "netztyp_id": 4,
            "strecken_link": strecken_link,
            "last_updated": last_updated,
        },
        geometry=gdf.geometry,
        crs=gdf.crs,
    )

    # Write GeoJSON
    out.to_file(OUTPUT, driver="GeoJSON")

    print(f"Wrote {OUTPUT} with {len(out)} features.")


if __name__ == "__main__":
    main()

