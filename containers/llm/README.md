# Open-weight LLM inference with Apptainer

These recipes build **separate** inference images. Model weights stay outside the
SIF so you can change models without rebuilding. Both servers expose an
OpenAI-compatible API. This is single-node, single-GPU serving, not distributed inference.

## Choose a backend

| Backend | Model format | Recommended starting point |
| --- | --- | --- |
| llama.cpp | GGUF, usually quantized | Iris V100 (16/32 GB), modest concurrency |
| vLLM | Hugging Face model directory | Iris H100 (`hopper` partition), batched/high-throughput serving |

Start with a small instruction model (e.g. 7–8B, Q4 GGUF for llama.cpp).
Weights **plus** KV cache and runtime buffers must fit in GPU memory. Context
length and concurrent requests affect memory usage. Not every architecture or
quantization format is supported by every backend/version.

The recipes pin example versions, not necessarily the latest releases:
llama.cpp `b5046` and vLLM `v0.11.0`. Check model compatibility before building;
newer models may require a newer backend. For strict reproducibility, also pin
base images by digest and llama.cpp by commit rather than relying on mutable tags.

### Check the allocated node first

On Iris, request a V100 interactive allocation with `si-gpu -G1 -c7`, then run:

```bash
nvidia-smi
module load tools/Apptainer
```

For H100, use the `hopper` partition with the appropriate allocation/QoS for your
account. Do not load modules or run inference on login nodes.

