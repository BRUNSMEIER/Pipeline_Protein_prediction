import subprocess
import argparse
from Bio import SearchIO
import os
import glob

model_tab = '/mnt/data2/supfam/supfam/model.tab'

def predict_superfamily(input_fasta, hmm_library='/mnt/data2/supfam/supfam/hmmlib', e_value_threshold=0.001):
    """
    Predict structural superfamilies using the SUPERFAMILY HMM library based on a FASTA sequence.
    
    Parameters:
    - input_fasta: Path to the input FASTA file.
    - hmm_library: Path to the SUPERFAMILY HMM library (default: /mnt/data2/supfam/supfam/hmmlib).
    - e_value_threshold: E-value threshold for filtering significant matches (default: 0.001).
    
    Returns: Prints the matching superfamily IDs and details for each query sequence, and saves summary to a file.
    """
    # Generate unique output table file based on input fasta name
    base_name = os.path.basename(input_fasta).replace('.fa', '')  # Remove .fa extension
    output_tbl = f"{base_name}_output.tbl"
    summary_file = f"{base_name}_summary.txt"  # Summary file for this fasta

    # Load model.tab
    id_to_name = {}
    with open(model_tab, 'r') as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 2:
                id_to_name[parts[0]] = parts[1]

    print(f"Starting prediction for file: {input_fasta}")  # Add this line
    print(f"HMM library: {hmm_library}")
    print(f"Output table: {output_tbl}")
    print(f"Summary file: {summary_file}")
    
    try:
        result = subprocess.run([
            '/mnt/data2/supfam/hmmer-3.1b2/src/hmmscan',  # Add absolute path
            '--domtblout', output_tbl,
            '-E', str(e_value_threshold),
            hmm_library,
            input_fasta
        ], check=True, capture_output=True, text=True)
        print("hmmscan ran successfully. Stdout:", result.stdout)  # Add
        print("Stderr (if any):", result.stderr)  # Add
    except subprocess.CalledProcessError as e:
        print(f"Error running hmmscan: {e.stderr}")
        return
    except FileNotFoundError as fnf:
        print(f"Command not found: {fnf}")  # New capture
        return

    print("Parsing output file...") # Parse output
    try:
        # Open summary file for writing
        with open(summary_file, 'w') as sf:
            queries = list(SearchIO.parse(output_tbl, 'hmmscan3-domtab'))
            if not queries:
                print("No queries found in output.")  # Add
                sf.write("No queries found in output.\n")
    
            for query in SearchIO.parse(output_tbl, 'hmmscan3-domtab'):
                print(f"\nQuery sequence: {query.id}")
                sf.write(f"\nQuery sequence: {query.id}\n")
                if not query.hits:
                    print("No significant superfamily matches found.")
                    sf.write("No significant superfamily matches found.\n")
                    continue
                
                for hit in query.hits:
                    for hsp in hit.hsps:
                        if hsp.evalue < e_value_threshold:
                            superfamily_id = hit.id  # This is the SCOP superfamily ID, e.g., '46458'
                            superfamily_name = id_to_name.get(superfamily_id, 'Unknown')
                            print(f" - Superfamily ID: {superfamily_id}")
                            print(f" - Superfamily Name: {superfamily_name}")
                            print(f"   E-value: {hsp.evalue}")
                            print(f"   Bit score: {hsp.bitscore}")
                            print(f"   Domain boundaries: {hsp.query_start}-{hsp.query_end}")
                            sf.write(f" - Superfamily ID: {superfamily_id}\n")
                            sf.write(f" - Superfamily Name: {superfamily_name}\n")
                            sf.write(f"   E-value: {hsp.evalue}\n")
                            sf.write(f"   Bit score: {hsp.bitscore}\n")
                            sf.write(f"   Domain boundaries: {hsp.query_start}-{hsp.query_end}\n")
    except Exception as e:
        print(f"Error parsing output: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Predict structural superfamilies using SUPERFAMILY HMM.")
    parser.add_argument('input_fasta', nargs='?', default=None, help="Path to input FASTA file or directory")  # Allow optional
    parser.add_argument('--hmm_library', default='/mnt/data2/supfam/supfam/hmmlib', help="Path to SUPERFAMILY HMM library")
    parser.add_argument('--e_value', type=float, default=0.001, help="E-value threshold for filtering")
    
    args = parser.parse_args()
    
    fasta_dir = '/mnt/data2/supfam/fangshun/fasta/'
    if args.input_fasta is None or os.path.isdir(args.input_fasta):
        # If not specified or specified as a directory, process all .fa files under fasta/
        fa_files = glob.glob(os.path.join(fasta_dir, '*.fa'))
        if not fa_files:
            print(f"No .fa files found in {fasta_dir}")
        for fa_file in fa_files:
            print(f"\nProcessing file: {fa_file}")
            predict_superfamily(fa_file, args.hmm_library, e_value_threshold=args.e_value)
    else:
        # Otherwise process a single file
        predict_superfamily(args.input_fasta, args.hmm_library, e_value_threshold=args.e_value)