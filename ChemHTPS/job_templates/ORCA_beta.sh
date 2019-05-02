#!/usr/bin/env bash
#SBATCH --clusters=chemistry
#SBATCH --partition=beta --qos=beta
#SBATCH --account=hachmann
#SBATCH --time=100:00:00
#SBATCH --nodes=1
#SBATCH --output=slurm.out

# ====================================================
# For 16-core nodes
# ====================================================
#SBATCH --constraint=CPU-E5-2650v4
#SBATCH --tasks-per-node=1
##SBATCH --mem=64000

cur_dir=$(pwd)
#export INFILE=inp_ut.inp 
#export OUTFILE=out_put.out
infile here
outfile here

if [ ! -f $INFILE ]; then
  echo "Error! Input file does not exist (${INFILE})"
  echo "Aborting the job..."
  exit
fi

BASE=`basename $INFILE .inp`

# a parallel version of the infile
PINFILE=${BASE}.pin

#construct nodefile, named as per Orca manual
export SLURM_NODEFILE=${BASE}.nodes

#use analogous naming convention for rankfile
export ORCA_RANKFILE=${BASE}.ranks

tic=`date +%s`
echo "Start Time = "`date`

# load modules
echo "Loading modules ..."
module load openmpi/gcc-4.8.3/1.6.5
export NBOEXE=/util/academic/nbo/nbo6/bin/nbo6.i4.exe
module load orca
module load nbo/6
ulimit -s unlimited
module list

# disable PSM interface if the nodes have Mellanox hardware
bMLX=`/usr/sbin/ibstat | head -n1 | grep mlx | wc -l`
if [ "$bMLX" == "1" ]; then
  export OMPI_MCA_mtl=^psm
fi

# change to working directory
#cd $SLURM_SUBMIT_DIR

echo "%pal nprocs $SLURM_NPROCS end" > $PINFILE
cat $INFILE | grep -v "^%pal nprocs" >> $PINFILE

echo "Launching orca ..."
echo "SLURM job ID         = "$SLURM_JOB_ID
echo "Working Dir          = "$SLURM_SUBMIT_DIR
echo "Compute Nodes        = "`nodeset -e $SLURM_NODELIST`
echo "Number of Processors = "$SLURM_NPROCS
echo "Number of Nodes      = "$SLURM_NNODES 
echo "mpirun command       = "`which mpirun`
echo "orca nodefile        = "$SLURM_NODEFILE
echo "orca rankfile        = "$ORCA_RANKFILE

echo " "
echo "Input file"
cat $PINFILE
echo " "

# create rank file to explicitly bind cores
echo "creating hostfile and rankfile"
uid=`id -u`
jid=$SLURM_JOB_ID
nodes=`nodeset -e $SLURM_NODELIST`

# trigger creation of cpuset information and save to working dir
srun bash -c "cat /cgroup/cpuset/slurm/uid_${uid}/job_${jid}/cpuset.cpus > cpus.\`hostname\`.$SLURM_JOB_ID"

rm -f $ORCA_RANKFILE
rm -f $SLURM_NODEFILE
rank=0
for i in ${nodes}; do
  # extract space-separated list of assigned cpus
  cpus=`cat cpus.${i}.${SLURM_JOB_ID}`
  cpus=`nodeset -Re $cpus`
  # add cpu assignments to the rank file
  for j in ${cpus}; do
    echo "rank ${rank}=$i slot=$j" >> $ORCA_RANKFILE
    echo "$i" >> $SLURM_NODEFILE
    rank=`expr $rank + 1`
    if [ "$rank" == "$SLURM_NPROCS" ]; then
      break;
    fi
  done
  if [ "$rank" == "$SLURM_NPROCS" ]; then
    break;
  fi
done

# use ssh instead of slurm as the launcher
# the rankfile that was just created will ensure cpusets are still honored.
export OMPI_MCA_plm=rsh

# launch application using mpirun
echo "Launching application using mpirun"

# launch application
$ORCA_PATH/orca $PINFILE >> $OUTFILE

echo "All Done!"
