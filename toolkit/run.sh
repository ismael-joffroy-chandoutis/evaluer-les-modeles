#!/usr/bin/env bash
# Banc d'essai d'atelier. Toutes les commandes ci-dessous ont ete executees.
#
#   ./run.sh install                      installe inspect-ai dans .venv
#   ./run.sh un <modele> [tache]          un modele, une tache (defaut : les trois)
#   ./run.sh tous                         les modeles de MODELES sur les trois taches
#   ./run.sh logs                         ouvre le visualiseur de logs
#   ./run.sh table                        recalcule le tableau de resultats
#
# Prerequis : la variable d'environnement OPENROUTER_API_KEY.
# Aucun secret n'est stocke dans ce depot.

set -euo pipefail
ICI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ICI"

VENV="${VENV:-$ICI/.venv}"
PY="$VENV/bin/python"
INSPECT="$VENV/bin/inspect"
LOGS="${LOGS:-$ICI/logs}"

# Modeles evalues. Quatre familles distinctes.
MODELES=(
  "openrouter/anthropic/claude-sonnet-5"
  "openrouter/openai/gpt-5.6-terra"
  "openrouter/google/gemini-3.6-flash"
  "openrouter/mistralai/mistral-medium-3-5"
)

TACHES=("banc/tasks/creation.py" "banc/tasks/admin_juridique.py" "banc/tasks/recherche.py")

verif_cle() {
  if [ -z "${OPENROUTER_API_KEY:-}" ]; then
    echo "OPENROUTER_API_KEY absente. export OPENROUTER_API_KEY=... puis relancer." >&2
    exit 1
  fi
}

cmd_install() {
  command -v uv >/dev/null 2>&1 || { echo "uv requis : https://docs.astral.sh/uv/" >&2; exit 1; }
  uv venv --python 3.12 "$VENV"
  uv pip install --python "$PY" -r requirements.txt
  "$PY" items/_generer_exemples.py
  "$INSPECT" --version
}

# Budget d'erreur serre : sans ces limites on mesure la tolerance du harnais.
# Les desserrer volontairement est une experience, pas un reglage par defaut.
LIMITES=(--message-limit 4 --token-limit 12000 --time-limit 300 --max-connections 8)

cmd_un() {
  verif_cle
  local modele="$1"; shift
  local taches=("$@")
  [ ${#taches[@]} -eq 0 ] && taches=("${TACHES[@]}")
  for t in "${taches[@]}"; do
    echo ">>> $modele | $t"
    "$INSPECT" eval "$t" \
      --model "$modele" \
      -T candidat="$modele" \
      --log-dir "$LOGS" \
      "${LIMITES[@]}"
  done
}

cmd_tous() {
  for m in "${MODELES[@]}"; do cmd_un "$m"; done
  cmd_table
}

cmd_logs() { "$INSPECT" view --log-dir "$LOGS"; }
cmd_table() { "$PY" analyse/table.py "$LOGS"; }

case "${1:-aide}" in
  install) cmd_install ;;
  un) shift; cmd_un "$@" ;;
  tous) cmd_tous ;;
  logs) cmd_logs ;;
  table) cmd_table ;;
  *) sed -n '2,14p' "$0" ;;
esac
