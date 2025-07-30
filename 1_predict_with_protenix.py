#!/usr/bin/env python3
"""
1_predict_with_protenix.py
———————————————
在 Protenix 环境中运行：
    • target.fasta  → reference.pdb
    • input_pdbs/*  → predicted_structures/<basename>_pred.pdb
CLI 兼容：
    protenix predict --input <file|dir> --out_dir <dir> …
"""

import os
import sys
import glob
import shutil
import subprocess
from pathlib import Path


# === 基本路径 ===
PROTENIX      = "protenix"          # 若不在 $PATH，请写绝对路径
INPUT_DIR     = "input_pdbs"
PRED_DIR      = "predicted_structures"
TARGET_FASTA  = "target_without_msa.json"
REFERENCE_PDB = "reference.pdb"


def run(cmd: str) -> None:
    """执行命令并在失败时抛异常，便于 SLURM 捕获"""
    print(f"▶ {cmd}", flush=True)
    subprocess.run(cmd, shell=True, check=True)


def predict_to_single_pdb(src: str, dst_pdb: str) -> None:
    """
    调用 protenix 预测并把生成的第一个 PDB 文件移动/重命名到 dst_pdb
    src      : 输入文件（.fasta / .pdb）
    dst_pdb  : 期望保存的最终 PDB 路径
    """
    base   = Path(src).stem
    tmpdir = Path(PRED_DIR) / f"tmp_{base}"
    tmpdir.mkdir(parents=True, exist_ok=True)

    # Protenix 不区分 input 类型的话，可删掉 typ_flag
    run(f"{PROTENIX} predict --input {src} --out_dir {tmpdir} --use_msa_server")

    # 抓第一个生成的 PDB（若你想自定义规则，可修改这里）
    pdb_candidates = sorted(glob.glob(str(tmpdir / "*.pdb")))
    if not pdb_candidates:
        raise RuntimeError(f"[{src}] 预测后未发现 PDB 文件，目录：{tmpdir}")

    first_pdb = pdb_candidates[0]
    shutil.move(first_pdb, dst_pdb)
    shutil.rmtree(tmpdir)          # 如想保留临时目录，注释掉此行
    print(f"✓ saved → {dst_pdb}", flush=True)


def main() -> None:
    os.makedirs(PRED_DIR, exist_ok=True)

    # 1) 预测目标 FASTA → reference.pdb
    predict_to_single_pdb(TARGET_FASTA, REFERENCE_PDB)

    # 2) 预测 input_pdbs 中的 8 个结构
    for fname in sorted(os.listdir(INPUT_DIR)):
        if not fname.lower().endswith(".pdb"):
            continue
        src_path = os.path.join(INPUT_DIR, fname)
        dst_path = os.path.join(
            PRED_DIR, f"{Path(fname).stem}_pred.pdb"
        )
        predict_to_single_pdb(src_path, dst_path)


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)
    except Exception as exc:
        print("ERROR:", exc, file=sys.stderr, flush=True)
        sys.exit(1)
