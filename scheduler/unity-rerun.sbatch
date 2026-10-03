#!/bin/bash
#SBATCH --job-name=reproseed-rerun
#SBATCH --partition=cpu
#SBATCH --constraint=amd
#SBATCH --cpus-per-task=4
#SBATCH --mem=4G
#SBATCH --time=00:10:00
#SBATCH --output=unity-rerun-%j.log
set -euo pipefail
cd "$HOME/reproseed/dataset"
../reproseed-pixi run --locked datalad rerun c3fa2559a942cebce693fd6f9608ee77558855ab
