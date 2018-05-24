#!/bin/bash
#SBATCH -p highmem
#SBATCH --job-name=bee_param_sweep  # Job name
#SBATCH --mail-type=ALL             # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --mail-user=ding1018@colorado.edu
#SBATCH --nodes=1
#SBATCH --ntasks=48
#SBATCH --mem=1000gb                # Memory limit
#SBATCH --time=72:00:00             # Time limit hrs:min:sec
#SBATCH --output=/Users/ding1018/bee_communication_project/eofiles/slurm_test_%j.out     # Standard output and error log
#SBATCH --error=/Users/ding1018/bee_communication_project/eofiles/slurm_test_%j.err	 # %j inserts job number

pwd; hostname; date

module load python/3.6.3

python /Users/ding1018/bee_communication_project/main.py

date
