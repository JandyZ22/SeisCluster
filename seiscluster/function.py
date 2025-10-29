import os
from obspy import read, Stream
import numpy as np
import pandas as pd
import subprocess
import pickle
from kneed import KneeLocator


def getwindow(tr,wp,tmarker):
    """
    get wp index
    :param tr:
    :param wp:
    :param tmarker:
    :return:
    """
    b = tr.stats.sac.b
    delta = tr.stats.delta
    if len(tmarker) == 1:
        t_n = tmarker[0]
        t_marker = getattr(tr.stats.sac, t_n, None)
        phase_index = int((t_marker - b) / delta)
        # Calculate window start and end times
        # start_time = t_marker + wp[0]  # t_marker + start_offset
        # end_time = t_marker + wp[1]  # t_marker + end_offset
        # idx
        start_idx = int(phase_index + (wp[0]/delta))
        end_idx = int(phase_index + (wp[1]/delta))
        return start_idx, end_idx
        # # Ensure indices are within the bounds of the trace data
        # start_idx = max(0, start_idx)
        # end_idx = min(len(tr.data) - 1, end_idx)
    elif len(tmarker) == 2:
        t_n1 = tmarker[0]
        t_n2 = tmarker[1]
        t_marker_1 = getattr(tr.stats.sac, t_n1, None)
        t_marker_2 = getattr(tr.stats.sac, t_n2, None)
        # Calculate window start and end times
        phase_index_1 = int((t_marker_1 - b) / delta)
        phase_index_2 = int((t_marker_2 - b) / delta)
        # Calculate window start and end times
        # start_time = t_marker + wp[0]  # t_marker + start_offset
        # end_time = t_marker + wp[1]  # t_marker + end_offset
        # idx
        start_idx = int(phase_index_1 + (wp[0]/delta))
        end_idx = int(phase_index_2 + (wp[1]/delta))

        # start_time = t_marker_1 + wp[0]  # t_marker + start_offset
        # end_time = t_marker_2 + wp[1]  # t_marker + end_offset
        # idx
        # start_idx = int((start_time - b) / delta)
        # end_idx = int((end_time - b) / delta)
        return start_idx, end_idx
    else:
        print("tmarker can only have 1 or 2, and t_N1<t_N2. please check your cfg file.")

def getflst(datapath):
    """
    get sacfile list
    """
    f_list = sorted(os.listdir(datapath))
    return f_list

def read_sac_files(directory, file_list,suffix):
    """

    :param directory:
    :param file_list:
    :param suffix:
    :return:
    """
    st = Stream()
    for filename in file_list:
        if filename.endswith(suffix):
            file_path = os.path.join(directory, filename)
            tr = read(file_path)
            st += tr
    return st



