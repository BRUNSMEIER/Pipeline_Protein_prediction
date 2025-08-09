import subprocess
import argparse
from Bio import SearchIO

# Default paths
default_target = 'target.fasta'
model_tab = '/mnt/data2/supfam/supfam/model.tab'

def predict_superfamily(input_fasta, hmm_library='/mnt/data2/supfam/supfam/hmmlib', output_tbl='output.tbl', e_value_threshold=0.001):
    """
    Predict structural superfamilies for input FASTA sequences using the SUPERFAMILY HMM library.
    
    Parameters:
    - input_fasta: Path to the input FASTA file.
    - hmm_library: Path to the SUPERFAMILY HMM library (default: /mnt/data2/supfam/supfam/hmmlib).
    - output_tbl: Output file path for HMMER's domain table (default: output.tbl).
    - e_value_threshold: E-value cutoff for filtering significant matches (default: 0.001).
    
    Returns: Prints matched superfamily IDs and related information for each query.
    """
    # Dictionary to store mapping from superfamily IDs to names
    id_to_name = {}

    print(f"Starting prediction for file: {input_fasta}")
    print(f"HMM library: {hmm_library}")

    # Run hmmscan command
    try:
        result = subprocess.run([
            '/mnt/data2/supfam/hmmer-3.1b2/src/hmmscan',  # Full path to hmmscan binary
            '--domtblout', output_tbl,
            '-E', str(e_value_threshold),
            hmm_library,
            input_fasta
        ], check=True, capture_output=True, text=True)

        print("hmmscan ran successfully. Stdout:", result.stdout)
        print("Stderr (if any):", result.stderr)
    except subprocess.CalledProcessError as e:
        print(f"Error running hmmscan: {e.stderr}")
        return
    except FileNotFoundError as fnf:
        print(f"Command not found: {fnf}")
        return

    print("Parsing output file...")

    try:
        # Parse HMMER domtblout results
        queries = list(SearchIO.parse(output_tbl, 'hmmscan3-domtab'))
        if not queries:
            print("No queries found in output.")

        for query in SearchIO.parse(output_tbl, 'hmmscan3-domtab'):
            print(f"\nQuery sequence: {query.id}")
            if not query.hits:
                print("No significant superfamily matches found.")
                continue

            for hit in query.hits:
                for hsp in hit.hsps:
                    if hsp.evalue < e_value_threshold:
                        superfamily_id = hit.id  # This is the SCOP superfamily ID (e.g., '46458')
                        print(f" - Superfamily ID: {superfamily_id}")
                        print(f"   E-value: {hsp.evalue}")
                        print(f"   Bit score: {hsp.bitscore}")
                        print(f"   Domain boundaries: {hsp.query_start}-{hsp.query_end}")
    except Exception as e:
        print(f"Error parsing output: {e}")
        return

    # Load mapping from superfamily ID to human-readable name
    with open(model_tab, 'r') as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 2:
                id_to_name[parts[0]] = parts[1]

    # Print human-readable superfamily name for the last matched ID (if any)
    superfamily_name = id_to_name.get(superfamily_id, 'Unknown')
    print(f" - Superfamily Name: {superfamily_name}")

if __name__ == "__main__":
    # Argument parser setup
    parser = argparse.ArgumentParser(description="Predict structural superfamilies using SUPERFAMILY HMM.")
    parser.add_argument('input_fasta', nargs='?', default='target.fasta', help="Path to input FASTA file")
    parser.add_argument('--hmm_library', default='/mnt/data2/supfam/supfam/hmmlib', help="Path to SUPERFAMILY HMM library")
    parser.add_argument('--e_value', type=float, default=0.001, help="E-value threshold for filtering")

    args = parser.parse_args()
    
    # Run prediction function
    predict_superfamily(args.input_fasta, args.hmm_library, e_value_threshold=args.e_value)
