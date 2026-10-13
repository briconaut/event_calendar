#!/bin/bash
# SessionStart-Hook: Python-Pakete installieren und Architektur-Tools (specctl/taskctl)
# auf einem fest gepinnten Commit bereitstellen. Fehler brechen die Session nicht ab.
set -u

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"

# Gepinnter Stand der Architektur-Tools; Update = bewusste Änderung dieses Werts
ARCH_TOOLS_REPO="https://github.com/com-gft-tsbo-source/ai-architecture-tools"
ARCH_TOOLS_COMMIT="f25ae40a696037be4b9b6507c14cb08abbb73256"
ARCH_TOOLS_DIR="${ARCH_TOOLS_DIR:-$HOME/ai-architecture-tools}"

# 1) Python-Abhängigkeiten
pip install --quiet --disable-pip-version-check -r "$PROJECT_DIR/requirements.txt" \
  || pip install --quiet --disable-pip-version-check --break-system-packages -r "$PROJECT_DIR/requirements.txt" \
  || echo "WARNUNG: pip install fehlgeschlagen" >&2

# 2) Architektur-Tools: nur holen, wenn der gepinnte Commit noch nicht ausgecheckt ist
current="$(git -C "$ARCH_TOOLS_DIR" rev-parse HEAD 2>/dev/null || true)"
if [ "$current" != "$ARCH_TOOLS_COMMIT" ]; then
  if [ ! -d "$ARCH_TOOLS_DIR/.git" ]; then
    git init --quiet "$ARCH_TOOLS_DIR" && git -C "$ARCH_TOOLS_DIR" remote add origin "$ARCH_TOOLS_REPO"
  fi
  if git -C "$ARCH_TOOLS_DIR" fetch --quiet --depth 1 origin "$ARCH_TOOLS_COMMIT" \
     && git -C "$ARCH_TOOLS_DIR" checkout --quiet --detach FETCH_HEAD; then
    :
  else
    echo "WARNUNG: Architektur-Tools konnten nicht geholt werden ($ARCH_TOOLS_REPO@$ARCH_TOOLS_COMMIT)." >&2
    echo "         Ist das Repo in dieser Umgebung per Git erreichbar?" >&2
  fi
fi

# 3) Pfad für die Wrapper tools/specctl und tools/taskctl bekanntgeben
if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
  echo "export ARCH_TOOLS_DIR=\"$ARCH_TOOLS_DIR\"" >> "$CLAUDE_ENV_FILE"
fi
exit 0
