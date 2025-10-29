import pandas as pd
import numpy as np
import os
from .function import dfuni

# coef_cal

def discorminator(ts):
    if len(ts) == 1:
        cor_m_lst = np.nan
    else:
        correlation_matrix = np.corrcoef(ts)
        masked_cmtr = np.ma.masked_equal(correlation_matrix, 1)
        cor_m_lst = np.mean(masked_cmtr, axis=1)
    return cor_m_lst



def cor_m(df):
    # cal coef
    #
    arr = df['data'].to_numpy()
    ts = np.vstack(arr, dtype=np.float64)
    cor_m_lst = discorminator(ts)
    coef_df = df.copy()
    coef_df['corr'] = cor_m_lst
    return coef_df


def coef_cal(evt_path, df, outpath):
    evt = os.path.basename(os.path.normpath(evt_path))
    new_df = pd.DataFrame()
    for i in dfuni(df, col='clustern'):
        df_subset = df[df['clustern'] == i]
        nc_df = cor_m(df_subset)
        new_df = pd.concat([new_df,nc_df])
        pass
    # save coef_cls_sac_df
    pkloutpath = os.path.join(outpath, 'pkl')
    new_df.to_pickle(os.path.join(pkloutpath, evt + 'coef_df.pkl'))
