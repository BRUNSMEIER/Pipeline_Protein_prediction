#!/usr/bin/env python3
"""
convert.py
———————————————
• Run after Protenix prediction is completed
• Converts predicted_structures/**.cif → reference.pdb
"""

import glob
import sys
from pathlib import Path
import gemmi  # pip install gemmi

# === Parameters: modify as needed ===
PRED_DIR = "predicted_structures/tmp_target"  # Output directory from Protenix
OUTPUT_PDB = "target.pdb"                     # Name of the output PDB file

def pick_cif(cif_list):
    """
    Choose one mmCIF file from the list.
    You can filter by seed/sample here if needed.
    Currently: pick the first file in the sorted list.
    """
    return cif_list[0] if cif_list else None

def main():
    # Recursively find all .cif files under the prediction directory
    cif_files = glob.glob(str(Path(PRED_DIR) / "**" / "*.cif"), recursive=True)
    if not cif_files:
        print(f"[ERROR] No .cif files found under {PRED_DIR}/ and its subdirectories", file=sys.stderr)
        sys.exit(1)

    # Select a cif file to convert
    cif_path = pick_cif(sorted(cif_files))
    print(f"✔ Selected mmCIF file: {cif_path}")

    # Convert mmCIF to PDB
    st = gemmi.read_structure(cif_path)
    st.write_pdb(OUTPUT_PDB)
    print(f"✓ Successfully wrote {OUTPUT_PDB}")

if __name__ == "__main__":
    main()
