# radlvorrangnetz-export
Build pipeline to generate the RadlVorrangNetz app GeoJSON. Converts IST_RadlVorrangNetz_MunichWays_V20.geojson into radlvorrangnetz_app_V07.geojson without Carto, using a reproducible Python script and GitHub Actions for automated exports.

Siehe Wiki https://github.com/MunichWays/masterliste/wiki/GeoJSON-Datei-erstellen#v07-geojson-app-datei-erstellen

Liest die V20er Datei vom Webspace https://www.munichways.de/App/ und erstellt daraus die V07 App Datei. 

Neu ab 2026 per github workflow aus der V20er Datei erstellen (ohne postgreSQL DB im Carto alt).

## OSM POI-Export

Der Workflow `osmexport.yml` exportiert jeden Montag öffentlich zugängliche
Trinkwasserstellen aus OpenStreetMap für den Regierungsbezirk Oberbayern nach
`App/poi/drinking_water.geojson` auf dem Webspace. Manuell kann die Datei mit
folgendem Befehl erzeugt werden:

Exportiert werden ausschließlich Objekte, die ausdrücklich mit
`drinking_water=yes` gekennzeichnet sind. Die FeatureCollection enthält den
Erstellungszeitpunkt in UTC. Neben der aktuellen Datei wird jeder Export unter
`App/save/drinking_water_<Zeitstempel>.geojson` archiviert.

```shell
python scripts/build_osm_drinking_water.py
```
