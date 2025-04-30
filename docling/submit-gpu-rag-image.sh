#!/bin/bash
#SBATCH --account=project_2002820
#SBATCH --partition=gpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=10
#SBATCH --mem=250G
#SBATCH --time=02:00:00
#SBATCH --gres=gpu:v100:2,nvme:250
#SBATCH --output=rag-image-merged-output.txt
#SBATCH --error=rag-image-merged-error.txt

module load pytorch/2.0
export TORCH_CUDA_ARCH_LIST="7.0+PTX"

source venv-mrag/bin/activate

srun python3 docling_rag_image.py

deactivate