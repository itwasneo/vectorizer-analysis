#!/bin/bash -l
#SBATCH --job-name=llm-server
#SBATCH --output=%x-%j.out
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=7
#SBATCH --gpus-per-task=1
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --partition=gpu
#SBATCH --qos=normal

set -euo pipefail

if (( $# < 4 )); then
    echo "Usage: sbatch [Slurm options] $0 {llama-cpp|vllm} IMAGE MODEL CACHE [server options...]" >&2
    echo "Use --partition=hopper for vLLM. Paths must be absolute and visible on the compute node." >&2
    exit 2
fi
backend=$1
image=$2
model=$3
cache=$4
shift 4

for path in "$image" "$model" "$cache"; do
    [[ "$path" == /* && "$path" != *[:,]* ]] || {
        echo "Paths must be absolute and must not contain ':' or ',': $path" >&2
        exit 2
    }
done
[[ -f "$image" && -e "$model" ]] || { echo "Image or model not found" >&2; exit 2; }
mkdir -p "$cache"

case "$backend" in
    llama-cpp)
        [[ -f "$model" ]] || { echo "llama.cpp requires a GGUF file" >&2; exit 2; }
        options=(--model "/models/$(basename "$model")" --alias local-model
                 --n-gpu-layers 99 --ctx-size 4096)
        ;;
    vllm)
        [[ -d "$model" ]] || { echo "vLLM requires a Hugging Face model directory" >&2; exit 2; }
        options=(--model "/models/$(basename "$model")" --served-model-name local-model
                 --dtype half --max-model-len 4096
                 --tensor-parallel-size 1 --gpu-memory-utilization 0.90)
        ;;
    *) echo "Unknown backend: $backend" >&2; exit 2 ;;
esac

module purge
module load tools/Apptainer
# Preserve Slurm's GPU selection through --cleanenv; never replace it with a hardcoded GPU ID.
if [[ -v CUDA_VISIBLE_DEVICES ]]; then
    export APPTAINERENV_CUDA_VISIBLE_DEVICES="$CUDA_VISIBLE_DEVICES"
fi
export APPTAINERENV_HF_HUB_OFFLINE=1
export APPTAINERENV_TRANSFORMERS_OFFLINE=1

echo "Backend: $backend; node: $(hostname); port: 8000 (loopback only)"
srun apptainer run --nv --cleanenv --no-mount home \
    --bind "$(dirname "$model"):/models:ro,$cache:/cache" \
    "$image" "${options[@]}" \
    --host 127.0.0.1 --port 8000 "$@"
