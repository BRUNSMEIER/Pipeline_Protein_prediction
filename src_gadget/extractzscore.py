#!/usr/bin/env python3
"""
Extract Z-scores from DALI output TXT files and generate CSV
Run this script in the working directory containing dali_outputs/
"""

from pathlib import Path
import csv
import os
import argparse
import sys

class ZScoreExtractor:
    def __init__(self):
        self.base_dir = Path(os.getcwd())
        self.outputs_dir = self.base_dir / "dali_outputs"
        self.zscore_csv = self.base_dir / "zscore_summary.csv"
    
    def extract_zscores(self):
        """Extract Z-scores from output files, skip empty or invalid TXT"""
        print("📊 Extracting Z-scores...")
        
        results = []
        txt_files = list(self.outputs_dir.glob("*.txt"))
        
        if not txt_files:
            print("❌ No TXT files found in dali_outputs")
            return False
        
        for txt_file in txt_files:
            chain_id = txt_file.stem.split('_vs_')[0].lower()
            pdb_id = chain_id[:-1] if len(chain_id) > 4 else chain_id  # Handle chain
            chain = chain_id[-1].upper() if len(chain_id) > 4 else "A"
            
            z = self._extract_zscore(txt_file)
            if z != "NA":
                results.append((f"{pdb_id}_{chain}", z))
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
                content = f.read().strip().lower()
                if not content:
                    return "NA"  # Empty file
                
                if "zscore" in content:
                    lines = content.splitlines()
                    for line in lines:
                        if line.strip().startswith("1:"):
                            parts = line.split()
                            if len(parts) > 2:
                                try:
                                    return float(parts[2])  # Z column
                                except ValueError:
                                    pass
        except Exception as e:
            print(f"⚠️ Error reading {txt_file}: {e}")
        return "NA"

def main():
    parser = argparse.ArgumentParser(description='Extract Z-scores from DALI TXT files')
    parser.add_argument('--output', help='Output CSV path', default='zscore_summary.csv')
    
    args = parser.parse_args()
    
    extractor = ZScoreExtractor()
    extractor.zscore_csv = Path(args.output)
    
    success = extractor.extract_zscores()
    
    if success:
        print("\n🎊 Success!")
        sys.exit(0)
    else:
        print("\n💥 Failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()