import os.path
import matplotlib.pyplot as plt
import numpy as np
from scipy.cluster.hierarchy import dendrogram,fcluster
from .function import gettp,getthreholds
# from .cluster import matrix,sorted_ds_pd
# import seaborn as sns


def Elbowplt(Z, evt, outpath, pictype):
    """

    :param Z:
    :param evt:
    :param outpath:
    :param pictype:
    :return:
    """
    heightlst = Z[:, 2]
    heights = heightlst[::-1]
    cluster_counts = []
    for height in heights:
        labelst = fcluster(Z, height, criterion='distance')
        cluster_counts.append(len(np.unique(labelst)))
        pass
    cc = cluster_counts
    n_tp = gettp(heights, cc)
    tp_index = int(n_tp - 1)
    o_threholds = getthreholds(heights ,n_tp)
    threholds = o_threholds - 0.001
    """
    if o_threholds >= 2:
        # threholds = 2 
        threholds = o_threholds - 0.01
        pass
    else:
        threholds = o_threholds + 0.01
    """
    t_point_x = cc[tp_index]
    t_point_y = heights[tp_index]
    plt.figure()
    plt.axhline(y=t_point_y, linestyle='dashed', color='black' ,linewidth=0.8)
    plt.axvline(x=t_point_x, linestyle='dashed', color='black' ,linewidth=0.8)
    plt.scatter(cc, heights ,s=2)
    plt.scatter(t_point_x, t_point_y, color='red' ,s=10)  # t_point red
    plt.xlabel('Number of clusters')
    plt.ylabel('Distance')
    plt.title('evt:' + evt )
    # plt.title('the relation between the number of clusters and height')
    # plt.show()
    # save in output
    picpath = os.path.join(outpath, evt + '_cluster_Elbow.'+ pictype)
    plt.savefig(picpath, dpi=720)
    plt.close()
    plt.clf()

    return threholds



def dendrogramplt(Z, labels, evt, threshold, outpath, pictype, noxticks=True):
    """
    Plot a dendrogram by threshold (eblow method auto)
    :param Z:
    :param labels:
    :param evt:
    :param threshold:
    :param outpath:
    :param pictype:
    :param noxticks:
    :return:
    """
    plt.figure(figsize=(40, 18))
    dendrogram(Z, leaf_font_size=8, labels=labels, color_threshold=threshold)
    if noxticks==True:
        plt.xticks([])
    plt.axhline(y=threshold, linestyle='dashed', color='black',linewidth=0.8)
    picpath = os.path.join(outpath, evt + '_cluster_dendrogram.'+ pictype)
    plt.savefig(picpath, dpi=720)
    plt.axis('auto')
    plt.close()
    plt.clf()