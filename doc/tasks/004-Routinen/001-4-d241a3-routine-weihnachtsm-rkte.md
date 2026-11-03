# 4-001-d241a3-Routine_Weihnachtsm_rkte

## Meta

- ID: d241a3
- Type: 4
- Number: 001
- Status: R
- Phase: 004-Routinen
- review: user
- assignee-type: agent
- source: doc/spec.md#Arbeitsweise

## Routine Weihnachtsmärkte

> Geplante Suche Juli–Oktober (Prompt `search-weihnachtsmaerkte.md`).

## History

- 2026-10-13T11:24:31+00:00: M | Object created
- 2026-11-03T11:20:44+00:00: M [ ] -> [~] | starting
- 2026-11-03T11:27:02+00:00: T [~] -> [~] | PR #3 nach main gemergt (User-Anweisung). Routine 'Weihnachtsmaerkte pruefen' angelegt (User-Freigabe): trig_01DZyU2vwW6NLgktdCMyekHs, Cron 'CRON_TZ=Europe/Berlin 41 5 10 7-12,1 *' (10.7., 10.8., 10.9., 10.10., 10.11., 10.12., 10.1. um 05:41 Berlin), frische Session je Lauf, Prompt event-search + event-verify, validate, Push auf main, calendar-sync mit Loeschen erlaubt, Push-Benachrichtigung an. Naechster Lauf 2026-11-10 05:41 Berlin. EINSCHRAENKUNG: create_trigger lehnt connectors fuer diese Organisation ab; die Routine speichert keine MCP-Connectors, gefeuerte Sessions haben daher voraussichtlich keinen Google-Calendar-Zugriff, calendar-sync wuerde fehlschlagen. Abhilfe: Routine in claude.ai (Routines-UI) mit Google-Calendar-Connector anlegen/erweitern.
- 2026-11-03T11:27:02+00:00: M [~] -> [R] | routine done: angelegt (trig_01DZyU2vwW6NLgktdCMyekHs), aber ohne Google-Calendar-Connector; Review durch User
- 2026-11-03T11:46:01+00:00: T [R] -> [R] | User hat die Routine nachtraeglich selbst korrigiert (laut User-Angabe, Connector-Einschraenkung behoben; von mir nicht geprueft). Routine nicht loeschen und nicht neu anlegen.
