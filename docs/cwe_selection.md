# CWE Selection

**Edition:** 2025 MITRE CWE Top 25 Most Dangerous Software Weaknesses. Every tested
CWE is drawn from this list. Selection criteria: (a) on the 2025 Top 25, (b) realistic
to elicit from a normal feature-request prompt in Python or JavaScript web code, and
(c) detectable by the static analysers used (Semgrep taint rules + Bandit).

## Full set (8 CWEs)

| CWE | 2025 rank | Name | Category | Language |
|-----|-----------|------|----------|----------|
| CWE-79  | 1  | Cross-site Scripting        | injection / output encoding | JavaScript |
| CWE-89  | 2  | SQL Injection               | injection                   | Python |
| CWE-22  | 6  | Path Traversal              | data handling               | Python |
| CWE-78  | 9  | OS Command Injection        | injection                   | Python |
| CWE-94  | 10 | Code Injection              | injection                   | Python |
| CWE-434 | 12 | Unrestricted File Upload    | input validation            | Python |
| CWE-502 | 15 | Deserialization of Untrusted Data | data handling         | Python |
| CWE-918 | 22 | Server-Side Request Forgery | input validation            | Python |

## Detection notes
- CWE-94, 502, 918 have clean automated detection.
- CWE-434 (unrestricted upload) is flagged as a WARNING by Semgrep and leans on manual
  verification: the scanner flags any saved upload; a human confirms whether type/extension
  validation was applied.

## Scope note
The 2025 Top 25 has no cleanly testable "credential handling" weakness (hard-coded
credentials, CWE-798, was on the 2024 edition and dropped in 2025). Memory-safety entries
(buffer overflows, use-after-free) and authorization entries are excluded, since they
apply to C/C++ or require multi-endpoint context rather than a single Python/JS function.
