# investigate — CLI documentation
Version: 1.0.0
Last updated: 2026-06-02
## NAME
investigate — command-line interface for the Investigative Workflow toolkit
## SYNOPSIS
investigate [global options] <command> [command options] [arguments...]

## DESCRIPTION
`investigate` is a CLI that helps automate investigative workflows: project initialization, running analyses, exporting results, and managing configurations. This document describes available commands, flags, examples, and integration tips (man pages, shell completion, automated docs).

## INSTALLATION
- From prebuilt binary (Linux x64):
  - Download and place in your PATH: `tar -xzf investigate-linux-amd64.tar.gz && sudo mv investigate /usr/local/bin`
- From source:
  - Build with the repository's build tooling (e.g., `make build`).

## GLOBAL OPTIONS
- `-h`, `--help`         Show help and exit
- `-v`, `--verbose`      Increase output verbosity (repeatable)
- `--version`            Print version and exit
- `-c <file>`, `--config <file>`  Use configuration file (default: `~/.investigate/config.yaml`)
- `--dry-run`            Show actions without executing them
- `--json`               Output machine-readable JSON where applicable
## COMMANDS
- `init` — Initialize a new investigative project
  - Usage: `investigate init [options] <project-path>`
  - Options:
    - `--template <name>`  Use a named template (default: `default`)
    - `--force`            Overwrite existing files without prompting
  - Example: `investigate init ./my-case --template forensic`

- `run` — Execute a named workflow or analysis
  - Usage: `investigate run <workflow> [--input <file>] [--output <dir>] [options]`
  - Options:
    - `-i, --input <file>`   Input file or dataset
    - `-o, --output <dir>`   Output directory (default: `./output`)
    - `--steps <list>`       Comma-separated list of steps to run
    - `--parallel N`         Run up to N tasks in parallel
    - `--timeout DURATION`   Stop after duration (e.g., `30s`, `10m`)
  - Example: `investigate run triage --input evidence.zip --output ./results --parallel 4`

- `status` — Show status of running or last-run tasks
  - Usage: `investigate status [--last] [--json]`
  - Options:
    - `--last`  Show most recent run summary
  - Example: `investigate status --json`

- `list` — List available workflows, templates, or datasets
  - Usage: `investigate list [workflows|templates|datasets] [options]`
  - Example: `investigate list workflows`

- `export` — Export results in various formats
  - Usage: `investigate export <run-id> --format <format> [--output <file>]`
  - Supported formats: `json`, `csv`, `html`, `pdf`
  - Example: `investigate export 20260602-001 --format html --output report.html`

- `config` — Manage configuration
  - Usage: `investigate config get|set|edit [key] [value]`
  - Examples:
    - `investigate config get api.token`
    - `investigate config set api.timeout 30s`
    - `investigate config edit`

- `completion` — Generate shell completion script
  - Usage: `investigate completion [bash|zsh|fish]`
  - Example: `investigate completion bash > /etc/bash_completion.d/investigate`

- `help` — Show help for command
  - Usage: `investigate help <command>`

## EXIT CODES
- `0` — Success
- `1` — General error (invalid usage, unknown command)
- `2` — Configuration error (missing/invalid config)
- `3` — Input error (invalid input file, missing required argument)
- `4` — Runtime error (unhandled exception, external tool failure)
- `125` — Command was explicitly skipped/ignored (reserved for wrappers)
- `130` — Script terminated by Control-C (SIGINT)

## OUTPUT FORMATS
- Default human-readable text with optional verbosity levels.
- `--json` for structured output suitable for automation or CI.
- `--output` for file-based exports; formats: json/csv/html/pdf.

## CONFIGURATION FILE (example YAML)
```
# ~/.investigate/config.yaml
api:
  token: "changeme"
  timeout: "30s"

storage:
  path: "~/investigate-data"

defaults:
  output: "./output"
  parallel: 2
```

## EXAMPLES
- Initialize a project and run a workflow, exporting results as HTML:
```
investigate init ./case-123 --template forensic
investigate run triage --input ./case-123/evidence.s1 --output ./case-123/results
investigate export 20260602-001 --format html --output ./case-123/report.html
```

- Dry-run a workflow to preview steps:
```
investigate run triage --input evidence.zip --dry-run --steps ingest,hash,report
```

- Get verbose logs and JSON output for CI:
```
investigate run pipeline --input data.tar --verbose --json > run-output.json
```

## DEBUGGING & LOGS
- Use `--verbose` multiple times for more detailed logs (e.g., `-vv`).
- Logs are written to: `~/.investigate/logs` by default (configurable).
- For crash reports, include the last 100 lines of the log and the run-id when filing issues.

## MAN PAGE & AUTO-GENERATION
- The CLI supports `--help` and `completion`.
- Recommended to generate docs automatically from CLI metadata (e.g., cobra/argparse/click helpers) to output Markdown or man pages.
- Example (if using cobra in Go): `cobra doc --dir ./docs && cobra man --dir ./man`

## CONTRIBUTING & EXTENDING
- Follow repository CONTRIBUTING.md for code style and branching.
- To add a new command:
 1. Add command handler and unit tests.
 2. Add help text and example usages.
 3. Update completion and docs generation step.

## TROUBLESHOOTING
- Problem: "command not found" — Ensure `investigate` binary is in PATH.
- Problem: Permission denied exporting files — check output directory permissions.
- Problem: Config not loaded — verify `--config` path and file permissions.
- For unresolved issues, capture `investigate --version`, the command run, and logs, and open an issue.

---

If you want additional formats, I can also generate a man page (roff), shell completion scripts, or split this into per-command docs.