# SOP — OpsCore Automator

## Purpose
Run a small, reproducible workflow that validates inputs, produces an HTML Run Report with linked artifacts, and logs each run for traceability.

## Scope
Two adapter modes share ~90% of the code:
- Lab: `well,value` assay CSV → QC + 96-well heatmap → PASS/FAIL report.
- Actuarial: `accident_year,dev,paid` CSV → triangle + LDFs + simple CDFs → PASS/FAIL report.

## Prerequisites
- Python 3.x
- Project venv and dependencies installed (`pip install -r requirements.txt`)
- Sample data in `data_samples/`

## How to Run (Local)
1. Activate environment  
   `source .venv/bin/activate`
2. Run **Lab** mode  
   `python src/ops.py --mode lab --in data_samples/lab/assay_raw.csv`
3. Run **Actuarial** mode  
   `python src/ops.py --mode act --in data_samples/act/claims.csv`
4. Open the generated report  
   `reports/<RUN_ID>/report.html` (linked artifacts included)

## Inputs
- **Lab:** CSV with columns  
  - `well` (A1..H12, regex `^[A-H](?:[1-9]|1[0-2])$`)  
  - `value` (float ≥ 0, finite)
- **Actuarial:** CSV with columns  
  - `accident_year` (int ≥ 1900)  
  - `dev` (int in {12,24,36,48,60,72,84,96})  
  - `paid` (float ≥ 0, cumulative)

## Validation & Controls
- **Schema validation (pandera):** fail-fast; writes `validation_report.json` in each run folder.
- **Audit trail:** appends one JSONL line per run to `runs/runs.jsonl` with run_id, mode, timestamp, status.
- **Deterministic outputs:** each run writes to a unique `reports/<RUN_ID>/` directory.

## PASS / FAIL Criteria
- **PASS:** schema checks succeed; report includes visuals (heatmap or triangle/LDFs/CDFs) and artifact links.
- **FAIL:** schema violation or missing/invalid fields; report shows red FAIL banner + link to `validation_report.json`. No downstream artifacts are trusted.

## Rollback / Rerun
- To undo a run’s outputs, delete the corresponding `reports/<RUN_ID>/` directory.
- The audit log is append-only; add a note in your commit or README if you need to explain a rollback.

## Folder Conventions
- `data_samples/` — example inputs (safe to share)
- `reports/<RUN_ID>/` — HTML report + artifacts per run
- `runs/runs.jsonl` — append-only audit log
- `docs/` — this SOP + Data Dictionary

## Troubleshooting
- “Module not found”: activate venv and reinstall deps (`source .venv/bin/activate; pip install -r requirements.txt`).
- “File not found”: verify the `--in` path and that the CSV has the required columns.
- Blank visual: check for empty/malformed columns in input; see `validation_report.json`.

## Change Log & Ownership
- Owner: Ewetse Chisenga  
- v1.0 (Aug 2025): Initial CLI with validation, reports, audit trail; Lab heatmap + Actuarial triangles/LDFs/CDFs.

## Planned Adapter (Later)
- n8n webhook → save upload → call `python src/ops.py …` → return report link. (Self-hosted n8n exists; adapter to be added when needed.)
