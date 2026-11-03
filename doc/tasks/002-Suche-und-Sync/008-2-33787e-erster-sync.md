# 2-008-33787e-Erster_Sync

## Meta

- ID: 33787e
- Type: 2
- Number: 008
- Status: R
- Phase: 002-Suche-und-Sync
- review: user
- assignee-type: agent
- source: doc/spec.md#Synchronisation

## Erster Sync

> `calendar-sync` für alle drei Kalender; Bericht prüfen.

## History

- 2026-10-13T11:24:31+00:00: M | Object created
- 2026-11-03T11:15:17+00:00: M [ ] -> [~] | starting
- 2026-11-03T11:15:17+00:00: T [~] -> [~] | Sync-Bericht (Quelle: Sessions 2026-11-03, Freigabe jeweils durch User): Sync 1 nach Task 9a7221: Feuerwerke 8 angelegt (inkl. Mainfest), Weihnachtsmaerkte 42 und Events 1 unveraendert, 0 geloescht, 0 Fehler. Sync 2 nach Task de5a72: Events 13 angelegt, Feuerwerke 1 angelegt + 2 aktualisiert (parent-Verknuepfung), Weihnachtsmaerkte 42 unveraendert, 0 geloescht, 0 Fehler. Pruefabfragen: Feuerwerke (10 Termine) und Events (14 Termine) nach Sync 2 ohne Abweichung zum Soll (jede ID einmal, Hash gleich), keine fremden/verwaisten Termine. Ganztaegige Termine: Google-Ende exklusiv entspricht inklusivem end im Repo (z.B. Rhein in Flammen Bingen-Ruedesheim 03.07. -> Ende 04.07.), kein Tagesversatz. Einschraenkung: Weihnachtsmaerkte nach Sync 1 nicht erneut abgefragt (Soll unveraendert); get_event-Einzelpruefung nicht gesondert durchgefuehrt.
- 2026-11-03T11:15:22+00:00: M [~] -> [R] | Sync-Bericht vollstaendig, Review durch User
