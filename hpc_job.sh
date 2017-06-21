#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --time=72:00:00
#SBATCH --mem=4GB
#SBATCH --job-name=reference
#SBATCH --mail-type=END
#SBATCH --mail-user=yw1225@nyu.edu
#SBATCH --output=slurm_%j.out

module purge

JOBNAME=reference
RUNDIR=$SCRATCH/runs/$JOBNAME-${SLURM_JOB_ID/.*}
SOURCEDIR1=~/projects/reference_graph_python
SOURCEDIR2=~/anaconda3/lib/python3.6/site-packages

export PATH=SOURCEDIR1:$PATH
export PATH=SOURCEDIR2:$PATH

mkdir -p $RUNDIR

cd $RUNDIR
cp ~/projects/reference_graph_python/paper_list.txt  ./paper_list.txt

# now start the job:
python3 ~/projects/reference_graph_python/demo.py

# leave a blank line at the end
