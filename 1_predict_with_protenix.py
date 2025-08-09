#!/usr/bin/env python3
"""
1_predict_with_protenix.py
———————————————
Run this in the Protenix environment to:
    • Predict target.fasta → reference.pdb
    • Predict each file in input_pdbs/ → predicted_structures/<basename>_pred.pdb

CLI-compatible format:
    protenix predict --input <file|dir> --out_dir <dir> …
"""

import os
import sys
import glob
import shutil
import subprocess
from pathlib import Path

# === Basic paths ===
PROTENIX      = "protenix"          # If not in $PATH, provide full absolute path
INPUT_DIR     = "input_pdbs"
PRED_DIR      = "predicted_structures"
TARGET_FASTA  = "7.6.2.14.json"
REFERENCE_PDB = "7.6.2.14.pdb"

def run(cmd: str) -> None:
    """
    Execute a shell command and raise an exception if it fails.
    Useful for SLURM job monitoring or fail-fast behavior.
    """
    print(f"▶ {cmd}", flush=True)
    subprocess.run(cmd, shell=True, check=True)

def predict_to_single_pdb(src: str, dst_pdb: str) -> None:
    """
    Call Protenix to perform structure prediction,
    then move/rename the first predicted PDB file to `dst_pdb`.

    Parameters:
    - src: Input file (either .fasta or .pdb)
    - dst_pdb: Path to save the final renamed output PDB
    """
    base   = Path(src).stem
    tmpdir = Path(PRED_DIR) / f"tmp_{base}"
    tmpdir.mkdir(parents=True, exist_ok=True)

    # If Protenix does not require different flags for input types, you can remove any type logic
    run(f"{PROTENIX} predict --input {src} --out_dir {tmpdir} --use_msa_server")

    # Grab the first generated PDB file (you can customize selection logic here)
    pdb_candidates = sorted(glob.glob(str(tmpdir / "*.pdb")))
    if not pdb_candidates:
        raise RuntimeError(f"[{src}] No PDB file found after prediction. Checked directory: {tmpdir}")

    first_pdb = pdb_candidates[0]
    shutil.move(first_pdb, dst_pdb)
    shutil.rmtree(tmpdir)  # Comment this line if you want to keep the temp directory
    print(f"✓ saved → {dst_pdb}", flush=True)

def main() -> None:
    os.makedirs(PRED_DIR, exist_ok=True)

    # 1) Predict structure from target FASTA → reference.pdb
    predict_to_single_pdb(TARGET_FASTA, REFERENCE_PDB)

    # # 2) Predict structures for each file in input_pdbs/
    # for fname in sorted(os.listdir(INPUT_DIR)):
    #     if not fname.lower().endswith(".pdb"):
    #         continue
    #     src_path = os.path.join(INPUT_DIR, fname)
    #     dst_path = os.path.join(
    #         PRED_DIR, f"{Path(fname).stem}_pred.pdb"
    #     )
    #     predict_to_single_pdb(src_path, dst_path)

if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)
    except Exception as exc:
        print("ERROR:", exc, file=sys.stderr, flush=True)
        sys.exit(1)
