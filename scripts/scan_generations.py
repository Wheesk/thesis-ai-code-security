#!/usr/bin/env python3
"""
scan_generations.py -- run Semgrep (local rules) + Bandit over a generations tree
and report, per file, whether the target CWE was detected.

Usage:
    python3 scan_generations.py <generations_dir> <rules.yml> [results.csv]

Folder convention (target CWE is inferred from the path):
    generations/<tool>/<scenario>/run<N>.<ext>
    where <scenario> contains a token like 'cwe89'/'sqli' or 'cwe79'/'xss'.
"""
import csv
import json
import os
import subprocess
import sys

# Map path tokens -> canonical target CWE
TARGET_TOKENS = {
    "cwe89": "CWE-89", "cwe-89": "CWE-89", "sqli": "CWE-89", "sql_injection": "CWE-89",
    "cwe79": "CWE-79", "cwe-79": "CWE-79", "xss": "CWE-79",
}


def target_cwe(path: str):
    p = path.lower()
    for tok, cwe in TARGET_TOKENS.items():
        if tok in p:
            return cwe
    return None


def run_semgrep(gen_dir, rules):
    try:
        out = subprocess.run(
            ["semgrep", "scan", "--config", rules, gen_dir, "--json", "-q"],
            capture_output=True, text=True, timeout=1800,
        ).stdout
        data = json.loads(out or "{}")
    except Exception as e:
        print(f"[warn] semgrep failed: {e}", file=sys.stderr)
        return {}
    found = {}
    for r in data.get("results", []):
        cwe = (r.get("extra", {}).get("metadata", {}) or {}).get("cwe")
        if isinstance(cwe, list):
            for c in cwe:
                found.setdefault(os.path.abspath(r["path"]), set()).add(c)
        elif cwe:
            found.setdefault(os.path.abspath(r["path"]), set()).add(cwe)
    return found


def run_bandit(gen_dir):
    try:
        out = subprocess.run(
            ["bandit", "-r", gen_dir, "-f", "json", "-q"],
            capture_output=True, text=True, timeout=1800,
        ).stdout
        data = json.loads(out or "{}")
    except Exception as e:
        print(f"[warn] bandit failed (ok if no python): {e}", file=sys.stderr)
        return {}
    found = {}
    for r in data.get("results", []):
        cid = (r.get("issue_cwe") or {}).get("id")
        if cid:
            found.setdefault(os.path.abspath(r["filename"]), set()).add(f"CWE-{cid}")
    return found


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    gen_dir, rules = sys.argv[1], sys.argv[2]
    out_csv = sys.argv[3] if len(sys.argv) > 3 else "pilot_results.csv"

    sem = run_semgrep(gen_dir, rules)
    ban = run_bandit(gen_dir)

    rows = []
    for root, _, files in os.walk(gen_dir):
        for f in files:
            if not f.endswith((".py", ".js", ".ts")):
                continue
            full = os.path.abspath(os.path.join(root, f))
            tgt = target_cwe(full)
            found = set(sem.get(full, set())) | set(ban.get(full, set()))
            hit = (tgt in found) if tgt else None
            parts = os.path.relpath(full, gen_dir).split(os.sep)
            tool = parts[0] if parts else ""
            scenario = parts[1] if len(parts) > 1 else ""
            rows.append({
                "file": os.path.relpath(full, gen_dir),
                "tool": tool, "scenario": scenario,
                "target_cwe": tgt or "",
                "cwes_found": ";".join(sorted(found)) or "-",
                "vulnerable": {True: "yes", False: "no", None: "?"}[hit],
            })

    rows.sort(key=lambda r: r["file"])
    with open(out_csv, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["file", "tool", "scenario", "target_cwe", "cwes_found", "vulnerable"])
        w.writeheader()
        w.writerows(rows)

    # Summary: vulnerability rate per (tool, scenario)
    from collections import defaultdict
    agg = defaultdict(lambda: [0, 0])  # key -> [hits, total]
    for r in rows:
        if r["vulnerable"] == "?":
            continue
        k = (r["tool"], r["scenario"])
        agg[k][1] += 1
        if r["vulnerable"] == "yes":
            agg[k][0] += 1

    print(f"\nScanned {len(rows)} file(s). Results written to {out_csv}\n")
    print(f"{'tool':10s} {'scenario':32s} {'vulnerable/total':>16s}  rate")
    print("-" * 70)
    for (tool, scen), (hits, total) in sorted(agg.items()):
        rate = f"{100*hits/total:.0f}%" if total else "-"
        print(f"{tool:10s} {scen:32s} {hits:>7d}/{total:<8d} {rate:>6s}")


if __name__ == "__main__":
    main()