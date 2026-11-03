# 4-003-8b0d95-Routine_Rollover

## Meta

- ID: 8b0d95
- Type: 4
- Number: 003
- Status: X
- Phase: 004-Routinen
- review: user
- assignee-type: agent
- source: doc/spec.md#Arbeitsweise

## Routine Rollover

> Jährlicher Lauf von `series-rollover`.

## History

- 2026-10-13T11:24:31+00:00: M | Object created
- 2026-11-03T11:54:14+00:00: M [ ] -> [~] | starting
- 2026-11-03T11:54:40+00:00: T [~] -> [~] | Routine 'Rollover Folgejahr' angelegt (User-Freigabe): trig_012GUUtrGN6vZ9adsXhxzaqB, Cron 'CRON_TZ=Europe/Berlin 23 5 28 12 *' (28.12. jeden Jahres 05:23 Berlin), frische Session, Prompt rollover-next-year (Skill series-rollover), validate, Push auf main, calendar-sync automatisch mit Loeschen (Vorgaben wie bei den anderen Routinen). Push-Benachrichtigung an. Naechster Lauf 2026-12-28 05:23 Berlin. Ohne Google-Calendar-Connector angelegt; User setzt den Connector manuell, von mir nicht geprueft.
- 2026-11-03T11:54:40+00:00: M [~] -> [R] | routine done: angelegt (trig_012GUUtrGN6vZ9adsXhxzaqB), Connector durch User manuell; Review durch User
- 2026-11-03T11:56:37+00:00: M [R] -> [X] |
  > USER-APPROVED: Ja, 8b0d95 abnehmen, PR erstellen und mergen
  > Review durch User: Ergebnis akzeptiert
