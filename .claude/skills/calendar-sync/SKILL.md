---
name: calendar-sync
description: Gleicht die drei Google-Kalender (Weihnachtsmärkte, Feuerwerke, Events und Feste) mit dem Repo-Stand ab – anlegen, aktualisieren, löschen. Nutzen nach jeder Datenänderung, bei „sync“, „Kalender aktualisieren“ oder „Kalender abgleichen“.
---

# calendar-sync

Das Repo ist der **Soll-Zustand**, der Kalender der **Ist-Zustand**. Der Abgleich läuft über die
Sync-Fußzeile `ec:<id> · h:<hash>` am Ende jeder Terminbeschreibung. Werkzeug: der
Google-Calendar-MCP-Connector (`list_events`, `create_event`, `update_event`, `delete_event`).

## Schritte

1. **Soll erzeugen.** `python3 tools/ec.py render > "$SCRATCH/soll.json"` (Scratchpad verwenden).
   Bricht der Befehl ab, zuerst die `validate`-Fehler beheben; ohne gültigen Soll-Zustand kein Sync.
   Jeder Eintrag enthält `id`, `hash`, `calendarId` und die fertigen Felder für den Connector.

2. **Ist lesen**, je Kalender aus `config/settings.yaml` (`calendars.*.google_id`):
   `list_events` mit `calendarId`, `startTime` = heute `T00:00:00`, `endTime` = heute + 2 Jahre,
   `pageSize` 250, `timeZone` `Europe/Berlin`; alle Seiten über `nextPageToken`. Aus jeder
   Beschreibung die Fußzeile per Regex `ec:(\d{4}/[\w-]+) · h:([0-9a-f]{8})` ziehen.
   Mehrtägige Termine, die vor heute begonnen haben und noch laufen, gehören dazu.

3. **Abgleichen** – jede Soll-ID und jeder Ist-Termin landet in genau einer Klasse:

   | Klasse | Bedingung | Aktion |
   |---|---|---|
   | neu | Soll-ID ohne Ist-Termin | `create_event` |
   | geändert | gleiche ID, anderer Hash | `update_event` (alle Felder) |
   | Farbe zurücksetzen | geändert, Ist hat `colorId`, Soll hat `colorId: null` | `delete_event` + `create_event` (eine Farbe lässt sich per Update nicht entfernen) |
   | unverändert | gleiche ID, gleicher Hash | nichts |
   | verwaist | Ist-ID nicht im Soll (z. B. abgesagt, gelöscht, verschoben) | `delete_event` |
   | fremd | Ist-Termin ohne Fußzeile | `delete_event`, im Bericht einzeln aufführen |
   | doppelt | mehrere Ist-Termine mit gleicher ID | ersten behalten (wie oben behandeln), Rest `delete_event` |

   Termine, die vor heute **geendet** haben, liegen außerhalb des Listenfensters und werden nie angefasst.

4. **Schreiben.** Felder 1:1 aus dem Soll übernehmen: `calendarId`, `summary`, `location`,
   `description`, `startTime`, `endTime`, `allDay`, `timeZone`, `colorId` (nur wenn nicht null),
   `availability`, `useDefaultReminders`. Bei Create/Update/Delete immer
   `notificationLevel: NONE`. Schlägt ein Aufruf fehl, einmal wiederholen, dann im Bericht als Fehler führen
   und mit dem nächsten Termin weitermachen.

5. **Prüfen.** Schritt 2 erneut ausführen: Jede Soll-ID existiert genau einmal mit dem Soll-Hash, es gibt
   keine fremden oder verwaisten Termine mehr. Abweichungen gehen in den Bericht.
   Beim ersten Sync zusätzlich einen ganztägigen Termin mit `get_event` prüfen: Das letzte Tag muss dem
   `end` im Repo entsprechen (Google-Ende exklusiv). Ist es um einen Tag verschoben, abbrechen und melden.

## Bericht

Je Kalender eine Zeile: angelegt / aktualisiert / gelöscht / unverändert / Fehler. Danach jeden gelöschten
fremden Termin mit Titel und Datum und jeden Fehler mit Meldung. Fertig ist der Sync, wenn Schritt 5 ohne
Abweichung durchläuft oder jede Abweichung im Bericht steht.
