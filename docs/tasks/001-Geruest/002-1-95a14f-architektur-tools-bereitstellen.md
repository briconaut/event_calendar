# 1-002-95a14f-Architektur_Tools_bereitstellen

## Meta

- ID: 95a14f
- Type: 1
- Number: 002
- Status: R
- Phase: 001-Geruest
- review: user
- assignee-type: agent
- source: docs/spec.md#Tools

## Architektur-Tools bereitstellen

> SessionStart-Hook in `.claude/settings.json` ergänzen: `com-gft-tsbo-source/ai-architecture-tools` shallow auf Commit `f25ae40a696037be4b9b6507c14cb08abbb73256` klonen (idempotent, nur wenn noch nicht vorhanden) und `specctl`/`taskctl` aufrufbar machen. Prüfen, dass das Tool-Repo in Web-Sessions per Git erreichbar ist.

## History

- 2026-10-13T11:24:29+00:00: M | Object created
- 2026-10-13T11:29:40+00:00: M | Description changed
- 2026-10-13T11:45:19+00:00: M [ ] -> [~] | starting
- 2026-10-13T11:45:19+00:00: T [~] -> [~] | Hook .claude/hooks/session-start.sh klont ai-architecture-tools auf f25ae40 nach $HOME/ai-architecture-tools (idempotent, Fehler nur als Warnung); Wrapper tools/specctl und tools/taskctl. Lokal mit frischem Zielverzeichnis getestet. Offen: Erreichbarkeit des Tool-Repos in neuen Web-Sessions ohne manuelles add_repo.
- 2026-10-13T11:45:19+00:00: M [~] -> [R] | Nutzer prüft, ob der Hook in einer neuen Session das Tool-Repo holen kann
