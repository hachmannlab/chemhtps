#!/bin/sh
#SBATCH --clusters=ub-hpc
#SBATCH --partition=gpu --qos=gpu
#SBATCH --time=72:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --job-name="qchemtest"
#SBATCH --output=slurm.out

echo "SLURM job ID         = "$SLURM_JOB_ID
echo "Working Dir          = "$SLURM_SUBMIT_DIR
echo "Temporary scratch    = "$SLURMTMPDIR
echo "Compute Nodes        = "$SLURM_JOB_NODELIST
echo "Number of Processors = "$SLURM_NPROCS
echo "Number of Nodes      = "$SLURM_JOB_NUM_NODES
echo "Tasks per Node       = "$SLURM_TASKS_PER_NODE
echo "Memory per Node      = "$SLURM_MEM_PER_NODE

#export INFILE=inp_ut.inp
#export OUTFILE=QC.out
infile here
outfile here

module load qchem/4.4
module list
ulimit -s unlimited
#
export QCLOCALSCR=$SLURMTMPDIR

echo "SLURM_JOB_NODELIST"=$SLURM_JOB_NODELIST
echo "SLURM_NNODES"=$SLURM_NNODES

export PBS_NODEFILE=nodelist.$$
srun --nodes=${SLURM_NNODES} bash -c 'hostname' | sort > $PBS_NODEFILE
cat $PBS_NODEFILE

NPROCS=`cat $PBS_NODEFILE | wc -l`
echo "NPROCS="$NPROCS

qchem -pbs -np $NPROCS $INFILE $OUTFILE
#
echo "All Done!"
