# SeisCluster

SeisCluster is a python package for waveform auto-identification using hierarchical clustering, especially for teleseismic waveforms with multi-seismic phases.

## Acknowledgements

For the use of the SeisCluster package, please cite as：

- Yandi Zeng, Xinlei Sun, Tao Yang, Haonan Chen, Hierarchical clustering using seismic waveform information: a strategy for automatic waveform identification, Geophysical Journal International, Volume 244, Issue 1, January 2026, ggaf437, https://doi.org/10.1093/gji/ggaf437

## Installation

Creating a virtual environment with `conda` is based on the `environment.yml` file.

   ```
   conda env create -f environment.yml
   ```

##  Contact information

- Yandi Zeng (Jandyz@stu.cdut.edu.cn)

The  GUI for waveform display is still under development, please contact me if you have any questions or suggestions about the code.

##  Usage

### input

- `cfg`  config file
```bash 
[FileIO]
# Path to data
data_path = /home/jandyz/workspace/testpython/seiscluster/example/data

# Output path to images and results
cluster_result_path = /home/jandyz/workspace/testpython/seiscluster/example/output

# sac_file_suffix
Sac_File_Suffix = .sac

# No redundant header, whether to read only the data from the sac file
onlydata = yes

[Parameters]
# metric  (default: metric =  DTW)
metric = cc # (Pearson correlation coefficients (p), with distance defined as 1 − p.)
# Window setting
# sac header (Theoretical arrival),
# or dynamic time window if two are set,
# e.g. tmarker = t1, t2 wp = -4, 8 , time window is [t1-4 , t2+8] (s)
tmarker = t2
wp = -40,20

# pick criteria
coef_threshold = 0.4
nw = 2
```
- `data` original data 
(1. The data format is SAC format.)
(2. Note that the  `delta` of data should be consistent here, and inconsistencies will be automatically resampled to a consistent delta.)
- The structure is as follows：
```
    data/
    ├── evt1
    │   ├── TA.A19A.2010.049.011319.BHE.sac
    │   ├── TA.A20A.2010.049.011319.BHE.sac
    │   │......
    ├── evt2
    │   ├── TA.109C.2008.105.094519.BHE.sac
    │   ├── TA.112C.2008.105.094519.BHE.sac
    │   │......
```
  In addition, the data will check whether there is a number in the header `user9`, and if not, it will be `automatically numbered` and written to the original data.

- `oneflow.py` 

  after configuring `cfg` file,  performs clustering (cluster) and waveforms identification (pick).
     ```
    python oneflow.py
     ```

### output
  There are two modes for waveform output:

- `mod = 'sac'`:  copy the original waveform and categorize it according to the clustering result.  # default

- `mod = 'df'`:  only the final waveform structure (DataFrame) is output.   # pandas.DataFrame

   no_criterion:

  - `no_criterion= False`:  Criteria for picking  need to be used  # default
  - `no_criterion= True`:  If you don't use the pick criterion, Output all clusters.  

```
    # mod = 'sac' (default)
    # pick results
    output/
    ├── pick
    │   ├── evt1              # evt1 
    	│   ├── all           # all pick sac files
    		│   ├── TA.A19A.2010.049.011319.BHE.sac
    		│   ├── ......
    	│   ├── cluster           # cluster sac files
    		│   ├── cluster_1
    			│   ├── TA.A19A.2010.049.011319.BHE.sac
    			│   ├── ......
    		│   ├── cluster_2
    		│   ├── ......
    │   │......
    # mod = 'df', no pick folder
    ├── Allevt_sc_df.pkl
    # cluster results
    ├── picture
    │   ├── evt1_cluster_dendrogram.pdf
    │   ├── evt1_cluster_Elbow.pdf
    │   │......
    ├── pkl
    │   ├── evt1cls_df.pkl            # df_after cluster
    │   ├── evt1cls_mtr.pkl           # distance matrix_after cluster
    │   ├── evt1coef_df.pkl           # coef_df
    │   ├── evt1df.pkl                # ori df
    │   ├── evt1mtr.pkl               # ori_distance matrix
    │   ├── evt1indexlst.npy          # indexlst
    │   ├── evt1trelst.npy            # tree_lst
    │   │......
    ├── threshold.lst                 # Dendrogram clipping thresholds for each event clustering 
```