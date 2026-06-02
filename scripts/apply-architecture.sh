#!/usr/bin/env bash
set -e
# Configurable project list: provide as first argument or via PROJECTS env var.
# Example: PROJECTS="ai-discovery mathematical-teleology" ./apply-architecture.sh
PROJECTS="${1:-${PROJECTS:-ai-discovery mathematical-teleology evolution-as-search genomic-teleology}}"

mkdir -p brainstorms concepts projects synthesis docs scripts
# Create project subdirectories under projects/
IFS=' ' read -r -a PROJ_LIST <<< "$PROJECTS"
for p in "${PROJ_LIST[@]}"; do
  mkdir -p "projects/$p"
done

touch concepts/.gitkeep synthesis/.gitkeep
echo "Architecture applied."
