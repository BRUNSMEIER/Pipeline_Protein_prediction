#!/usr/bin/env python3
"""
integrated_predict.py
---------------------
Convert FASTA to JSON if necessary, then run Protenix to predict structure and save as reference.pdb.

Workflow:
1. Check if target_without_msa.json exists.
2. If not, convert target.fasta to target_without_msa.json.
3. Run Protenix on the JSON and store the first generated model as reference.pdb.
   - If no PDB, convert the first CIF to PDB using gemmi.

Usage:
    python integrated_predict.py [--fasta target.fasta] [--json target_without_msa.json] [--out reference.pdb]
"""

import argparse
import json
import subprocess
import glob
import shutil
import sys
from pathlib import Path
import gemmi  # pip install gemmi

# ── configuration ─────────────────────────────────────────────────────────────
PROTENIX = "protenix"  # absolute path if not in $PATH
PRED_DIR = "predicted_structures"
DEFAULT_FASTA = "target.fasta"
DEFAULT_JSON = "target_without_msa.json"
DEFAULT_PDB = "reference1.pdb"

# ── helper: run shell commands ────────────────────────────────────────────────
def run(cmd: str) -> None:
    """Run a shell command; raise CalledProcessError on failure."""
    print(f"▶ {cmd}", flush=True)
    subprocess.run(cmd, shell=True, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

# ── FASTA to JSON conversion ──────────────────────────────────────────────────
def parse_fasta(path: Path):
    """Return a list of (header, sequence) tuples found in a FASTA file."""
    records, header, seq = [], None, []
    with path.open() as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            if line.startswith(">"):
                if header:  # save the previous record
                    records.append((header, "".join(seq)))
                header, seq = line[1:], []
            else:
                seq.append(line)
        if header:
            records.append((header, "".join(seq)))

    if not records:
        raise ValueError("No valid FASTA records found.")
    return records

def build_json(records):
    """Create a Protenix-style JSON object."""
    header, seq = records[0]  # use the first record as the sequence
    count = len(records)  # total number of FASTA records
    name = (header.split() or ["target"])[0]

    return [
        {
            "sequences": [
                {
                    "proteinChain": {
                        "sequence": seq,
                        "count": count
                    }
                }
            ],
            "name": name
        }
    ]

def fasta_to_json(in_path: Path, out_path: Path):
    """Convert FASTA to JSON."""
    data = build_json(parse_fasta(in_path))
    with out_path.open("w") as fp:
        json.dump(data, fp, indent=2)
    print(f"✔ Wrote {out_path} (found {data[0]['sequences'][0]['proteinChain']['count']} FASTA record(s))")

# ── Prediction to PDB ─────────────────────────────────────────────────────────
def predict_to_single_pdb(src: str, dst_pdb: str) -> None:
    """
    Call Protenix on *src* (JSON) and save the first structure in PDB format to *dst_pdb*.
    """
    base = Path(src).stem
    tmpdir = Path(PRED_DIR) / f"tmp_{base}"
    tmpdir.mkdir(parents=True, exist_ok=True)

    # Run inference (replace --use_msa_server with --cycle 0 for offline mode)
    run(f"{PROTENIX} predict --input {src} "
        f"--out_dir {tmpdir} --use_msa_server")

    # Preferred output: PDB
    pdb_files = glob.glob(str(tmpdir / "**" / "*.pdb"), recursive=True)
    if pdb_files:
        first_pdb = pdb_files[0]
    else:
        # Fallback: CIF → convert to PDB
        cif_files = glob.glob(str(tmpdir / "**" / "*.cif"), recursive=True)
        if not cif_files:
            raise RuntimeError(f"No structure produced in {tmpdir}")
        cif_path = cif_files[0]
        first_pdb = tmpdir / "converted.pdb"
        gemmi.read_structure(cif_path).write_pdb(str(first_pdb))

    # Copy to destination
    shutil.copy(first_pdb, dst_pdb)
    print(f"✓ Saved PDB → {dst_pdb}", flush=True)

# ── entry point ───────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Integrated FASTA to PDB prediction via Protenix.")
    parser.add_argument("--fasta", default=DEFAULT_FASTA, help="Input FASTA file (default: target.fasta)")
    parser.add_argument("--json", default=DEFAULT_JSON, help="Target JSON file (default: target_without_msa.json)")
    parser.add_argument("--out", default=DEFAULT_PDB, help="Output PDB file (default: reference.pdb)")
    args = parser.parse_args()

    fasta_path = Path(args.fasta)
    json_path = Path(args.json)
    out_pdb = Path(args.out)

    try:
        Path(PRED_DIR).mkdir(exist_ok=True)

        # Check if JSON exists; if not, convert from FASTA
        if not json_path.is_file():
            if not fasta_path.is_file():
                sys.exit(f"Input FASTA not found: {fasta_path}")
            print(f"JSON not found: {json_path}. Converting from FASTA...")
            fasta_to_json(fasta_path, json_path)

        # Run prediction
        predict_to_single_pdb(str(json_path), str(out_pdb))

    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)
    except Exception as exc:
        print("ERROR:", exc, file=sys.stderr, flush=True)
        sys.exit(1)

if __name__ == "__main__":
    main()