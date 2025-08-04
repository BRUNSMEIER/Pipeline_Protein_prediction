import os
import shutil
import subprocess
import argparse
import glob

# Fixed paths
superfamily_dir = '/mnt/data2/supfam/supfam/'
superfamily_script = os.path.join(superfamily_dir, 'superfamily.pl')
fangshun_dir = '/mnt/data2/supfam/fangshun/'
results_dir = os.path.join(fangshun_dir, 'supfamresults/')

# Create output directory if it doesn't exist
os.makedirs(results_dir, exist_ok=True)

def run_superfamily_pipeline(input_fasta):
    base_name = os.path.basename(input_fasta).replace('.fa', '')
    target_fasta = os.path.join(superfamily_dir, f"{base_name}.fa")

    # Copy input FASTA file to SUPERFAMILY working directory
    shutil.copy2(input_fasta, target_fasta)

    print(f"\n✅ Running SUPERFAMILY on: {target_fasta}")
    try:
        # Run the annotation script
        subprocess.run(
            ['perl', superfamily_script, f"{base_name}.fa"],
            cwd=superfamily_dir,
            check=True
        )

        # Default output filenames from the pipeline
        raw_ass = os.path.join(superfamily_dir, '.ass')
        raw_html = os.path.join(superfamily_dir, '.html')

        # Rename output files with base name
        out_ass = os.path.join(superfamily_dir, f"{base_name}.ass")
        out_html = os.path.join(superfamily_dir, f"{base_name}.html")

        # Final destination paths in the fangshun/supfamresults/ directory
        dest_ass = os.path.join(results_dir, f"{base_name}.ass")
        dest_html = os.path.join(results_dir, f"{base_name}.html")

        if os.path.exists(raw_ass):
            shutil.move(raw_ass, out_ass)
            shutil.copy2(out_ass, dest_ass)
        if os.path.exists(raw_html):
            shutil.move(raw_html, out_html)
            shutil.copy2(out_html, dest_html)

        print(f"✅ Output saved as: {out_ass}, {out_html}")
        print(f"📁 Copied to results folder: {dest_ass}, {dest_html}")

    except subprocess.CalledProcessError as e:
        print(f"❌ Error running SUPERFAMILY: {e}")
    except FileNotFoundError:
        print("❌ superfamily.pl not found or not executable.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run SUPERFAMILY structural annotation and save results to supfamresults directory."
    )
    parser.add_argument('input_fasta', nargs='?', default=None,
                        help="Path to input FASTA file or directory")

    args = parser.parse_args()

    fasta_dir = os.path.join(fangshun_dir, 'fasta/')

    if args.input_fasta is None or os.path.isdir(args.input_fasta):
        fa_files = glob.glob(os.path.join(fasta_dir, '*.fa'))
        if not fa_files:
            print(f"No .fa files found in {fasta_dir}")
        for fa_file in fa_files:
            run_superfamily_pipeline(fa_file)
    else:
        run_superfamily_pipeline(args.input_fasta)
