#!/usr/bin/env python3
"""
predictcif.py
--------------------
Run Protenix on `7.6.2.14.json` and store the first generated model
as `7.6.2.14.pdb`.
Use command 'conda activate protoneix' to initiate virtual environment
Workflow
--------
1. Launch Protenix and place its output under `predicted_structures/tmp_reference`.
2. Search recursively for the first *.pdb* file.
3. If no PDB exists, take the first *.cif*, convert it to PDB with *gemmi*.
4. Copy the chosen PDB to `reference.pdb`.
"""
import subprocess, glob, shutil, sys
from pathlib import Path
import gemmi                         # pip install gemmi

# ── configuration ─────────────────────────────────────────────────────────────
PROTENIX      = "protenix"           # absolute path if not in $PATH
PRED_DIR      = "predicted_structures"
TARGET_JSON   = "7.6.2.14.json"
REFERENCE_PDB = "7.6.2.14.pdb"

# ── helper: run shell commands ────────────────────────────────────────────────
def run(cmd: str) -> None:
    """Run a shell command; raise CalledProcessError on failure."""
    print(f"▶ {cmd}", flush=True)
    subprocess.run(cmd, shell=True, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

# ── core routine ──────────────────────────────────────────────────────────────
def predict_to_single_pdb(src: str, dst_pdb: str) -> None:
    """
    Call Protenix on *src* (FASTA / JSON / PDB) and save the first structure
    in PDB format to *dst_pdb*.
    """
    base   = Path(src).stem
    tmpdir = Path(PRED_DIR) / f"tmp_{base}"
    tmpdir.mkdir(parents=True, exist_ok=True)

    # 1. run inference (replace --use_msa_server with --cycle 0 for offline mode)
    run(f"{PROTENIX} predict --input {src} "
        f"--out_dir {tmpdir} --use_msa_server")

    # 2. preferred output: PDB
    pdb_files = glob.glob(str(tmpdir / "**" / "*.pdb"), recursive=True)
    if pdb_files:
        first_pdb = pdb_files[0]
    else:
        # 3. fallback: CIF → convert to PDB
        cif_files = glob.glob(str(tmpdir / "**" / "*.cif"), recursive=True)
        if not cif_files:
            raise RuntimeError(f"No structure produced in {tmpdir}")
        cif_path  = cif_files[0]
        first_pdb = tmpdir / "converted.pdb"
        gemmi.read_structure(cif_path).write_pdb(str(first_pdb))

    # 4. copy to destination
    shutil.copy(first_pdb, dst_pdb)
    print(f"✓ saved PDB → {dst_pdb}", flush=True)

# ── entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    try:
        Path(PRED_DIR).mkdir(exist_ok=True)
        predict_to_single_pdb(TARGET_JSON, REFERENCE_PDB)
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)
    except Exception as exc:
        print("ERROR:", exc, file=sys.stderr, flush=True)
        sys.exit(1)
