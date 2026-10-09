#!/bin/bash -l
#SBATCH --job-name=llm-query
#SBATCH --output=%x-%j.out
#SBATCH --error=%x-%j.out
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=7
#SBATCH --gpus-per-task=1
#SBATCH --mem=32G
#SBATCH --time=00:30:00
#SBATCH --partition=gpu
#SBATCH --qos=normal

set -euo pipefail

if (( $# < 3 )); then
    echo "Usage: sbatch [Slurm options] $0 IMAGE MODEL 'PROMPT' [llama-cli options...]" >&2
    echo "IMAGE and MODEL must be absolute paths visible on the compute node." >&2
    exit 2
fi
image=$1
model=$2
prompt=$3
shift 3

for path in "$image" "$model"; do
    [[ "$path" == /* && "$path" != *[:,]* ]] || {
        echo "Paths must be absolute and must not contain ':' or ',': $path" >&2
        exit 2
    }
    [[ -f "$path" ]] || { echo "File not found: $path" >&2; exit 2; }
done
[[ -n "$prompt" ]] || { echo "Prompt must not be empty" >&2; exit 2; }

module purge
module load tools/Apptainer
if [[ -v CUDA_VISIBLE_DEVICES ]]; then
    export APPTAINERENV_CUDA_VISIBLE_DEVICES="$CUDA_VISIBLE_DEVICES"
fi

echo "Started: $(date -Is); node: $(hostname); job: ${SLURM_JOB_ID:-unknown}"
printf 'Model: %s\nPrompt: %s\n' "$model" "$prompt"
# Use the model's chat template, run one turn, then exit. No listening port.
# EOF on stdin prevents an accidental interactive wait.
srun apptainer exec --nv --cleanenv --no-mount home \
    --bind "$(dirname "$model"):/models:ro" \
    "$image" /opt/llama.cpp/build/bin/llama-cli \
    --model "/models/$(basename "$model")" \
    --n-gpu-layers 99 --ctx-size 4096 \
    --threads "${SLURM_CPUS_PER_TASK:-7}" \
    --conversation --single-turn --prompt "$prompt" \
    --n-predict 128 --temp 0 --seed 42 \
    "$@" </dev/null

echo "Completed successfully: $(date -Is)"
