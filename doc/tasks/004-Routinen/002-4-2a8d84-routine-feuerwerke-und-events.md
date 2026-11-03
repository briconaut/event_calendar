# 4-002-2a8d84-Routine_Feuerwerke_und_Events

## Meta

- ID: 2a8d84
- Type: 4
- Number: 002
- Status: R
- Phase: 004-Routinen
- review: user
- assignee-type: agent
- source: doc/spec.md#Arbeitsweise

## Routine Feuerwerke und Events

> Monatliche Suche + Verify.

## History

- 2026-10-13T11:24:31+00:00: M | Object created
- 2026-11-03T11:49:18+00:00: M [ ] -> [~] | starting
- 2026-11-03T11:49:35+00:00: T [~] -> [~] | Routine 'Feuerwerke und Events pruefen' angelegt (User-Freigabe): trig_01PD7o8MHyLRgnDBnMqi8Q9o, Cron 'CRON_TZ=Europe/Berlin 17 5 1 * *' (am 1. jeden Monats 05:17 Berlin), frische Session je Lauf, Prompt: search-feuerwerke + search-events + event-verify, validate, Push auf main, calendar-sync automatisch mit Loeschen (Vorgaben wie bei Routine d241a3 uebernommen). Push-Benachrichtigung an. Naechster Lauf 2026-12-01 05:17 Berlin. Ohne Google-Calendar-Connector angelegt (create_trigger lehnt connectors ab); User korrigiert die Berechtigungen/den Connector manuell, von mir nicht geprueft.
- 2026-11-03T11:49:35+00:00: M [~] -> [R] | routine done: angelegt (trig_01PD7o8MHyLRgnDBnMqi8Q9o), Connector durch User manuell; Review durch User
