import os
from .function import *
from .plt import Elbowplt,dendrogramplt
from dtaidistance import clustering, dtw
from scipy.cluster.hierarchy import linkage, fcluster, leaves_list


def cluster_saclst(sac_lst, tree_lst, cluster_df):
    """
    get saclst(df) after clustering
    :param sac_lst:
    :param tree_lst:
    :param cluster_df:
    :return:
    """
    clst = sac_lst.reindex(tree_lst)
    tlst = clst.reset_index(drop=True)
    nclst = pd.merge(tlst, cluster_df, on='number', how='right')
    return nclst


def cluster_nn(Z, threshold, labels):
    """
    get cluster number and name
    :param Z:
    :param threshold:
    :param labels:
    :return:
    """
    lbnp = np.array(labels)
    max_d = threshold
    # <class 'numpy.ndarray'> (160,)
    clusters = fcluster(Z, max_d, criterion='distance')
    #
    df = pd.DataFrame({'number': lbnp, 'clustern': clusters})
    #
    trlst = leaves_list(Z)
    ndf = df.reindex(trlst)
    return ndf



def cluster(ds, method):
    """
    method = single ds = datas  Z[3] = 0  imperfection
    method = ward ds = ds       Z[3] √
    """
    if method == 'single':
        model1 = clustering.Hierarchical(dtw.distance_matrix_fast, {})
        cluster_idx = model1.fit(ds.values)  # 字典
        model2 = clustering.HierarchicalTree(model1)
        cluster_idx = model2.fit(ds.values)
        l = len(model2.linkage)
        Z_ori = np.array(model2.linkage)  # list -> np  ?[3] = 0
        Z = Z_ori.reshape((l, 4))
        pass

    if method == 'ward':
        # trids = np.triu(ds,k=1)  # 上三角矩阵
        trids = ds[np.triu_indices(len(ds), k=1)]  # 获取距离矩阵的对角线以上部分
        #dimensionality = len(trids) * len(trids)  # 一维数组的维度
        # 转化为距离数组distance_matrix 格式为 上三角矩阵的 0 1 2 3 4 5
        #dsm = trids.reshape((dimensionality,))
        #dsm_index = np.nonzero(dsm)  # 非零元素的索引
        #dsm_last = dsm[dsm_index]  # 最终程序所需的一维距离数组
        # <class 'numpy.ndarray'>  [ len(z) - 1  * 4 ]
        Z = linkage(trids, 'ward')

    return Z



def wave_cluster(evt_path, mtr, sac_df, outpath):
    """
    wave cluster base dtw distance matrix
    :param outpath:
    :param mtr:
    :param sac_df:
    :return:
    """
    orid = mtr.values
    labels = mtr.index
    Z = cluster(orid , 'ward')
    trelst = leaves_list(Z)  # tree
    evt = os.path.basename(os.path.normpath(evt_path))
    picpath = os.path.join(outpath, 'picture')
    # pic path
    if not os.path.exists(picpath):
        os.makedirs(picpath)
    # plot Elbow
    threshold = Elbowplt(Z, evt ,outpath = picpath,pictype = 'pdf')
    thlstpath = os.path.join(outpath,"threshold.lst")
    with open(thlstpath, "a") as file:
        file.write(f"evt:{evt} Cluster threshold = {threshold}\n")
    print(f"evt:{evt} Cluster threshold =  {threshold}")

    # plot dendrogram
    dendrogramplt(Z, labels, evt, threshold,outpath = picpath,pictype='pdf',noxticks=True)
    # cluster nb and cluster_n
    cls_df = cluster_nn(Z, threshold, labels)
    # df after clustering
    cl_sac_df = cluster_saclst(sac_df, trelst, cls_df)
    # save tree_list and index_list
    indexlst = np.array(cl_sac_df['clustern'])
    lstpath = os.path.join(outpath,'pkl')
    np.save(os.path.join(lstpath, evt + 'trelst.npy'), trelst)
    np.save(os.path.join(lstpath, evt +'indexlst.npy'), indexlst)
    # mtr sort by cluster tree_lst
    mtr_sort = sorted_ds_pd(mtr ,trelst)
    mtr_sort.to_pickle(os.path.join(lstpath, evt +'cls_mtr.pkl'))
    # mtr_cluster_n = mtr_idx(mtr_sort.values, indexlst)
    # save sac_df after clustering
    cl_sac_df.to_pickle(os.path.join(lstpath, evt +'cls_df.pkl'))
