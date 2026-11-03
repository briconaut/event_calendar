---
name: event-search
description: Recherchiert neue Termine für die Kalender Weihnachtsmärkte, Feuerwerke oder Events und Feste und legt sie als Event-Dateien (plus Locations/Eventserien) an. Nutzen bei „suche“, „finde Events“, „neue Termine“ oder einer Eventsuche je Kalender, Region oder Zeitraum.
---

# event-search

Definitionen, Regionen, Statusregeln und Herkunftsregeln stehen in `CLAUDE.md` – sie sind der Maßstab
für jede Aufnahmeentscheidung.

## Schritte

1. **Rahmen festlegen.** Kalender, Regionen und Zeitraum aus dem Auftrag; fehlt etwas, gelten alle drei
   Kalender, alle Regionen mit Stufe `all`/`major` und der Horizont aus `config/settings.yaml`
   (Weihnachtsmärkte: kommende Saison). Den Rahmen am Anfang des Berichts nennen.

2. **Pflichtprogramm holen.** Je Kalender:
   `python3 tools/ec.py checklist --calendar <kalender> --from <von> --to <bis>`.
   Das liefert die **Pflichtquellen** (`required_sources` aus `config/settings.yaml`) und die
   **Pflicht-Serien** – alle Serien des Kalenders aus `config/locations/` und `config/series.yaml`
   (ortsunabhängige Wanderevents); bei `feuerwerke` zusätzlich jede Serie mit `has_fireworks: true`
   (`search_for: show`). Jede Serie hat eine Aktion: `vorhanden` (bestätigter Termin im Zeitraum, nicht
   neu recherchieren – Hochstufen ist Aufgabe von `event-verify`), `recherchieren` oder `ausgeschlossen`.

3. **Kandidaten sammeln – alle drei Teile sind Pflicht, keiner ersetzt einen anderen:**

   a. **Pflicht-Serien.** Jede Serie mit `recherchieren` über `homepage`/`sources` der Serie und gezielte
      Websuche. Ortsunabhängige Serien (`location: null`): zuerst den Austragungsort im Zeitraum
      ermitteln; der Termin hängt an dessen Location (ggf. neu anlegen), die Regionsregeln gelten für
      diesen Ort. Austragungsort unzulässig → verwerfen mit Grund.

   b. **Pflichtquellen.** Jede URL aus `required_sources` lesen (WebFetch) und alle Termine im Zeitraum
      als Kandidaten übernehmen. Nicht lesbar (Bot-Prüfung, nur JavaScript, Fehler) → `fallback_url`
      versuchen, dann Websuche mit `site:<domain>`; Status je Quelle: `gelesen`, `teilweise (über Suche)`
      oder `nicht erreichbar`. Termine außerhalb zulässiger Regionen nur zählen, nicht einzeln aufführen.

   c. **Freie Suche** – genau so, als gäbe es a. und b. nicht: WebSearch/WebFetch über Stadtportale,
      Veranstalterseiten und regionale Eventkalender, **mindestens eine eigene Suchanfrage je Kalender und
      zulässiger Region**, weiter, bis die offensichtlichen Quellen erschöpft sind. Für Feuerwerke gezielt
      nach Shows in Festprogrammen suchen (Abschlussfeuerwerk, Drohnenshow, Lasershow, Illumination,
      Silvester). Ein ergiebiger Teil a. oder b. ist kein Grund, Teil c. zu kürzen.

4. **Jeden Kandidaten entscheiden:** aufnehmen, aktualisieren (Termin existiert schon) oder verwerfen,
   mit Grund (Kategorie passt nicht, Region ausgeschlossen, kein Großevent, zu klein, Dublette).

5. **Anlegen.**
   - Location: vorhandene nutzen, sonst `python3 tools/ec.py new-location` mit Region nach der Liste in
     `CLAUDE.md`. Wiederkehrende Events als Serie eintragen (`id`, `name`, `calendar`, `category`,
     `major`, `homepage`, `sources`, `typical_period`, `has_fireworks`) – mit wechselndem Austragungsort
     (Hessentag, Gartenschauen) nicht an der Location, sondern in `config/series.yaml` (mit `scope`).
     Serien-IDs sind repo-weit eindeutig.
   - Termin: `python3 tools/ec.py new-event …`, dann alle Felder füllen – `status` nach den Statusregeln,
     `sources` mit den tatsächlich genutzten URLs (Platzhalter `https://TODO` ersetzen), `checked_at` = heute.
   - Hat ein Event eine Show: das Event anlegen und für **jede** Show (je Datum und Ort) einen eigenen
     Termin im Kalender `feuerwerke` mit `parent` = Event-ID und eigener Uhrzeit; an der Serie des Events
     `has_fireworks: true` setzen, damit die Show künftig Pflicht-Serie der Feuerwerkssuche ist.

6. **Validieren und abschließen** gemäß Arbeitsablauf in `CLAUDE.md` (validate → Push auf `main` → `calendar-sync`).

## Bericht

Kann eine Pflichtquelle nicht gelesen werden (`nicht erreichbar`), steht ganz oben eine **Warnung**.
Danach vier Abschnitte:

1. **Pflicht-Serien:** Serie, Location bzw. Austragungsort, Aktion aus der Checkliste, Ergebnis
   (Event-ID, „vorhanden“, „kein Termin gefunden“ oder Grund für „verworfen“).
2. **Pflichtquellen:** URL, Status (`gelesen` / `teilweise (über Suche)` / `nicht erreichbar`), Zahl der
   Kandidaten, Zahl der Termine außerhalb zulässiger Regionen.
3. **Freie Suche:** die tatsächlich gestellten Suchanfragen je Kalender und Region mit der Zahl neuer
   Kandidaten (neu = nicht schon aus 1. oder 2.).
4. **Kandidaten:** Tabelle aller Kandidaten aus Schritt 4 – Titel, Ort, Datum, Herkunft (Serie/Pflichtquelle/
   freie Suche), Entscheidung, Grund bzw. Event-ID.

Fertig ist die Suche erst, wenn jede Pflicht-Serie ein Ergebnis und jede Pflichtquelle einen Status hat,
die freie Suche je Kalender und zulässiger Region mindestens eine Suchanfrage umfasst, jeder Kandidat eine
Entscheidung hat und `ec.py validate` fehlerfrei ist.

## Widersprüchliche Zeiträume

Nennen Quellen unterschiedliche Zeiträume: nur die Schnittmenge als `start`/`end` eintragen und den Widerspruch mit allen Varianten und Quellen in `status_note` vermerken (Regel in `CLAUDE.md`, Abschnitt „Status eines Termins“). Nicht zusammenhängende Schnittmengen dem User melden.
