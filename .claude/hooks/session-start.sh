#!/bin/bash
# SessionStart-Hook: Python-Abhängigkeiten installieren. Fehler brechen die Session nicht ab.
set -u

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"

pip install --quiet --disable-pip-version-check -r "$PROJECT_DIR/requirements.txt" \
  || pip install --quiet --disable-pip-version-check --break-system-packages -r "$PROJECT_DIR/requirements.txt" \
  || echo "WARNUNG: pip install fehlgeschlagen" >&2
exit 0
