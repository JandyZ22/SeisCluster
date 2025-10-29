from .function import dfuni
import pandas as pd
import shutil
import os


def pick_waves_df_byCC(df, coef_threshold):
    """
    rm waves <= min_CC
    """
    pick_df_byCC = pd.DataFrame()
    for i in dfuni(df, col='clustern'):
        df_subset = df[df['clustern'] == i]
        filtered_df = df_subset[df_subset['corr'] >= coef_threshold]
        pick_df_byCC = pd.concat([pick_df_byCC, filtered_df])
        pass

    return pick_df_byCC


def pick_waves_df_bycount(df, nw):
    """
    rm waves < nw
    """
    pick_df_bycount = pd.DataFrame()
    for i in dfuni(df, col='clustern'):
        df_subset = df[df['clustern'] == i]
        count = df_subset['clustern'].value_counts()
        nb = count[count > nw]
        # clc = clc + len(nb)
        filtered_df = df_subset[df_subset['clustern'].isin(nb.index)]
        pick_df_bycount = pd.concat([pick_df_bycount, filtered_df])
        pass

    return pick_df_bycount

def getlow_bound_df(df):
    cluster = df['clustern']
    unique_clusterns = cluster.unique()
    lowb_df = pd.DataFrame()
    for clustern in unique_clusterns:
        df_n = df[df['clustern']==clustern]
        Q1 = df_n['corr'].quantile(0.25)
        Q3 = df_n['corr'].quantile(0.75)
        IQR = Q3 - Q1
        low_bound = Q1 - 1.5 * IQR
        df_n['low_bound'] = low_bound
        lowb_df = pd.concat([lowb_df, df_n])
    return lowb_df


def rm_outliers(df,column_name='corr'):
    cluster = df['clustern']
    unique_clusterns = cluster.unique()
    lrmout_df = pd.DataFrame()
    for clustern in unique_clusterns:
        df_n = df[df['clustern'] == clustern]
        Q1 = df_n[column_name].quantile(0.25)
        Q3 = df_n[column_name].quantile(0.75)
        IQR = Q3 - Q1
        low_bound = Q1 - 1.5 * IQR
        # up_bound = Q3 + 1.5 * IQR
        # rmout_df = df_n[(df_n[column_name] >= low_bound) & (df_n[column_name]<= up_bound)]
        rmout_df = df_n[(df_n[column_name] >= low_bound)]
        lrmout_df = pd.concat([lrmout_df, rmout_df])
    return lrmout_df


def pickdf(coef_df, coef_threshold, nw):
    lrmout_df = rm_outliers(coef_df)
    pick_df_byCC = pick_waves_df_byCC(lrmout_df, coef_threshold)
    pick_df_bycount = pick_waves_df_bycount(pick_df_byCC, nw)
    return pick_df_bycount


def mvsac(datapath, outpath, saclst_df):
    df = saclst_df['sacn']
    for sacn in df:
        sac_file = os.path.join(datapath, str(sacn))
        out_file = os.path.join(outpath,  str(sacn))
        shutil.copy(sac_file, out_file)



def pickwaves(pickdf,inputpath,outpath,evt):
    """
    Pick waves for seiscluster's result
    :param pickdf:
    :param inputpath:
    :param outpath:
    :param evt:
    :return:
    --pick
      --all -- x1.sac
            ...
            -- x??.sac
      --cluster
            -- cluster_1 -- x??.sac
                         ...
                         -- x??.sac
            ...
            -- cluster_? -- x??.sac
                         ...
                         -- x??.sac
    """
    evt_outpath = os.path.join(outpath, evt)
    allsac_outpath = os.path.join(evt_outpath, 'all')
    os.makedirs(allsac_outpath, exist_ok=True)
    for cluster_n in pickdf['clustern'].unique():
        sub_pickdf = pickdf[pickdf['clustern'] == cluster_n]
        cluster_outpath = os.path.join(evt_outpath,'cluster')
        aimpath = os.path.join(cluster_outpath,'cluster_' + str(cluster_n))
        os.makedirs(aimpath, exist_ok=True)
        # mv sac to all(folder)
        mvsac(inputpath, allsac_outpath, sub_pickdf)
        # mv sac to cluster(folder)\cluster_n(folder)\
        mvsac(inputpath, aimpath, sub_pickdf)


def mkdir_waves(pdf, inputpath, outpath, evt):
    for c1 in pdf['clustern'].unique():
        subdf = pdf[pdf['clustern'] == c1]
        aimpath = outpath + evt
        os.makedirs(aimpath, exist_ok=True)
        mvsac(inputpath, aimpath, subdf)
