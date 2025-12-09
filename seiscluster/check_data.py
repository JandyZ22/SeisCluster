from .function import *
from collections import Counter
import shutil

def autonb(stream, sacflst,datapath):
    """
    Automatically assign incrementing numbers to the `user9` field of each Trace
    and write the updated Trace back to its SAC file.

    :param stream: ObsPy Stream object
    :param sacflst: List of SAC file paths corresponding to the Stream
    """
    for i, (tr, sac_file) in enumerate(zip(stream, sacflst)):

        coverpath = os.path.join(datapath, sac_file)
        tr.stats.sac.user9 = i  # 将 user9 设置为递增的数字
        # 将修改后的 Trace 写回到对应的 SAC 文件
        tr.write(coverpath, format='SAC')
    print("Successfully updated 'user9' for all traces.")


def auto_delta_consistent(st, sacflst, datapath):
    """
    Automatically resample Traces with less frequent delta values to match
    the most frequent delta value.

    :param st: ObsPy Stream object
    :param sacflst: List of SAC file paths corresponding to the Stream
    :param datapath: Path where SAC files are stored
    """
    # Step 1: Counting different delta values and their number
    delta_values = [tr.stats.delta for tr in st]  # 获取所有 delta 值
    delta_count = Counter(delta_values)  # 使用 Counter 统计每个 delta 的数量

    # print(f"Number of different delta values: {len(delta_count)}")
    # print("Counts of each delta value:")
    # for delta, count in delta_count.items():
    #     print(f"Delta value: {delta}, Count: {count}")

    # Step 2: Find the one with the most delta value as the target sampling rate
    target_delta, max_count = delta_count.most_common(1)[0]
    # print(f"Target delta value for resampling: {target_delta}, Count: {max_count}")

    # Step 3: Resampling of Trace for other delta values
    for i, tr in enumerate(st):
        if abs(tr.stats.delta - target_delta) > 1e-6:  # 只有 delta 不同的才需要重采样
            original_delta = tr.stats.delta
            print(f"Resampling Trace {i} from delta {original_delta} to {target_delta}")
            tr.interpolate(1.0 / target_delta, method='linear')  # Resampling using linear interpolation

            # 更新 SAC 文件
            coverpath = os.path.join(datapath, sacflst[i])
            tr.write(coverpath, format='SAC')

    print(f"Successfully resampled and updated all traces with inconsistent delta values{target_delta}.")


def check_data(datapath,suffix):
    """
    check data delta and user9
    :param datapath:evt_wave_path
    :return: bool
    """
    sacflst = getflst(datapath)
    st = read_sac_files(datapath, sacflst,suffix)
    # check Amplitude
    Amp_threshold = 3
    max_amps = np.array([np.max(np.abs(tr.data)) for tr in st])
    ref_amp = np.median(max_amps)  # 用中位数
    bad_idx = np.where(
    (max_amps > ref_amp * 10**Amp_threshold) |
    (max_amps < ref_amp / 10**Amp_threshold)
)[0]

    if len(bad_idx) > 0:
        parent_2_dir =  os.path.dirname(os.path.dirname(datapath))
        bad_dir = os.path.join(parent_2_dir, "BAD_Amplitude")
        if not os.path.exists(bad_dir):
            os.makedirs(bad_dir, exist_ok=True)

        print(f"Found {len(bad_idx)} abnormal traces ( > or < 10^{Amp_threshold} orders):")
        for idx in sorted(bad_idx, reverse=True):
            bad_file = sacflst[idx]
            src = os.path.join(datapath, bad_file)
            dst = os.path.join(bad_dir, bad_file)
            shutil.move(src, dst)
            st.remove(st[idx])
            sacflst.pop(idx)

        print("Abnormal Amplitude data moved to BAD_Amplitude")

    # check delta
    tolerance = 1e-6  # 设置一个容差范围
    delta_ref = st[0].stats.delta #
    # 检查所有 Trace 的 delta 是否一致
    all_equal = all(abs(tr.stats.delta - delta_ref) < tolerance for tr in st)
    if all_equal:
        print(f"The delta is the same for all Traces, with a value of: {delta_ref}")
        # check user9(number)
        for i, tr in enumerate(st):
            # if not hasattr(tr.stats.sac, 'user9'):
            if not hasattr(tr.stats.sac, 'user9') or not isinstance(tr.stats.sac.user9, (int, np.integer)):
                print(f"Trace {i} does not have a 'user9' header.")
                autonb(st,sacflst,datapath)
                print(f"Automatic numbering of all traces (user9)")
                break
        # check ready
        print(f"The data is ready. ")
    else:
        # delta auto resample
        auto_delta_consistent(st, sacflst, datapath)
        for i, tr in enumerate(st):
            if not hasattr(tr.stats.sac, 'user9') or not isinstance(tr.stats.sac.user9, (int, np.integer)):
                print(f"Trace {i} does not have a 'user9' header.")
                autonb(st,sacflst,datapath)
                print(f"Automatic numbering of all traces (user9)")
                break
        # check ready
        print(f"The data is ready. ")
        pass