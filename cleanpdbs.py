from pathlib import Path

INPUT_DIR = Path("input_pdbs")
OUTPUT_DIR = Path("cleaned_pdbs")
OUTPUT_DIR.mkdir(exist_ok=True)

def clean_pdb_lines(lines):
    cleaned = []
    for line in lines:
        record = line[:6].strip()
        altloc = line[16]  # alternate location indicator
        resname = line[17:20].strip()

        # 1. 删除 HETATM 行
        if record == "HETATM":
            continue

        # 2. 删除水分子
        if resname == "HOH":
            continue

        # 3. 删除 ALTLOC 不为 空格 或 A 的原子
        if altloc not in (" ", "A"):
            continue

        cleaned.append(line)

    return cleaned

for pdb_path in INPUT_DIR.glob("*.pdb"):
    print(f"Cleaning {pdb_path.name}...")
    with open(pdb_path, "r") as f:
        lines = f.readlines()

    cleaned_lines = clean_pdb_lines(lines)
    out_path = OUTPUT_DIR / pdb_path.name

    with open(out_path, "w") as f:
        f.writelines(cleaned_lines)

    print(f"✅ Cleaned → {out_path}")
