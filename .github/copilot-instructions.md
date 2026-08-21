<!-- .github/copilot-instructions.md -->
# Guidance for AI coding assistants working on this repository

Purpose: help an AI agent become productive quickly by describing the repository layout, key workflows, and project-specific patterns.

Big picture
- **Goal:** empirical experiment comparing code-generation tools (Claude, Copilot, Codex) for CWE vulnerabilities. See `README.md` for project aims.
- **Data flow:** prompts → generated code stored in `generations/<tool>/<scenario>/run<N>.<ext>` → static scanning (`scripts/scan_generations.py`) → results CSV in project root (default `pilot_results.csv`) → analysis in `results/`.

Important files and dirs
- `scripts/scan_generations.py`: central runner that invokes `semgrep` and `bandit`, aggregates findings, and writes a CSV. Usage:
  - `python3 scripts/scan_generations.py <generations_dir> <rules.yml> [results.csv]`
  - Example: `python3 scripts/scan_generations.py generations/ scanners/pilot-cwe.yml pilot_results.csv`
- `scanners/pilot-cwe.yml`: semgrep rules used in the pilot. Rules MUST include a `metadata.cwe` field — the scanner extracts CWE IDs from `extra.metadata.cwe`.
- `generations/`: generated outputs organized by tool and scenario. Conventions used by the scanner:
  - `generations/<tool>/<scenario>/run<N>.<ext>`
  - `scenario` must contain a CWE token (e.g. `cwe89`, `cwe79`, `sqli`, `xss`) so `scan_generations.py` can infer the target CWE.
- `docs/decisions.md`: records methodological choices; useful to understand why directories/rules were chosen.

Project-specific conventions
- File extensions scanned: only `.py`, `.js`, `.ts` are considered by `scan_generations.py`.
- Target detection: `scripts/scan_generations.py` maps path tokens to canonical CWEs using `TARGET_TOKENS`. Add tokens here (and in scenario names) to ensure correct target inference.
- Semgrep rule metadata: rules should set `metadata.cwe` (string or list) — `run_semgrep()` collects these and joins them into `cwes_found` in the CSV.
- Bandit mapping: Python Bandit results are read from `issue_cwe.id` and normalized to `CWE-<id>`.

Running and debugging
- Requirements: `python3`, `semgrep` and `bandit` on PATH. The script runs both tools via subprocess with a 30-minute timeout per tool.
- Common invocation:
  - `python3 scripts/scan_generations.py generations/ scanners/pilot-cwe.yml results/pilot_results.csv`
- Failure modes:
  - If `semgrep` or `bandit` fail, the script prints a warning and continues (empty findings). Look for `[warn] semgrep failed:` or `[warn] bandit failed` messages.

Extending the experiment
- To add a new CWE scenario: create `generations/<tool>/<new-scenario>/run1.<ext>` and include a token in the scenario name that maps to `TARGET_TOKENS` in `scripts/scan_generations.py`.
- To add new semgrep rules: edit `scanners/pilot-cwe.yml` (or add alternative configs) and ensure `metadata.cwe` is present so results are attributed correctly.

Quick examples for edits an AI assistant might make
- Add a new semgrep rule with `metadata.cwe: "CWE-XX"` so it appears in CSV `cwes_found`.
- Update `TARGET_TOKENS` in `scripts/scan_generations.py` if you create scenario directories with new tokens.

Notes and assumptions
- This file documents only discoverable, implemented behavior (scanner aggregation, file layout, semgrep metadata usage). It does not prescribe experimental methodology beyond what the code enforces.

If anything here is unclear or you'd like explicit examples for tests or commits, tell me which section to expand.
