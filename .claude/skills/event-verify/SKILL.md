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

2. **Pflichtquellen lesen.** Je Kalender der Prüfliste die `required_sources` aus
   `python3 tools/ec.py checklist --calendar <kalender>` einmal lesen (Umgang mit nicht lesbaren Quellen wie
   in `event-search`, Schritt 3 b) und daraus Hinweise auf geänderte oder abgesagte Termine der Prüfliste
   übernehmen.

3. **Jeden Termin prüfen.** Zuerst die `sources` und die Homepage öffnen, dann gezielt suchen – die
   Pflichtquellen ergänzen das, ersetzen es nicht. Abgleichen: Datum, Uhrzeit (Shows), Öffnungszeiten, Ort,
   Absage.

4. **Ergebnis eintragen** – genau eines je Termin:
   - unverändert: nur `checked_at` = heute,
   - geändert: Felder korrigieren, `sources`/`checked_at` aktualisieren, Status ggf. hochstufen;
     liegt ein neues Startdatum vor, Datei mit neuem Namen anlegen, alte löschen und `parent`-Verweise
     von Shows auf die neue ID umstellen,
   - abgesagt: `status: abgesagt`, Quelle in `sources`,
   - keine Information gefunden: Status bleibt, `status_note` ergänzen.

5. **Abschließen** gemäß Arbeitsablauf in `CLAUDE.md`.

## Bericht

Warnung oben, falls eine Pflichtquelle `nicht erreichbar` war; dann Pflichtquellen mit Status (`gelesen` /
`teilweise (über Suche)` / `nicht erreichbar`) und die Tabelle: Event-ID, alter → neuer Status, Änderung,
Quelle. Fertig ist die Prüfung, wenn jede Pflichtquelle einen Status und jeder Termin der Prüfliste genau
ein Ergebnis aus Schritt 4 hat.

## Widersprüchliche Zeiträume

Nennen Quellen unterschiedliche Zeiträume: nur die Schnittmenge als `start`/`end` eintragen und den Widerspruch mit allen Varianten und Quellen in `status_note` vermerken (Regel in `CLAUDE.md`, Abschnitt „Status eines Termins“). Nicht zusammenhängende Schnittmengen dem User melden.
