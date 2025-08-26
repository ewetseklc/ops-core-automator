# Data Dictionary — OpsCore Automator (v1)

This document defines the **inputs**, **validation rules**, and **outputs** for both adapter modes.
CSV files must be UTF-8 encoded with a **header row** and **comma** as the delimiter.

---

## 1) Lab Mode (assay plate)

### Expected Input File
**Path (example):** `data_samples/lab/assay_raw.csv`  
**Primary key:** `well` (each well appears at most once)

| Field | Type | Required | Allowed / Rule | Examples |
|---|---|---:|---|---|
| `well` | string | Yes | Plate coordinate **A1..H12**. Regex: `^[A-H](?:[1-9]|1[0-2])$` (case-insensitive accepted, trimmed) | `A1`, `B12`, `h7` |
| `value` | float | Yes | Finite and **≥ 0** | `0.12`, `1.05`, `0` |

**Notes**
- Duplicate `well` rows are not allowed; keep the latest measurement upstream or aggregate before intake.
- Extra/unrecognized columns are ignored in v1.
- Missing cells are displayed as blanks in the heatmap.

### QC & Validation (pandera)
- **Schema check:** field presence & types
- **Well format:** must match the regex above
- **Value range:** finite, non-negative
- **On failure:** run marked **FAIL**; see `validation_report.json`

### Generated Artifacts (per run folder)
- `report.html` — one-page Run Report with PASS/FAIL banner and heatmap
- `validation_report.json` — machine-readable error details (if any)
- `lab_heatmap.png` — 8×12 grid heatmap (rows A–H, cols 1–12)

---

## 2) Actuarial Mode (claims triangle demo)

### Expected Input File
**Path (example):** `data_samples/act/claims.csv`  
**Primary key:** `(accident_year, dev)` (each pair appears at most once)

| Field | Type | Required | Allowed / Rule | Examples |
|---|---|---:|---|---|
| `accident_year` | int | Yes | **≥ 1900** (practical: recent years) | `2021`, `2022` |
| `dev` | int (months) | Yes | One of `{12,24,36,48,60,72,84,96}` | `12`, `24` |
| `paid` | float | Yes | Finite and **≥ 0** (interpreted as **cumulative paid** at `dev`) | `1200`, `0` |

**Assumptions**
- `paid` is **cumulative** by development age. (Monotonicity is expected but **not enforced** in v1.)
- Data may be sparse; missing cells are allowed and appear as blanks.

### QC & Validation (pandera)
- **Schema check:** field presence & types
- **Domain checks:** `dev` ∈ {12,24,…,96}; `paid` ≥ 0
- **On failure:** run marked **FAIL**; see `validation_report.json`

### Transformations & Outputs
- **Triangle:** pivot to `paid_triangle.csv` with rows = `accident_year`, columns = `dev`
- **Age-to-Age LDFs:** `ldf.csv` from adjacent dev ratios (mean across AY where both devs exist)
- **Simple CDFs:** cumulative product of LDFs from latest age back (displayed in report)

### Generated Artifacts (per run folder)
- `report.html` — PASS/FAIL banner, triangle table, LDF table, simple CDFs, notes
- `validation_report.json` — machine-readable error details (if any)
- `paid_triangle.csv` — triangle matrix export
- `ldf.csv` — age-to-age factors
- `act_triangle_heat.png` — heatmap of triangle values

---

## 3) Run Folders & Audit Log

### Run Folder (created per execution)
`reports/<RUN_ID>/`  
Contains all artifacts listed above for the chosen mode. `<RUN_ID>` auto-generated (e.g., `LAB_20250826_133737`).

### Audit Log
File: `runs/runs.jsonl` (append-only; one JSON object per line)

| Field | Type | Description |
|---|---|---|
| `run_id` | string | Unique run identifier (e.g., `ACT_20250826_133753`) |
| `mode` | string | `"lab"` or `"act"` |
| `ts` | string | Timestamp `YYYY-MM-DD HH:MM:SS` (local) |
| `status` | string | `"PASS"` or `"FAIL"` |
| `notes` | string | Optional summary (e.g., `rows=4, cols=3`) |

---

## 4) File Conventions

- **CSV:** UTF-8, header row, comma delimiter, no quoted headers.
- **Missing values:** empty cells allowed; validation enforces required fields presence but allows sparse triangles.
- **Whitespace/case:** leading/trailing spaces trimmed; `well` case normalized internally.
- **Time-stamped outputs:** every run writes to a new folder to ensure reproducibility.

---

## 5) Glossary (selected)

- **Well:** Physical coordinate on a 96-well plate (rows A–H, columns 1–12).  
- **Triangle:** Matrix of cumulative values by **Accident Year** (rows) and **Development Age (months)** (columns).  
- **LDF (Age-to-Age):** Ratio from dev *k* to dev *k+1* (used for chain-ladder style projections).  
- **CDF:** Cumulative development factor from a given age to ultimate (product of subsequent LDFs).  
- **PASS/FAIL:** Overall run status based on schema/QC checks; failures produce a JSON validation report.

---

## 6) Version & Ownership

- **Owner:** Ewetse Chisenga  
- **Version:** v1.0 (Aug 2025) — initial release with schema validation, artifacts, audit log, and HTML reports for both modes.
