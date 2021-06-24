## Repo under construction. Coming June 2021

# Measuring and predicting variation in the interestingness of physical structures
[Cogsci 2021 paper](https://github.com/cogtoolslab/curiotower_CogSci2021/blob/master/CogSci2021_final_submission.pdf)
<p align="center">
  <img align = 'center' src="https://github.com/cogtoolslab/curiotower_CogSci2021/blob/master/stimuli/curiotower_4_high_0005_1.png" width="20%" height="20%">
  <img align = 'center' src="https://github.com/cogtoolslab/curiotower_CogSci2021/blob/master/stimuli/curiotower_8_high_0000_0.png" width="20%" height="20%">
</p>


## What makes a tower interesting?
What features of a physical scene make it interesting? In this project we explore both open-ended building behavior in kids, as well as adult ratings of pre-built towers. We find that _interestingness_ is a surprisingly reliable measure between subjects, and that physical configurations that violate expectations are considered more interesting.

## Project Overview:
_Where can I find things?_

The repo is divided into three main sections: 
1. ``/stimuli/`` where you can find scripts for generating or viewing the stimuli from the two experiments
2. `/experiments/` where you can find code used for running the two web-based rating tasks
3. `/analysis/` where you can find our scripts for analysis and results.

There are also two additional directories: `models` and `utils` which provide auxiliary support. 


#### Experiment 1: What towers do children choose to build?
<p align="center">
<img align = 'center' src="https://github.com/cogtoolslab/curiotower_CogSci2021/blob/master/stimuli/cooltower_example.jpeg" width="20%" height="20%">
 <img align = 'center' src="https://github.com/cogtoolslab/curiotower_CogSci2021/blob/master/stimuli/121319_03.png" width="20%" height="20%">
 </p>

In this experiment we gave 53 children a set of 9 primitve plastic blocks and asked them to construct a "cool tower". We documented the towers and then asked adults to rate the towers on a scale from 1-5 on how interesting they were. Our key finding was that taller towers were considered more interesting.

`stimuli` We gave each of the kids a set of 9 preimitive plastic blocks and instructions to "build a cool tower". [link to all towers](https://github.com/langcog/curiobaby_drop/tree/master/coolTower)

`analysis` The script generating the dataframe consisting of adult ratings of the child-built towers can be found [here](https://github.com/cogtoolslab/curiotower_CogSci2021/blob/master/analysis/evalTower-cooltower.ipynb).
And you can find the script for generating the key figure [here](https://github.com/cogtoolslab/curiotower_CogSci2021/blob/master/analysis/curiotower_figs.R)

#### Experiment 2: What features of a physical scene make it interesting?
<p align="center">
  <img align = 'center' src="https://github.com/cogtoolslab/curiotower_CogSci2021/blob/master/stimuli/curiotower_4_high_0005_1.png" width="20%" height="20%">
  <img align = 'center' src="https://github.com/cogtoolslab/curiotower_CogSci2021/blob/master/stimuli/curiotower_8_high_0000_0.png" width="20%" height="20%">
</p>

In this experiment we procedurally generated towers using the TDW physics environment. We specififcally varied the height (2,4,8 blocks) and the jitter in the x position (low, med, high jitter). We created 72 towers, rendered from two different viewpoints for a total of 144 towers. 

`stimuli` In the second experiment, we procedurally generated towers using the [tdw_physics](https://github.com/cogtoolslab/tdw_physics) virtual 3d physics environment

`analysis` 
- The script for the [model comparisons](https://github.com/cogtoolslab/curiotower_CogSci2021/blob/master/analysis/curiotower_lme_analysis.R) in the paper 
- Generate key [figures](https://github.com/cogtoolslab/curiotower_CogSci2021/blob/master/analysis/curiotower_figs.R)
- We also include aditional supplemental analyses for the [split-halves reliability](https://github.com/cogtoolslab/curiotower_CogSci2021/blob/master/analysis/Split-halves%20analysis.ipynb) and [correlation](https://github.com/cogtoolslab/curiotower_CogSci2021/blob/master/analysis/Stability-Interesting%20Correlation.ipynb) we conducted while exploring the relationship between interestingness and stability  