The llama.cpp recipe uses CUDA 12.4 and explicitly compiles for V100 (`sm_70`)
and H100 (`sm_90`); no GPU is needed during compilation. The vLLM recipe inherits
CUDA/PyTorch from its upstream image and targets H100, **not V100**. Check its
[upstream requirements](https://docs.vllm.ai/en/v0.11.0/getting_started/installation/gpu.html)
against the node driver before using it.

Containers do not upgrade the host NVIDIA driver. The CUDA version shown by
`nvidia-smi` describes driver support, not an installed container toolkit.
`--nv` is required at runtime. If the host driver is too old, select a compatible
CUDA/backend version or ask the administrators; do not install a driver in the image.

## Build the SIF image

From this directory on a **local Linux x86-64 machine** with Apptainer and root
access (not the cluster login node):

```bash
sudo apptainer build llama-cpp.sif llama-cpp.def
# Alternatively, for H100 serving:
sudo apptainer build vllm.sif vllm.def
```

The build requires internet access and several GB of free disk space. The
llama.cpp image deliberately retains the CUDA development toolkit for simplicity
and is larger than a runtime-only image. Its build uses four CPU workers.
`--fakeroot` is an alternative only where user namespaces/subuid configuration
permit it; do not assume this is enabled on UL HPC.

Transfer the selected SIF to your project/work storage using the UL HPC
[data-transfer guidance](https://hpc-docs.uni.lu/data/transfer/). Images are generated build
artifacts, not files to commit to this repository.

## Prepare model files and writable cache

Download weights **before submitting the serving job**; compute nodes may not
have internet access. Respect the model license and accept gated-model terms
where required. Keep access tokens outside images, scripts and logs.

- **llama.cpp:** download a supported `.gguf` file, e.g.
  `/absolute/path/models/model-Q4_K_M.gguf`. For split GGUFs, keep all shards in
  that directory and pass the first shard.
- **vLLM:** download a complete Hugging Face snapshot to a directory, e.g.
  `/absolute/path/models/my-model` (config, tokenizer and all weight shards).
  Avoid symlinks to files outside the bound models directory, or bind their
  targets too. Do not enable `--trust-remote-code` unless you have reviewed and
  trust the model's code.
- Create a writable cache on project/work storage, e.g.
  `/absolute/path/llm-cache`. Prefer a separate cache for each job if running
  concurrent servers. vLLM may compile/cache kernels at startup.

## Run a one-shot query (no server)

The image already includes `llama-cli`; no rebuild is needed. Submit an
instruction/chat model with an embedded chat template, such as Qwen2.5 Instruct:

```bash
sbatch query.sbatch \
  /absolute/path/llama-cpp.sif \
  /absolute/path/models/qwen2.5-7b-instruct-q4_k_m-00001-of-00002.gguf \
  'Explain in two sentences what a GPU does.'
```

Use the actual downloaded filename. For a split GGUF, keep all shards in the
same directory and pass the first shard. The job generates at most 128 tokens,
logs the prompt, answer and diagnostics to `llm-query-JOBID.out` in the submission
directory, then exits automatically. No cache path, API server or SSH tunnel is
needed. Prompt text appears in the log, so do not include secrets.

Extra `llama-cli` options can follow the prompt, e.g. `--n-predict 256`.
The default uses one GPU, context length 4096 and greedy decoding (`--temp 0`).
The CLI applies the model's chat template using `--conversation --single-turn`.
For a base/completion model, append `--no-conversation` instead.

Inspect the output with `less llm-query-JOBID.out`. Check CUDA detection and the
reported number of offloaded layers, not just whether an answer was produced.
A final `Completed successfully` line means the CLI exited successfully, not
that GPU use or answer quality has been independently verified. A larger GPU
request can be made with `sbatch --gpus-per-task=4 --cpus-per-task=28 query.sbatch
... --split-mode layer --tensor-split 1,1,1,1` if needed.

## Submit the server

Use **absolute paths visible on the compute node**. Replace every example path.
From this directory:

```bash
# One V100; the default partition is gpu.
sbatch serve.sbatch llama-cpp \
  /absolute/path/llama-cpp.sif \
  /absolute/path/models/model-Q4_K_M.gguf \
  /absolute/path/llm-cache

# One H100; override the default partition.
sbatch --partition=hopper serve.sbatch vllm \
  /absolute/path/vllm.sif \
  /absolute/path/models/my-model \
  /absolute/path/llm-cache
```

Add `--account=YOUR_PROJECT` before `serve.sbatch` if required. Adjust CPU/memory,
wall time and QoS for your allocation and current cluster policy. Extra backend
options can be appended after the cache path. The defaults use context length
4096 and one GPU. For llama.cpp, lower `--n-gpu-layers` or `--ctx-size` if you run
out of VRAM; for vLLM, reduce `--max-model-len`/concurrency or use a smaller model.
CPU offload is possible in llama.cpp but can substantially slow inference.

The launcher uses `srun`, `--nv`, a read-only model bind, writable `/cache`,
`--cleanenv`, and disables the automatic home bind to avoid host Python packages
contaminating vLLM. It preserves Slurm's `CUDA_VISIBLE_DEVICES`; do not set GPU IDs
manually. vLLM downloads are disabled so an incomplete local model fails rather
than unexpectedly fetching weights. Do not add `--containall` without considering
shared-memory requirements for PyTorch/vLLM.

## Connect and test

The job log (`llm-server-JOBID.out`) gives the compute hostname. Both servers bind
**only to loopback** and use API model name `local-model`. Wait for startup/model
loading to finish, then, if cluster policy allows SSH to your allocated node,
forward a local port from your workstation:

```bash
ssh -J USER@ACCESS_HOST -N -L 8000:127.0.0.1:8000 USER@COMPUTE_HOST
```

Replace the user and hostnames with your actual cluster access host and allocated
compute node. If compute-node SSH is disallowed, use the site's approved tunneling
method or test from inside the allocation. Do not expose an unauthenticated
server with `--host 0.0.0.0` on the cluster network.

In another workstation terminal:

```bash
curl http://127.0.0.1:8000/v1/models
curl http://127.0.0.1:8000/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"model":"local-model","messages":[{"role":"user","content":"Hello!"}],"max_tokens":64}'
```

Use an instruction/chat model with an appropriate chat template for the chat
endpoint. Check the server log for CUDA detection and actual GPU offload;
`nvidia-smi` alone does not prove model inference uses the GPU. Cancel the job
with `scancel JOBID` when finished.

## Validation status

The `%test` sections are structural build checks only. They do **not** validate
GPU inference. These recipes must still be built and smoke-tested on the intended
node with its actual NVIDIA driver and your chosen model.
