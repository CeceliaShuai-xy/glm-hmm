# glm-hmm
Revised version of Ashwood et al. code to adapt to fit mice behavioral data from Touchscreen Attentional Task (You & Mysore, 2020) with
GLM-HMM. The original version of the code reproduces figures in ["Mice alternate between discrete strategies
 during perceptual decision-making"](https://www.biorxiv.org/content/10.1101/2020.10.19.346353v4.full.pdf) from Ashwood, Roy, Stone, IBL, Urai, Churchland, Pouget and Pillow (2020).  Note: while this code reproduces the figures/analyses for our paper, the easiest way to get started applying the GLM-HMM to your own data, is with [this notebook](https://github.com/zashwood/ssm/blob/master/notebooks/2b%20Input%20Driven%20Observations%20(GLM-HMM).ipynb). This repository revised the code mentioned above to suit the specific behavioral task of interest and it should be run in the following order:

Code is ordered so that the IBL dataset discussed in the paper is
 preprocessed into the
 desired
 format by (1) a Matlab script "preprocess_v3" (most updated version), which extracts the desrived test-related variables
 and saves in the corresponding data folders. Then (2) user should run
 the scripts in "1_preprocess_data". Within this directory, run the scripts
  in the order indicated by the number at the beginning of the file name (i.e
  . run
   "1_get_data.py" first to obtain the
   data saved in the data folder and then run "2_create_design_mat.py" to obtain the design
    matrix used as input for all of the models). Next
    , you can fit the GLM, lapse and GLM-HMM models discussed in the paper using
      the code contained in "2_fit_models".  (3) The
       GLM should be run first as the GLM fit is used to initialize the
        global GLM-HMM (the model that is fit with data from all animals). (4) The
           lapse model fits, while not used for any initialization purposes, should be run next so as to be able to perform model comparison with the global and individual GLM-HMMs. (5) The
         global GLM-HMM should be run next, as it is used to initialize the
          models for all individual animals.  Finally GLM-HMMs can
           be fit to the data from individual animals using the code in the
            associated directory. With the trained  model, user can generate the graphs similar to Ashwood et al. by running scripts in 
            "2_make_figures". Note that this repository ONLY updated the code in folders "figure_2" and "figure_3", given how far the
            project proceeded. 

** Note that the path in the code should be changed accordingly.**

Before beginning, create a conda environment from the environment yaml file by running 
```
conda env create -f environment.yml
```
Note: this may take a while as ibllib relies on OpenCV, and installing
 this can take a while.  Activate this
 environment by running 
 ```
 conda activate glmhmm
```

We use version 0.0.1 of the Bayesian State Space Modeling framework from
 Scott Linderman's lab to perform GLM-HMM inference.  Within the `glmhmm
 ` environment, install the forked version of the `ssm` package available 
  [here](https://github.com/zashwood/ssm).  This is a lightly modified
   version of
   the
  master branch of the ssm package available at [https://github.com
  /lindermanlab/ssm](https://github.com/lindermanlab/ssm).  It is modified so as to handle violation trials as
   described in Section 4 of our manuscript.  In order to install this
    version of `ssm`, follow the instructions provided there, namely: 
    
```
cd ssm
pip install numpy cython
pip install -e .
```
