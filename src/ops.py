#!/usr/bin/env python3
import argparse, json, time, pathlib
import pandas as pd

def ensure_dir(p): pathlib.Path(p).mkdir(parents=True, exist_ok=True)

def write_runlog(run_id, mode, status, notes=""):
    ensure_dir("runs")
    entry = {"run_id": run_id, "mode": mode, "ts": time.strftime("%Y-%m-%d %H:%M:%S"), "status": status, "notes": notes}
    with open("runs/runs.jsonl", "a") as f: f.write(json.dumps(entry) + "\n")

def write_report(run_id, mode, summary_html):
    out_dir = f"reports/{run_id}"
    ensure_dir(out_dir)
    html = f"""<!doctype html><html><head><meta charset="utf-8"><title>Run {run_id}</title></head>
<body>
<h1>Run {run_id} — Mode: {mode}</h1>
{summary_html}
<p><em>This is a stub report to verify the pipeline.</em></p>
</body></html>"""
    with open(f"{out_dir}/report.html", "w") as f: f.write(html)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["lab","act"], required=True)
    ap.add_argument("--in", dest="infile", required=True, help="Path to CSV input")
    ap.add_argument("--run-id", required=True)
    args = ap.parse_args()

    df = pd.read_csv(args.infile)
    rows, cols = df.shape
    summary = f"<p>Loaded <strong>{rows}</strong> rows and <strong>{cols}</strong> columns from <code>{args.infile}</code>.</p>"

    write_report(args.run_id, args.mode, summary)
    write_runlog(args.run_id, args.mode, "PASS", f"rows={rows}, cols={cols}")
    print(f"OK: report at reports/{args.run_id}/report.html")

if __name__ == "__main__":
    main()
