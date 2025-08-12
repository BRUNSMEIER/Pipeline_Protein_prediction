#!/usr/bin/env python3
"""
Integrated SUPERFAMILY and DALI Pipeline
First perform SUPERFAMILY prediction on target.fasta (known FASTA in base_dir).
If no significant results, run DALI comparisons on reference.pdb and other PDBs in input_pdbs.
"""

from pathlib import Path
import subprocess
import csv
import os
import argparse
import glob
import time
import sys
from Bio import SearchIO

class DaliPipeline:
    def __init__(self):
        self.base_dir = Path(os.getcwd())
        self.pdb_dir = self.base_dir / "input_pdbs"
        self.dat1_dir = self.base_dir / "imported_DAT/input"
        self.dat2_dir = self.base_dir / "imported_DAT/refx"
        self.outputs_dir = self.base_dir / "dali_outputs"
        self.zscore_csv = self.base_dir / "zscore_summary.csv"
        
        self.ref_pdb = "refx.pdb"  # Updated to match user's reference.pdb
        self.ref_base = "refx"
        self.ref_chain = "refxA"  # Assume A chain for reference
        
        self.dali_pl = Path("/home/wenhao/6tx0/software/dali/DaliLite.v5/bin/dali.pl")
        self.import_pl = Path("/home/wenhao/6tx0/software/dali/DaliLite.v5/bin/import.pl")
    
    def check_prerequisites(self):
        """Check required files and directories"""
        print("🔍 Checking environment...")
        
        # Check DALI binaries
        if not self.dali_pl.exists():
            print(f"❌ DALI binary not found: {self.dali_pl}")
            return False
        
        if not self.import_pl.exists():
            print(f"❌ Import binary not found: {self.import_pl}")
            return False
        
        # Check directories
        required_dirs = [self.pdb_dir, self.dat1_dir, self.dat2_dir, self.outputs_dir]
        for d in required_dirs:
            d.mkdir(parents=True, exist_ok=True)
            if not d.exists():
                print(f"❌ Cannot create directory: {d}")
                return False
        
        # Check reference PDB
        ref_path = self.pdb_dir / self.ref_pdb
        if not ref_path.exists():
            print(f"❌ Reference PDB not found: {ref_path}")
            return False
        
        # Check input PDBs
        pdb_files = list(self.pdb_dir.glob("*.pdb"))
        if not pdb_files:
            print(f"❌ No input PDB files found in {self.pdb_dir}")
            return False
        
        print(f"✅ Environment check passed. Found {len(pdb_files)} PDB files")
        return True
    
    def run_import(self, pdb_file: Path, pdb_base: str, dat_dir: Path):
        """Import single PDB to DAT - imports all chains"""
        cmd = [
            str(self.import_pl),
            "--pdbfile", str(pdb_file),
            "--pdbid", pdb_base,
            "--dat", str(dat_dir),
            "--clean"
        ]
        
        print(f"> Importing {pdb_base}: {' '.join(cmd)}")
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        print(">>> STDOUT:\n", proc.stdout or "(empty)")
        print(">>> STDERR:\n", proc.stderr or "(empty)")
        
        if proc.returncode != 0:
            print(f"❌ Import failed for {pdb_base}")
            return False
        
        # Check generated DAT files (multiple chains)
        generated_dats = list(dat_dir.glob(f"{pdb_base}*.dat"))
        if not generated_dats:
            print(f"❌ No DAT files generated for {pdb_base}")
            return False
        
        print(f"✅ Imported {pdb_base}, generated {len(generated_dats)} chain DAT files: {[d.name for d in generated_dats]}")
        return True
    
    def import_all_pdbs(self):
        """Import all PDBs to DAT"""
        print("🔄 Starting PDB to DAT import...")
        
        # Import reference (only A chain expected, but import all)
        ref_path = self.pdb_dir / self.ref_pdb
        if not self.run_import(ref_path, self.ref_base.upper(), self.dat2_dir):
            return False
        
        # Import query PDBs
        pdb_files = list(self.pdb_dir.glob("*.pdb"))
        successful_imports = 0
        
        for pdb_file in pdb_files:
            if pdb_file.name == self.ref_pdb:
                continue  # Skip reference
            
            # For naming like 3wdl_B.pdb, use pdb_base = "3WDL"
            stem = pdb_file.stem.upper()
            pdb_base = stem.split('_')[0] if '_' in stem else stem
            
            if self.run_import(pdb_file, pdb_base, self.dat1_dir):
                successful_imports += 1
        
        print(f"✅ Imported {successful_imports}/{len(pdb_files)-1} query structures")
        return successful_imports > 0
    
    def run_dali_comparison(self, chain_id: str) -> bool:
        """Run DALI pairwise comparison for single chain"""
        out_txt = self.outputs_dir / f"{chain_id}_vs_{self.ref_chain}.txt"
        
        args = [
            str(self.dali_pl),
            "--cd1", chain_id,
            "--cd2", self.ref_chain,
            "--dat1", str(self.dat1_dir),
            "--dat2", str(self.dat2_dir),
            "--outfmt", "summary",
            "--clean"
        ]
        
        print(f"> Comparing {chain_id} vs {self.ref_chain}: {' '.join(args)}")
        proc = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        print("=== STDOUT ===")
        print(proc.stdout or "(empty)")
        print("=== STDERR ===")
        print(proc.stderr or "(empty)")
        
        # Check fort.*
        fort_files = list(Path('.').glob('fort.*'))
        print(f"→ fort.* files: {fort_files}")
        
        # Check if output file was generated by DALI (since output is redirected to file)
        dali_generated_txt = Path(f"{chain_id}.txt")
        if dali_generated_txt.exists():
            try:
                os.rename(dali_generated_txt, out_txt)
                print(f"✅ Saved result to {out_txt}")
                return True
            except Exception as e:
                print(f"⚠️ Failed to move output file: {e}")
                return False
        elif proc.stdout:
            out_txt.write_text(proc.stdout)
            print(f"✅ Saved result to {out_txt}")
            return True
        else:
            print(f"⚠️ No output for {chain_id}")
            return False
    
    def run_all_comparisons(self):
        """Run all DALI comparisons for all chains"""
        print("🔍 Starting DALI comparisons...")
        
        dat_files = list(self.dat1_dir.glob("*.dat"))
        if not dat_files:
            print("❌ No DAT files in input directory")
            return False
        
        for dat_file in dat_files:
            chain_id = dat_file.stem  # e.g., "3WDLB" for B chain
            self.run_dali_comparison(chain_id)
        
        return True
    
    def extract_zscores(self):
        """Extract Z-scores from output files, skip empty or invalid TXT"""
        print("📊 Extracting Z-scores...")
        
        results = []
        txt_files = list(self.outputs_dir.glob("*_vs_refxA.txt"))
        
        if not txt_files:
            print("❌ No TXT files found in dali_outputs matching *_vs_referenceA.txt")
            return False
        
        for txt_file in txt_files:
            chain_id = txt_file.stem.split('_vs_referenceA')[0].lower()
            pdb_id = chain_id[:-1] if len(chain_id) > 4 else chain_id
            chain = chain_id[-1].upper() if len(chain_id) > 4 else "A"
            
            z = self._extract_zscore(txt_file)
            if z != "NA":
                results.append((f"{pdb_id}_{chain}", z))
                print(f"✅ Extracted Z-score {z} for {chain_id}")
            else:
                print(f"⚠️ Skipped {txt_file.name}: No Z-score found or empty file")
        
        if not results:
            print("❌ No valid Z-scores found")
            return False
        
        with self.zscore_csv.open("w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["chain_id", "zscore"])
            writer.writerows(results)
        
        print(f"✅ Extracted {len(results)} Z-scores, saved to {self.zscore_csv}")
        return True
    
    def _extract_zscore(self, txt_file: Path):
        """Extract Z-score from single TXT file"""
        try:
            with txt_file.open() as f:
                content = f.read().strip()
                if not content:
                    return "NA"  # Empty file
                
                lines = content.splitlines()
                for line in lines:
                    stripped = line.strip().lower()
                    if stripped.startswith("1:"):
                        parts = line.split()
                        if len(parts) > 2:
                            try:
                                return float(parts[2])
                            except ValueError:
                                pass
        except Exception as e:
            print(f"⚠️ Error reading {txt_file}: {e}")
        return "NA"
    
    def debug_view_dat_files(self):
        """Debug: View DAT files content summary"""
        print("🔍 Viewing DAT files...")
        
        for dat_dir in [self.dat1_dir, self.dat2_dir]:
            print(f"📂 {dat_dir}")
            for dat_file in dat_dir.glob("*.dat"):
                print(f"  - {dat_file.name}")
                with dat_file.open() as f:
                    lines = f.readlines()
                    print(f"    Lines: {len(lines)}")
                    print(f"    First line: {lines[0].strip() if lines else 'Empty'}")
                    if "-ca" in ''.join(lines):
                        print("    Contains -ca: Yes")
                    else:
                        print("    Contains -ca: No")
        
    def run_pipeline(self):
        """Run complete DALI pipeline"""
        print("🚀 Starting DALI pipeline...")
        print("="*50)
        
        try:
            if not self.check_prerequisites():
                return False
            
            # Step 1: Import PDBs
            if not self.import_all_pdbs():
                return False
            
            # Step 2: Run comparisons
            self.run_all_comparisons()
            
            # Step 3: Extract Z-scores
            if not self.extract_zscores():
                return False
            
            print("="*50)
            print("🎉 Pipeline completed!")
            return True
            
        except Exception as e:
            print(f"❌ Pipeline failed: {str(e)}")
            return False

def predict_superfamily(input_fasta):
    import os, shutil, subprocess

    superfamily_dir = '/mnt/data2/supfam/supfam/'
    superfamily_script = os.path.join(superfamily_dir, 'superfamily.pl')
    fangshun_dir = '/mnt/data2/supfam/fangshun/'
    results_dir = os.path.join(fangshun_dir, 'supfamresults/')
    os.makedirs(results_dir, exist_ok=True)

    base_name = Path(input_fasta).stem
    target_fasta = os.path.join(superfamily_dir, f"{base_name}.fa")

    shutil.copy2(input_fasta, target_fasta)

    print(f"\n✅ Running SUPERFAMILY on: {target_fasta}")
    try:
        subprocess.run(
            ['perl', superfamily_script, f"{base_name}.fa"],
            cwd=superfamily_dir,
            check=True
        )

        raw_ass = os.path.join(superfamily_dir, '.ass')
        raw_html = os.path.join(superfamily_dir, '.html')
        out_ass = os.path.join(superfamily_dir, f"{base_name}.ass")
        out_html = os.path.join(superfamily_dir, f"{base_name}.html")
        dest_ass = os.path.join(results_dir, f"{base_name}.ass")
        dest_html = os.path.join(results_dir, f"{base_name}.html")

        if os.path.exists(raw_ass):
            shutil.move(raw_ass, out_ass)
            shutil.copy2(out_ass, dest_ass)
        if os.path.exists(raw_html):
            shutil.move(raw_html, out_html)
            shutil.copy2(out_html, dest_html)

        print(f"✅ Output saved as: {out_ass}, {out_html}")
        print(f"📁 Copied to results folder: {dest_ass}, {dest_html}")
        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Error running SUPERFAMILY: {e}")
    except FileNotFoundError:
        print("❌ superfamily.pl not found or not executable.")
    return False


def main():
    parser = argparse.ArgumentParser(description='Integrated SUPERFAMILY and DALI Pipeline')
    parser.add_argument('--check', action='store_true', help='Only check environment')
    parser.add_argument('--debug-dat', action='store_true', help='Debug DAT files')
    parser.add_argument('--skip-import', action='store_true', help='Skip PDB import step')
    
    args = parser.parse_args()
    
    pipeline = DaliPipeline()
    
    if args.check:
        pipeline.check_prerequisites()
        return
    
    if args.debug_dat:
        pipeline.debug_view_dat_files()
        return
    
    # Known FASTA path
    ref_fasta_path = pipeline.base_dir / "target.fasta"
    if not ref_fasta_path.exists():
        print(f"❌ Known FASTA not found: {ref_fasta_path}. Falling back to DALI.")
        if args.skip_import:
            print("⏭️ Skipping import step")
            success = pipeline.run_all_comparisons() and pipeline.extract_zscores()
        else:
            success = pipeline.run_pipeline()
        sys.exit(0 if success else 1)
    
    # Run SUPERFAMILY prediction on known FASTA
    supfam_output_tbl = 'supfam_output.tbl'
    has_results = predict_superfamily(str(ref_fasta_path))
    
    supfam_results_dir = Path("/mnt/data2/supfam/fangshun/supfamresults/")
    base_name = Path(ref_fasta_path).stem  # "target.fasta" -> "target"
    supfam_html = supfam_results_dir / f"{base_name}.html"

    if supfam_html.exists():
        print(f"📝 Found SUPERFAMILY HTML: {supfam_html}. Skipping DALI.")
        sys.exit(0)
    else:
        print(f"❌ SUPERFAMILY HTML not found: {supfam_html}. Proceeding to DALI.")
        if args.skip_import:
            print("⏭️ Skipping import step")
            success = pipeline.run_all_comparisons() and pipeline.extract_zscores()
        else:
            success = pipeline.run_pipeline()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()