def saclst(stream, file_list,wp,tmarker,onlydata):
    """
    :param stream: st in evt
    :param file_list:
    :param data:
    :return:
    """
    st = stream
    waves_nb = len(st)
    if onlydata=='no':
        df = pd.DataFrame(index=range(waves_nb), columns=range(11))
        #
        if len(tmarker) == 1:
            for i in range(waves_nb):
                name = file_list[i]
                s_idx , e_idx = getwindow(st[i],wp,tmarker)
                data = st[i].data[s_idx:e_idx]   # single tmarker
                stla = st[i].stats.sac.stla
                stlo = st[i].stats.sac.stlo
                evla = st[i].stats.sac.evla
                evlo = st[i].stats.sac.evlo
                # tpla = st[i].stats.sac.user2
                # tplo = st[i].stats.sac.user1
                dep = st[i].stats.sac.evdp
                gcarc = st[i].stats.sac.gcarc
                baz = st[i].stats.sac.baz
                az = st[i].stats.sac.az
                nb = st[i].stats.sac.user9

                df.at[i, 0] = str(name)  # sacn
                df.at[i, 1] = np.array(data)  # data
                df.at[i, 2] = float(stla)  # evla
                df.at[i, 3] = float(stlo)  # evlo
                df.at[i, 4] = float(evla)  # evla
                df.at[i, 5] = float(evlo)  # evlo
                # df.at[i, 6] = float(tpla)         # tpla
                # df.at[i, 7] = float(tplo)         # tplo
                df.at[i, 6] = float(dep)  # dep
                df.at[i, 7] = float(gcarc)  # gcarc
                df.at[i, 8] = float(baz)  # baz
                df.at[i, 9] = float(az)  # az
                df.at[i, 10] = int(nb)  # number
        else:
            # two tmarker
            data_list = []  # The dynamic time window needs to be filled with zero
            max_length = 0
            for i in range(waves_nb): # First find the longest data slice
                s_idx, e_idx = getwindow(st[i], wp, tmarker)
                data = st[i].data[s_idx:e_idx]
                data_list.append(data)
                max_length = max(max_length, len(data))
                pass
            for i in range(waves_nb):
                name = file_list[i]
                data = data_list[i]
                stla = st[i].stats.sac.stla
                stlo = st[i].stats.sac.stlo
                evla = st[i].stats.sac.evla
                evlo = st[i].stats.sac.evlo
                # tpla = st[i].stats.sac.user2
                # tplo = st[i].stats.sac.user1
                dep = st[i].stats.sac.evdp
                gcarc = st[i].stats.sac.gcarc
                baz = st[i].stats.sac.baz
                az = st[i].stats.sac.az
                nb = st[i].stats.sac.user9
                length = len(data)
                # Calculate the number of zeros that need to be padded
                if length % 2 == 0:  # even number
                    pad_left = (max_length - length) // 2
                    pad_right = max_length - length - pad_left
                else:  # odd number
                    pad_left = (max_length - length) // 2
                    pad_right = max_length - length - pad_left

                # Fill with zeros
                padded_data = np.pad(data, (pad_left, pad_right), mode='constant')
                df.at[i, 0] = str(name)  # sacn
                df.at[i, 1] = padded_data  # data
                df.at[i, 2] = float(stla)  # evla
                df.at[i, 3] = float(stlo)  # evlo
                df.at[i, 4] = float(evla)  # evla
                df.at[i, 5] = float(evlo)  # evlo
                # df.at[i, 6] = float(tpla)         # tpla
                # df.at[i, 7] = float(tplo)         # tplo
                df.at[i, 6] = float(dep)  # dep
                df.at[i, 7] = float(gcarc)  # gcarc
                df.at[i, 8] = float(baz)  # baz
                df.at[i, 9] = float(az)  # az
                df.at[i, 10] = int(nb)  # number

        df.columns = ['sacn', 'data', 'stla','stlo', 'evla', 'evlo','dep', 'gcarc', 'baz', 'az' ,'number']

    elif onlydata =='yes':
        df = pd.DataFrame(index=range(waves_nb), columns=range(3))
        if len(tmarker) == 1:
            for i in range(waves_nb):
                name = file_list[i]
                s_idx , e_idx = getwindow(st[i],wp,tmarker)
                data = st[i].data[s_idx:e_idx]   # single tmarker
                nb = st[i].stats.sac.user9

                df.at[i, 0] = str(name)          # sacn
                df.at[i, 1] = np.array(data)      # data
                df.at[i, 2] = int(nb)             # number
        else:
            # two tmarker
            data_list = []  # The dynamic time window needs to be filled with zero
            max_length = 0
            for i in range(waves_nb): # First find the longest data slice
                s_idx, e_idx = getwindow(st[i], wp, tmarker)
                data = st[i].data[s_idx:e_idx]
                data_list.append(data)
                max_length = max(max_length, len(data))
                pass
            #
            for i in range(waves_nb):
                name = file_list[i]
                data = data_list[i]
                nb = st[i].stats.sac.user9
                length = len(data)
                # Calculate the number of zeros that need to be padded
                if length % 2 == 0:  # even number
                    pad_left = (max_length - length) // 2
                    pad_right = max_length - length - pad_left
                else:  # odd number
                    pad_left = (max_length - length) // 2
                    pad_right = max_length - length - pad_left

                # Fill with zeros
                padded_data = np.pad(data, (pad_left, pad_right), mode='constant')
                df.at[i, 0] = str(name)          # sacn
                df.at[i, 1] = padded_data        # data
                df.at[i, 2] = int(nb)            # number

        df.columns = ['sacn', 'data','number']
    else:
        print(f'{onlydata} Not a valid, check your cfg.')
    return df


# cluster

def pkl_read(path, name):
    """
    load pickle(df)
    :param path:
    :param name:
    :return:
    """
    abspath = os.path.join(path,name + '.pkl')
    with open(abspath, 'rb') as f:
        df = pickle.load(f)
    return df

def datas_pd(ts, labelst):
    datas = pd.DataFrame(ts, index=labelst)  # datas structure
    return datas


# mtr by cluster tree_lst
def sorted_ds_pd(sorted_ds, lst):
    """
    sort distance matrix by number(user9)
    :param sorted_ds:
    :param lst:
    :return:
    """
    sort_ds = sorted_ds.reindex(index=lst, columns=lst)
    return sort_ds

def mtr_idx(distances,indexlst):
    """
    get distance matrix bt cluster_n
    :param distances:
    :param indexlst:
    :return:
    """
    mtr = pd.DataFrame(distances, index=indexlst,columns=indexlst)
    return mtr



def dtwds_nb(distance_m, df):
    return datas_pd(distance_m, np.array(df['number']))




def gettp(v_lst, n_clst):
    """
    :param v_lst:
    :param n_clst:
    :return:
    """
    kl = KneeLocator(n_clst, v_lst, curve="convex", direction='decreasing')
    if kl.elbow is None:
        return int(1)
    else:
        return kl.elbow

def getthreholds(values_lst,klp):
    """

    :param values_lst:
    :param klp:
    :return:
    """
    index = klp - 1
    return values_lst[index]

def dfuni(df,col):
    """

    :param df:
    :param col:
    :return:
    """
    uni = df[col].unique()
    return uni


def nts(nts):
    max_len = max(len(arr) for arr in nts)
    padded_lst = []
    for arr in nts:
        # 计算需要在每边填充的0的数量
        padding = (max_len - len(arr)) // 2
        # 根据需要使用奇偶长度修正填充
        if (max_len - len(arr)) % 2 == 0:  # 长度差是偶数，两边填充相同数量的零
            padded_array = np.pad(arr, (padding, padding), 'constant', constant_values=0)
        else:  # 长度差是奇数，选择一边多填充一个零
            padded_array = np.pad(arr, (padding, padding + 1), 'constant', constant_values=0)
        padded_lst.append(padded_array)

    return np.array(padded_lst)