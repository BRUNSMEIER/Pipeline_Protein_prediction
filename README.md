# Protein Structure Prediction and Analysis Pipeline

This repository contains the scripts and resources used to generate all data and results presented in my graduation thesis.  
The pipeline integrates **sequence-to-structure prediction**, **structural format conversion**, **functional superfamily classification**, and **structure-based alignment and visualisation**.

> **Environment note**: Due to virtual-environment differences on the school server, **Protenix and PyMOL are *not* executed by `pipeline.py`**.  
> `pipeline.py` runs **SUPFAM prediction** and **DaliLite alignment** only. Protenix and optional PyMOL rendering are executed in a separate environment, and their outputs are then consumed by the server-side pipeline.

All server-side scripts are configured to run under:

```
/mnt/data2/supfam/fangshun/
```

Paths, variables, and parameters are **pre-configured** for this location. For server-side steps, you can simply run:

```bash
python <script_name>.py
```

The outputs reproduce the results used in the thesis.

---

## Workflow Overview (Two-Stage Execution)

```
Stage A — Structure Prediction (Protenix environment, UCL server Coulomb)
  conda activate protoneix #initiate virtual environment
  FASTA → JSON (e.g., fasta2json.py)
      → Protenix → mmCIF (.cif)  (predictcif.py)
      → mmCIF → PDB (.pdb)       (also contained in predictcif.py)

Stage B — Classification & Alignment (Server main environment, UCL server Coulomb)
  SUPFAM → .tbl + HTML report   (pipeline.py / supfamhtml.py)
  DaliLite → alignments + Z-scores (pipeline.py / dali.py)
  →  PyMOL figures (pymol1.py)
```

---

## Script Overview

### `pipeline.py`  *(server-side)*
Runs **SUPFAM superfamily prediction** and **DaliLite alignment** on prepared structural inputs.  
It expects `.mmCIF`/`.pdb` files produced in Stage A to be available under the pre-configured directories.  
Outputs include SUPFAM classification artefacts, DaliLite comparison files, and summary tables used in the thesis.

---

### `predictcif.py`  *(Protenix environment)*
Executes Protenix on JSON sequence files to generate `.mmCIF` models.  
Run this in an environment where Protenix is installed and licensed.

---

### `supfamhtml.py`  *(server-side)*
Parses SUPFAM `.tbl` outputs and generates HTML-formatted classification reports.

---

### `dali.py`  *(server-side)*
Runs DaliLite structure-based alignment:
- Compares target structures to reference models.
- Produces per-comparison `.txt` reports and a `zscore_summary.csv`.

---

### `pymol1.py`  *(PyMOL environment, optional)*
Automates PyMOL visualisations (not part of `pipeline.py` on the server):
- Loads predicted `.pdb` structures.
- Applies colouring/alignment.
- Saves publication-quality figures.

---

### Supporting Files and Folders
- **`reference.pdb`** — Reference structure used in alignment.
- **`target.fasta`**, **`target.json`**, **`target.pdb`** — Example inputs.
- **`*.pdb`, `*.json`, `*.fa`** — Example files used during testing.
- **`htmlreport/`** — Output HTML reports from SUPFAM.
- **`Structures/`** — PyMOL-rendered structural images and pdb alignment models
- **`predicted_structures/`** — Protenix-generated models.
- **`input_pdbs/`** — Structures submitted to DaliLite.
- **`fasta/`** — Sequence files for batch processing.

---

## Running Instructions

### Stage A — Structure Prediction (Protenix environment)
```bash
python predictcif.py          # Generate .mmCIF from sequences

```
Automatically generate the resulting `.pdb` files into the server directory:
```
/mnt/data2/supfam/fangshun/
```

### Stage B — Classification & Alignment (Server)
```bash
python pipeline.py            # Runs SUPFAM + DaliLite on available structures
# or run individual steps:
python supfamhtml.py
python dali.py
```
# optional:
python pymol1.py              # Render figures if PyMOL is available
---

## Dependencies

**Server environment** (pre-configured):
- Python 3.x
- SUPFAM
- DaliLite.v5

**Protenix/PyMOL environment** (separate from the server pipeline):
- Protenix
- PyMOL (for figure generation)

All server-side variables and paths are already set for `/mnt/data2/supfam/<Your_Name>/`.

---

## `src_gadget` Directory

This folder contains various format conversion scripts and legacy test files.
They are **not** part of the main automated pipeline, but can be run individually if needed.

To use them:
1. Copy or move the desired script from `src_gadget/` into the working directory.
2. Run with:
```bash
python <script_name>.py
```
3. Follow the specific input/output format described in the comments at the beginning of each script.

### Script Notes:
- **`convert.py`** & **`cif2pdb.py`** — Both convert `.mmCIF` files into `.pdb` format, the latter one cif2pdb.py is specifically used to convert the 12 types of mmcif files used for comparison into pdb format files. Note that predictcif.py already contains the function for converting mmcifs into PDB, so these two scripts are just for testing.
- **`prep.py`** — Alternative version of `predictcif.py` for running Protenix directly.
- **`supfampred.py`** — Generates `.tbl` format reports from SUPFAM classification output.  
  This python file is retained here in this folder due to tbl results' low human readability.
- **`extractzscore.py`** — Extract Z-scores from DALI output TXT files and generate CSV
- **`fasta2json.py`** — Convert the raw input of FASTA sequences into json format, which is required by PROTENIX. Usage:
    python fasta2json.py <input.fasta>  for example: python fasta2json.py target.fasta

---

## Notes
- All outputs from this repository correspond directly to the figures, tables, and results in the thesis.
- Large multi-chain inputs (**>10 chains**) may cause Protenix runtime errors (e.g., list index errors) due to memory limits and complexity; see thesis Methodology for mitigation strategies.
