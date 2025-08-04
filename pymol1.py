import pymol
import os

# Start PyMOL
output_dir = "structures"
os.makedirs(output_dir, exist_ok=True)

pymol.finish_launching(['pymol', '-qc'])
# Load the reference PDB file
pymol.cmd.load('7.6.2.14.pdb', 'reference')
# Iterate over the list of PDB files to align and cluster
pdb_files = ['1v43A.pdb']
for pdb_file in pdb_files:
# Load the current PDB file
    pymol.cmd.load(pdb_file, 'current')
    # Align all atoms to the reference
    pymol.cmd.align('current', 'reference')
    # Cluster the aligned structure based on CA atoms
    # pymol.cmd.cluster('current', cutoff=3.0, selection='name CA')
    # Save the aligned and clustered structure
    pymol.cmd.zoom('current')
    pdb_out_path = os.path.join(output_dir, 'aligned_clustered_' + pdb_file)
    pymol.cmd.save(pdb_out_path, 'current')
    png_out_path = os.path.join(output_dir, 'aligned_clustered_' + pdb_file.replace('.pdb', '.png'))
    pymol.cmd.png(png_out_path, dpi=300, ray=1)

    # Delete the current structure from the PyMOL session
    
# Quit PyMOL
