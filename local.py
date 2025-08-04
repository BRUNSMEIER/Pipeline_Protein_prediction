#!/usr/bin/env python3
"""
1_predict_with_protenix.py
———————————————
Calls the Protenix CLI for structure prediction:
    • target.fasta  → reference.pdb
    • input_pdbs/*  → predicted_structures/<basename>_pred.pdb
"""

import os
import sys
import glob
import shutil
import subprocess
from pathlib import Path
import gemmi  # pip install gemmi


# === Path configuration ===
PROTENIX = r"C:\Users\schon\anaconda3\envs\PHAS0017\Scripts\protenix.exe"
INPUT_DIR     = "input_pdbs"
PRED_DIR      = "predicted_structures"
TARGET_FASTA  = "7.6.2.14.json"
REFERENCE_PDB = "7.6.2.14.pdb"


def run_protenix_prediction(input_path: str, out_dir: str, model: str = None, seeds: str = "101", use_msa: bool = True) -> None:
    """Wrapper for calling Protenix CLI"""
    cmd = [
        PROTENIX, "predict",
        "--input", input_path,
        "--out_dir", out_dir,
        "--seeds", seeds
    ]
    if model:
        cmd += ["--model_name", model]
    if use_msa:
        cmd += ["--use_msa_server"]
    else:
        cmd += ["--use_msa_server", "false"]

    print(f"▶ {' '.join(cmd)}", flush=True)
    subprocess.run(cmd, check=True)


def convert_first_cif_to_pdb(cif_dir: str, output_pdb: str) -> None:
    """
    Search for the first .cif file in a directory and convert it to .pdb
    """
    cif_files = sorted(glob.glob(str(Path(cif_dir) / "**/*.cif"), recursive=True))
    if not cif_files:
        raise RuntimeError(f"[{cif_dir}] No .cif files found")
    cif_path = cif_files[0]

    st = gemmi.read_structure(cif_path)
    st.write_pdb(output_pdb)
    print(f"✓ Converted to → {output_pdb}", flush=True)


def predict_to_single_pdb(src: str, dst_pdb: str) -> None:
    """
    Run Protenix CLI, and convert the first CIF output to the desired PDB file
    """
    base   = Path(src).stem  # Get file name without extension
    tmpdir = Path(PRED_DIR) / f"tmp_{base}"
    tmpdir.mkdir(parents=True, exist_ok=True)

    run_protenix_prediction(src, str(tmpdir))
    convert_first_cif_to_pdb(str(tmpdir), dst_pdb)

    shutil.rmtree(tmpdir)
    print(f"✓ Saved → {dst_pdb}", flush=True)


def main() -> None:
    os.makedirs(PRED_DIR, exist_ok=True)

    # 1) Predict reference structure (json → reference.pdb)
    predict_to_single_pdb(TARGET_FASTA, REFERENCE_PDB)

    # # 2) Batch predict input_pdbs/*.pdb
    # for fname in sorted(os.listdir(INPUT_DIR)):
    #     if fname.lower().endswith(".pdb"):
    #         src = os.path.join(INPUT_DIR, fname)
    #         dst = os.path.join(PRED_DIR, f"{Path(fname).stem}_pred.pdb")
    #         predict_to_single_pdb(src, dst)


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)
    except Exception as exc:
        print("ERROR:", exc, file=sys.stderr, flush=True)
        sys.exit(1)
