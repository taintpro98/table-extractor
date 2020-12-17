# Table Extraction Research
-------------


## Maintainer

@bruno

### Step-by-step installation

```bash
#dump environment to a file by running this script
conda env export | grep -v "^prefix: " > environment.yml


# install conda environment by running this script 
conda env create -f environment.yml

# follow PyTorch installation in https://pytorch.org/get-started/locally/
# we give the instructions for CUDA 9.2
conda install pytorch==1.2.0 torchvision==0.4.0 cudatoolkit=9.2 -c pytorch
```