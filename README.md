# radlvorrangnetz-export
Build pipeline to generate the RadlVorrangNetz app GeoJSON. Converts IST_RadlVorrangNetz_MunichWays_V20.geojson into radlvorrangnetz_app_V07.geojson without Carto, using a reproducible Python script and GitHub Actions for automated exports.

Siehe Wiki https://github.com/MunichWays/masterliste/wiki/GeoJSON-Datei-erstellen#v07-geojson-app-datei-erstellen

Liest die V20er Datei vom Webspace https://www.munichways.de/App/ und erstellt daraus die V07 App Datei. 

Neu ab 2026 per github workflow aus der V20er Datei erstellen (ohne postgreSQL DB im Carto alt).
