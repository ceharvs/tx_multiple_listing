#!/bin/bash 
# Submit the job with a specific name
#MSUB -N queuing_model
# Specify resources
#MSUB  -l nodes=1:ppn=7,walltime=01:00:00 -W ENVREQUESTED:TRUE
# Combine the standard out and standard error in the same output file
#MSUB -j oe
#MSUB -o queuing.out
# Pass environment variables
#MSUB -E
# Run as a job array from 0-1009
#MSUB -t jobarrays[0-1009]

# Move into user's working directory
cd $PBS_O_WORKDIR

# Asign and create an output directory
OUTPUT_DIR='20181127'
mkdir -p ${OUTPUT_DIR}


# Convet the JOBID to a number and define the advantage probability and the seed
let "JOB_ID = $((MOAB_JOBARRAYINDEX))"
let "ADV_PROB = $JOB_ID % 101"
let "SEED = $JOB_ID / 101"

# Run Python Code
python3 main.py $SEED $ADV_PROB ${OUTPUT_DIR}/${MOAB_JOBARRAYINDEX}.csv

echo -e "Job submitted by $PBS_O_LOGNAME ran on $HOSTNAME with:\n\tJOBARRAYINDEX=$MOAB_JOBARRAYINDEX\n\tADV_PROB=$ADV_PROB\n\tSEED=$SEED"
