#!/usr/bin/env bash
set -e

NAME="$1"
shift

case "$NAME" in
  "main")
    PROJECT_DIR="development/Captain"
    VENV="venv"
    SCRIPT="$PROJECT_DIR/main.py"
    ;;

  "piet")
    PROJECT_DIR="development/piet/Captain"
    VENV="venv"
    SCRIPT="$PROJECT_DIR/main.py"
    ;;

  "noora")
    PROJECT_DIR="development/noora/Captain"
    VENV="venv"
    SCRIPT="$PROJECT_DIR/main.py"
    ;;

  "webinterface")
    PROJECT_DIR="development/webinterface/"
    VENV="venv"
    SCRIPT="$PROJECT_DIR/main.py"
    ;;

  "guidance")
    PROJECT_DIR="development/Guidance"
    VENV="venv"
    SCRIPT="$PROJECT_DIR/main.py"
    ;;


  *)
    echo "Unbekanntes Projekt: $NAME"
    echo "Verfügbare: main, piet, noora, webinterface"
    exit 1
    ;;
esac

PYTHON="$VENV/bin/python3"

exec "$PYTHON" "$SCRIPT" "${@:1}"