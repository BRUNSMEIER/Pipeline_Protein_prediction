#!/usr/bin/env python3
"""
Convert mmCIF files from input_cifs to chain-specific PDB files in input_pdbs
"""

from pathlib import Path
from Bio.PDB import MMCIFParser, PDBIO, Select
import os

class ChainSelect(Select):
    def __init__(self, chain_id):
        self.chain_id = chain_id

    def accept_chain(self, chain):
        return chain.id == self.chain_id

def convert_cif_to_pdb(cif_path, pdb_path, chain_id):
    parser = MMCIFParser(QUIET=True)
    structure = parser.get_structure(cif_path.stem, cif_path)
    
    io = PDBIO()
    io.set_structure(structure)
    io.save(str(pdb_path), ChainSelect(chain_id))
    print(f"✅ Converted {cif_path.name} chain {chain_id} to {pdb_path.name}")

def main():
    base_dir = Path(os.getcwd())
    cif_dir = base_dir / "input_cifs"
    pdb_dir = base_dir / "input_pdbs"
    pdb_dir.mkdir(parents=True, exist_ok=True)
    
    # Chain mapping based on your screenshot (PDB ID to chain)
    chain_map = {
        "8dcd": "A",
        "7y7p": "A",
        "7tgk": "D",
        "6t0v": "B",
        "6ig2": "D",
        "6ci7": "C",
        "4ff3": "A",
        "3wdl": "B",
        "3gqk": "A",
        "3f2b": "A",
        "3amt": "A",
        "3xan": "A",  # Assuming 3xan.cif -> 3xan_A.pdb; adjust if 2xan
        # Add more if needed
    }
    
    cif_files = list(cif_dir.glob("*.cif"))
    if not cif_files:
        print("❌ No CIF files found in input_cifs")
        return
    
    successful = 0
    for cif_file in cif_files:
        pdb_id = cif_file.stem.lower()
        chain = chain_map.get(pdb_id, "A")  # Default to A if not specified
        
        pdb_filename = f"{pdb_id}_{chain}.pdb"
        pdb_path = pdb_dir / pdb_filename
        
        if pdb_path.exists():
            print(f"⏩ Skipping existing {pdb_filename}")
            successful += 1
            continue
        
        try:
            convert_cif_to_pdb(cif_file, pdb_path, chain)
            successful += 1
        except Exception as e:
            print(f"❌ Failed to convert {cif_file.name}: {e}")
    
    print(f"✅ Converted {successful}/{len(cif_files)} files")

if __name__ == "__main__":
    main()