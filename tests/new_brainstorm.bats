#!/usr/bin/env bats
# Tests for scripts/new-brainstorm.sh (legacy generator)
# Uses Bats (Bash Automated Testing System). Ensure bats is installed to run these.

setup() {
  TMPDIR=$(mktemp -d)
  cp "$BATS_TEST_DIRNAME/../scripts/new-brainstorm.sh" "$TMPDIR/new-brainstorm.sh"
  chmod +x "$TMPDIR/new-brainstorm.sh"
  cd "$TMPDIR"
}

teardown() {
  cd /
  rm -rf "$TMPDIR"
}

@test "creates brainstorm and prompt files for normal topic" {
  run bash -c 'printf "Test Topic\n" | ./new-brainstorm.sh'
  [ "$status" -eq 0 ]
  [[ "$output" =~ Created: ]]

  # Extract created file paths from output (lines prefixed by two spaces)
  created_files=()
  while IFS= read -r line; do
    case "$line" in
      "  "*) created_files+=("${line##  }") ;;
    esac
  done <<< "$output"

  [ "${#created_files[@]}" -eq 2 ]
  [ -f "${created_files[0]}" ]
  [ -f "${created_files[1]}" ]
}

@test "counter increments across consecutive runs" {
  run bash -c 'printf "First Topic\n" | ./new-brainstorm.sh'
  [ "$status" -eq 0 ]
  run bash -c 'printf "Second Topic\n" | ./new-brainstorm.sh'
  [ "$status" -eq 0 ]

  # Collect brainstorm files and ensure two exist with sequential numbers
  files=(brainstorms/*/BRAIN-*.adoc)
  [ "${#files[@]}" -ge 2 ]

  # Sort filenames to get chronological order (string sort works due to zero-padded counter)
  IFS=$'\n' read -r -d '' -a sorted <(printf "%s\n" "${files[@]}" | sort && printf '\0')
  first_base=$(basename "${sorted[0]}")
  second_base=$(basename "${sorted[1]}")

  # Extract numeric sequence portion (after date-)
  seq1=${first_base#BRAIN-????????-}
  seq1=${seq1%%-*}
  seq2=${second_base#BRAIN-????????-}
  seq2=${seq2%%-*}

  [ "$seq1" -lt "$seq2" ]
}

@test "slug generation normalizes and lowers case" {
  run bash -c 'printf "Hello, World!\n" | ./new-brainstorm.sh'
  [ "$status" -eq 0 ]

  files=(brainstorms/*/BRAIN-*.adoc)
  [ "${#files[@]}" -ge 1 ]
  base=$(basename "${files[0]}")
  [[ "$base" =~ -hello-world\.adoc$ ]]
}

@test "handles topic with only non-alphanumeric characters (edge case)" {
  run bash -c 'printf "!!!\n" | ./new-brainstorm.sh'
  [ "$status" -eq 0 ]

  # There should be a file whose name ends with "-.adoc" (empty slug produces trailing hyphen)
  match_count=0
  for f in brainstorms/*/BRAIN-*.adoc; do
    if [[ "$(basename "$f")" =~ ^BRAIN-[0-9]{8}-[0-9]{3}-.adoc$ ]]; then
      match_count=$((match_count+1))
    fi
  done
  [ "$match_count" -ge 1 ]
}
