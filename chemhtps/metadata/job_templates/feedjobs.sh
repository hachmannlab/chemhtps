#!/usr/bin/env bash
#SBATCH --clusters=faculty
#SBATCH --partition=beta --qos=beta
#SBATCH --account=hachmann 
##SBATCH --time=0
#SBATCH --nodes=1
#SBATCH --job-name="feedjobs"
#SBATCH --output=feedjobs.out

# ====================================================
# For 16-core nodes
# ====================================================
#SBATCH --constraint=CPU-E5-2630v3
#SBATCH --tasks-per-node=1
##SBATCH --mem=64000

echo "SLURM job ID         = "$SLURM_JOB_ID
echo "Working Dir          = "$SLURM_SUBMIT_DIR
echo "Temporary scratch    = "$SLURMTMPDIR
echo "Compute Nodes        = "$SLURM_JOB_NODELIST
echo "Number of Processors = "$SLURM_NPROCS
echo "Number of Nodes      = "$SLURM_JOB_NUM_NODES
echo "Tasks per Node       = "$SLURM_TASKS_PER_NODE
echo "Memory per Node      = "$SLURM_MEM_PER_NODE

ulimit -s unlimited
#module load python



echo "Launch job"
chemhtpsshell --feedjobs_remote
#
echo "All Done!"
