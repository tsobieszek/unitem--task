#!/bin/sh

bulk_run() {
  find . -name '*.py' -type f -print0 | xargs -0t "$@"
  echo '—————————————————————————————————————————————'
}

bulk_run mypy
bulk_run pyflakes

set -x
pytest --cov-report term-missing --cov
