# Protein Structure Prediction and Analysis Pipeline

This repository contains the scripts and resources used to generate all data and results presented in my graduation thesis.  
The pipeline integrates **sequence-to-structure prediction**, **structural format conversion**, **functional superfamily classification**, and **structure-based alignment and visualisation**.

## Workflow Overview

```
FASTA (.fa)
   ↓
(fasta → json) via pipeline.py
   ↓
Protenix → mmCIF (.cif)
   ↓
mmCIF → PDB (.pdb)
   ↓
+ SUPFAM → Functional classification (HTML report)
+ DaliLite → Structural alignment (Z-score summary)
+ PyMOL → Publication-ready figures
```

All scripts are configured to run **directly on the UCL school server** under:

```
/mnt/data2/supfam/<Your_Name>/
```

Required paths, variables, and parameters are **pre-configured** for this environment.  
Simply run:

```bash
python <script_name>.py
```

The outputs will match those used in the thesis.

---

## Script Overview

### `pipeline.py`
Main entry point for the complete automated workflow:
1. Converts FASTA input to JSON for Protenix.
2. Runs Protenix to produce `.mmCIF` structural models.
3. Converts `.mmCIF` to `.pdb` format.
4. Runs SUPFAM for functional superfamily classification.
5. Performs structural alignment via DaliLite.
6. Generates HTML and visualisation outputs.

---

### `predictcif.py`
Runs Protenix directly on prepared JSON sequence files to generate `.mmCIF` models.

---

### `supfamhtml.py`
Parses SUPFAM `.tbl` output files and generates HTML-formatted classification reports.

---

### `pymol1.py`
Automates PyMOL visualisations:
- Loads predicted `.pdb` structures.
- Applies colour schemes and alignment.
- Saves publication-quality images for inclusion in the thesis.

---

### `dali.py`
Runs DaliLite for structure-based alignment:
- Compares target structures to reference models.
- Outputs per-comparison `.txt` reports and a `zscore_summary.csv`.

---

### Supporting Files and Folders
- **`reference.pdb`** — Reference structure used in alignment.
- **`target.fasta`**, **`target.json`**, **`target.pdb`** — Example inputs.
- **`*.pdb`, `*.json`, `*.fa`** — Example files used during testing.
- **`htmlreport/`** — Output HTML reports from SUPFAM.
- **`visualisation/`** — PyMOL-rendered structural images.
- **`predicted_structures/`** — Protenix-generated models.
- **`input_pdbs/`** — Structures submitted to DaliLite.
- **`fasta/`** — Sequence files for batch processing.

---

## Dependencies
All required dependencies are installed and configured on the school server, including:
- Python 3.x
- Protenix
- SUPFAM
- DaliLite.v5
- PyMOL

---

## Running the Pipeline

### Full Pipeline:
```bash
python pipeline.py
```
Produces all structural models, classifications, alignments, and visualisation outputs.

### Individual Steps:
```bash
python predictcif.py     # Only run Protenix
python supfamhtml.py     # Only generate SUPFAM HTML report
python dali.py           # Only run DaliLite alignment
python pymol1.py         # Only render PyMOL visualisations
```

---

## Notes
- All outputs from this repository correspond directly to figures, tables, and results in the thesis.
- Large multi-chain inputs (**>10 chains**) may cause Protenix runtime errors due to memory constraints; see thesis Methodology for mitigation strategies.
