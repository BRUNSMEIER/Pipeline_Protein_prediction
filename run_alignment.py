#!/usr/bin/env python3
import os
import subprocess

# ==== 配置 ====
INPUT_DIR = "input_pdbs"
PREDICTED_DIR = "predicted_structures"
DAT_DIR = "imported_DAT"
REFERENCE_FASTA = "target.fasta"
REFERENCE_PDB = "reference.pdb"
REFERENCE_ID = "refx"  # 必须是4字符，用于 DaliLite
DALI_BIN = "/home/you/DaliLite.v5/bin"

# ==== 初始化 ====
os.makedirs(PREDICTED_DIR, exist_ok=True)
os.makedirs(DAT_DIR, exist_ok=True)

# ==== 结构预测 ====
def predict_from_fasta(fasta_path, output_pdb):
    print(f"🔬 Predicting structure from FASTA: {fasta_path}")
    cmd = f"protenix_predict --fasta {fasta_path} --output {output_pdb}"
    subprocess.run(cmd, shell=True, check=True)

def predict_from_pdb(input_pdb, output_pdb):
    print(f"🔬 Predicting structure from PDB: {input_pdb}")
    cmd = f"protenix_predict {input_pdb} {output_pdb}"
    subprocess.run(cmd, shell=True, check=True)

# ==== DALI 导入 ====
def import_to_dali(pdb_path, pdb_id, dat_path):
    print(f"📥 Importing {pdb_path} to DALI format as ID: {pdb_id}")
    cmd = f"{DALI_BIN}/import.pl --pdbfile {pdb_path} --pdbid {pdb_id} --dat {dat_path} --clean"
    subprocess.run(cmd, shell=True, check=True)

# ==== DALI 比对 ====
def run_dali(cd1, cd2, dat1, dat2, output_file):
    print(f"🔗 DALI compare {cd1} vs {cd2}")
    cmd = f"{DALI_BIN}/dali.pl --cd1 {cd1} --cd2 {cd2} --dat1 {dat1} --dat2 {dat2} --outfmt summary --clean > {output_file}"
    subprocess.run(cmd, shell=True, check=True)

def parse_z_score(file_path):
    with open(file_path, "r") as f:
        for line in f:
            if line.strip().startswith("1:"):
                parts = line.strip().split()
                try:
                    return float(parts[2])  # Z-score
                except:
                    continue
    return None

# ==== 主流程 ====
def main():
    print("==== Step 1: Predicting reference structure from FASTA ====")
    predict_from_fasta(REFERENCE_FASTA, REFERENCE_PDB)
    import_to_dali(REFERENCE_PDB, REFERENCE_ID, DAT_DIR)

    results = {}

    print("==== Step 2: Processing input PDBs ====")
    for fname in os.listdir(INPUT_DIR):
        if fname.endswith(".pdb"):
            basename = os.path.splitext(fname)[0]
            pdb_id = basename[:4].lower()  # 确保4字符
            input_path = os.path.join(INPUT_DIR, fname)
            pred_path = os.path.join(PREDICTED_DIR, f"{basename}_pred.pdb")
            output_txt = f"{pdb_id}_vs_ref.txt"

            predict_from_pdb(input_path, pred_path)
            import_to_dali(pred_path, pdb_id, DAT_DIR)

            run_dali(pdb_id + "A", REFERENCE_ID + "A", DAT_DIR, DAT_DIR, output_txt)
            z = parse_z_score(output_txt)

            if z:
                results[fname] = z
                print(f"✅ {fname}: Z-score = {z}")
            else:
                print(f"⚠️ {fname}: No Z-score found")

    if results:
        print("\n🎯 Final Results:")
        for f, z in sorted(results.items(), key=lambda x: -x[1]):
            print(f"{f}: Z = {z}")
        best = max(results, key=results.get)
        print(f"\n🏆 Best match: {best} with Z = {results[best]}")
    else:
        print("❌ No valid results.")

if __name__ == "__main__":
    main()
