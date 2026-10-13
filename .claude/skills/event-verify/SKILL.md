---
name: event-verify
description: Prüft vorhandene Termine (geschätzt, angekündigt, bald anstehend) gegen aktuelle Quellen, stuft den Status hoch und zieht Änderungen und Absagen nach. Nutzen bei „verifizieren“, „prüfen“, „Termine aktualisieren“ oder „Status prüfen“.
---

# event-verify

Statusregeln und Herkunftsregeln: `CLAUDE.md`.

## Schritte

1. **Prüfliste bilden** (Rahmen aus dem Auftrag, sonst Standard):
   - alle `geschätzt` und `angekündigt` im Suchhorizont:
     `python3 tools/ec.py list --status geschätzt --from <heute>` bzw. `--status angekündigt`,
   - alle `bestätigt`, die in den nächsten 30 Tagen beginnen und deren `checked_at` älter als 14 Tage ist.

2. **Jeden Termin prüfen.** Zuerst die `sources` und die Homepage öffnen, dann gezielt suchen. Abgleichen:
   Datum, Uhrzeit (Shows), Öffnungszeiten, Ort, Absage.

3. **Ergebnis eintragen** – genau eines je Termin:
   - unverändert: nur `checked_at` = heute,
   - geändert: Felder korrigieren, `sources`/`checked_at` aktualisieren, Status ggf. hochstufen;
     liegt ein neues Startdatum vor, Datei mit neuem Namen anlegen, alte löschen und `parent`-Verweise
     von Shows auf die neue ID umstellen,
   - abgesagt: `status: abgesagt`, Quelle in `sources`,
   - keine Information gefunden: Status bleibt, `status_note` ergänzen.

4. **Abschließen** gemäß Arbeitsablauf in `CLAUDE.md`.

## Bericht

Tabelle: Event-ID, alter → neuer Status, Änderung, Quelle. Fertig ist die Prüfung, wenn jeder Termin der
Prüfliste genau ein Ergebnis aus Schritt 3 hat.
