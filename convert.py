#!/usr/bin/env python3
"""
make_reference_pdb.py
———————————————
• 在 Protenix 预测完成后运行
• 把 predicted_structures/**.cif → reference.pdb
"""

import glob, sys
from pathlib import Path
import gemmi                           # pip install gemmi

# === 参数：按需修改 ===
PRED_DIR    = "predicted_structures"   # Protenix out_dir
OUTPUT_PDB  = "reference.pdb"          # 生成目标

def pick_cif(cif_list):
    """
    如果你想挑特定 seed/sample，可在此过滤。
    目前：取列表中第一个文件。
    """
    return cif_list[0] if cif_list else None

def main():
    # 递归找 .cif
    cif_files = glob.glob(str(Path(PRED_DIR) / "**" / "*.cif"), recursive=True)
    if not cif_files:
        print(f"[ERROR] 在 {PRED_DIR}/ 及子目录下未找到 .cif 文件", file=sys.stderr)
        sys.exit(1)

    cif_path = pick_cif(sorted(cif_files))
    print(f"✔ 选用 mmCIF: {cif_path}")

    # 转 PDB
    st = gemmi.read_structure(cif_path)
    st.write_pdb(OUTPUT_PDB)
    print(f"✓ 已生成 {OUTPUT_PDB}")

if __name__ == "__main__":
    main()
