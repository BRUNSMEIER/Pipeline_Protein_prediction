#!/usr/bin/env bash
set -euo pipefail

# -------- 配置 --------
DALIBIN=/mnt/data2/supfam/fangshun/DaliLite.v5/bin
DATDIR=/mnt/data2/supfam/fangshun/imported_DAT
PDBDIR=/mnt/data2/supfam/fangshun/input_pdbs
REFPDB=/mnt/data2/supfam/fangshun/reference.pdb

# -------- 导入参考结构 --------
echo "==== 导入参考结构 $REFPDB 为 ID ref ===="
import.pl --pdbfile "$REFPDB" --pdbid ref --dat "$DATDIR" \
  || echo "WARNING: pdbid 长度不能超过4字符，已跳过"

# -------- 准备汇总表 --------
echo "pdb,Zscore" > zscore_summary.csv

# -------- 主循环 --------
for pdbpath in "$PDBDIR"/*.pdb; do
  pdb=$(basename "${pdbpath%.*}")
  [[ "$pdb" == "reference" ]] && continue

  echo "---- 处理 $pdb ----"

  # 1) 生成 DSSP
  "$DALIBIN/dsspcmbi" "$pdbpath" "$pdb.dssp"

  # 2) WOLF→DP，拿到 fort.*
  "$DALIBIN/serialcompare" "$DATDIR/$pdb/" "$DATDIR/ref/" WOLF > /dev/null
  cat fort.1[0-9][0-9] > wolf_output 2>/dev/null || true
  rm -f fort.1[0-9][0-9]
  "$DALIBIN/serialcompare" "$DATDIR/$pdb/" "$DATDIR/ref/" DP < wolf_output > /dev/null

  # 3) 用 dccp2dalicon.pl 直接生成 list1
  cat fort.1[0-9][0-9] | perl "$DALIBIN/dccp2dalicon.pl" > list1 2>/dev/null || true
  rm -f fort.1[0-9][0-9] wolf_output

  # 确保 list1 存在（即使空文件也要 touch）
  [[ -f list1 ]] || touch list1

  # 4) 运行 soap4 —— 它会自己 open('list1') 来读
  #    不要用 "< list1"
  soap4_out="${pdb}_soap4.out"
  "$DALIBIN/soap4" > "$soap4_out" 2>&1

  # 5) 从 soap4_out 中提取 Z‑score
  if z=$(perl -ne 'print "$1\n" and exit if /Z[- ]?score[:=]?\s*([0-9.]+)/i' "$soap4_out"); then
    :
  else
    z=NA
  fi

  # 写到汇总表
  echo "${pdb},${z}" >> zscore_summary.csv

  # 清理
  rm -f list1 "$soap4_out"
done

echo "所有 Z‑score 已写入 zscore_summary.csv"
