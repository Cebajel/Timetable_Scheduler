#!/bin/sh
#SBATCH --output=/home/BTech/cebajel/slurm-%j.out
#SBATCH --error=/home/BTech/cebajel/slurm-%j.err
#SBATCH --ntasks=64
#SBATCH --time=12:00:00
#SBATCH --partition=normal
#SBATCH --mail-user=210010055@iitdh.ac.in
#SBATCH --mail-type=ALL

source /home/BTech/cebajel/Great/great/bin/activate
python /home/BTech/cebajel/Great/Source/scheduler.py