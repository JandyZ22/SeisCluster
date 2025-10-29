import os
from .function import *
from dtaidistance import dtw
from dtaidistance import clustering
from scipy.cluster.hierarchy import linkage, fcluster, leaves_list, dendrogram
from scipy import stats



def matrix_cal(evt_path,Suffix,metric,wp,tmarker,outpath,onlydata):
    """

    :param evt_path:
    :param Suffix:  .sac
    :param metric:  DTW / cc   <class 'str'>
    :param wp: [-5.0, 5.0]   <class 'list'>
    :param tmaker: ['t1'] <class 'list'>  can input ['t1','t2']
    :return: The DTW distance matrix of the evtwave  (output path\pkl\)
    """
    evt = os.path.basename(os.path.normpath(evt_path))
    pklpath = os.path.join(outpath, 'pkl')
    if not os.path.exists(pklpath):
        os.makedirs(pklpath)
    #
    sacflst = getflst(evt_path)
    st = read_sac_files(evt_path, sacflst ,Suffix)
    sac_df = saclst(st,sacflst,wp=wp,tmarker=tmarker, onlydata=onlydata)
    arr = np.array(sac_df['data'])
    # get narr  # fulfill zero
    narr = nts(arr)
    #
    # save sac_df(ori) .pkl
    for i in range(narr.shape[0]):
        sac_df.loc[i, 'data'] = narr[i]
    sac_df_path =  os.path.join(pklpath, evt + 'df.pkl')
    sac_df.to_pickle(sac_df_path)
    #
    ts = np.vstack(narr,dtype=np.float64)
    if metric == 'DTW':
        dtwds = dtw.distance_matrix_fast(ts)
        dtwds_nb_pd = dtwds_nb(dtwds, sac_df)
        # save matrix for cluster  (.pkl)
        matrix_path = os.path.join(pklpath, evt + 'mtr.pkl')
        dtwds_nb_pd.to_pickle(matrix_path)
    elif metric == 'cc':
        ccds = 1 - np.corrcoef(ts)
        ccds_nb_pd = dtwds_nb(ccds, sac_df)
        matrix_path = os.path.join(pklpath, evt + 'mtr.pkl')
        ccds_nb_pd.to_pickle(matrix_path)