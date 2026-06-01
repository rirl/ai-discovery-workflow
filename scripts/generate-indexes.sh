#!/usr/bin/env bash
set -e
for d in concepts projects synthesis; do
  echo "= ${d^} Index" > "$d/index.adoc"
done
