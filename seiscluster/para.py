from os.path import expanduser
import configparser


class SCPara(object):
    def __init__(self):
        # FileIO
        self.data_path = expanduser('~')
        self.cluster_result_path = expanduser('~')
        self.Suffix = '.sac'
        # para
        self.metric = 'DTW'  # and cc
        self.tmarker = 't7'
        self.wp = [-5,5]
        self.coef_threshold = 0.4
        self.nw = 2   #
        self.onlydata = 'no'   #

    def get_par(cfg_file):
        scpara = SCPara()
        cf = configparser.ConfigParser()
        try:
            cf.read(cfg_file)
        except Exception:
            raise FileNotFoundError('Cannot open configure file %s' % cfg_file)

        # Read and set properties from the configuration file
        # FileIO
        scpara.data_path = cf.get('FileIO', 'data_path', fallback=scpara.data_path)
        scpara.cluster_result_path = cf.get('FileIO', 'cluster_result_path', fallback=scpara.cluster_result_path)
        scpara.Suffix = cf.get('FileIO', 'Sac_File_Suffix', fallback=scpara.Suffix)
        scpara.onlydata = cf.get('FileIO', 'onlydata', fallback=scpara.onlydata)
        # Parameters
        scpara.metric = cf.get('Parameters', 'metric', fallback=scpara.metric)
        tmarker_str = cf.get('Parameters', 'tmarker', fallback=','.join(scpara.tmarker))
        scpara.tmarker = [tm.strip() for tm in tmarker_str.split(',')] if tmarker_str else scpara.tmarker
        scpara.wp = [float(x) for x in cf.get('Parameters', 'wp', fallback=f"{scpara.wp[0]},{scpara.wp[1]}").split(',')]
        scpara.coef_threshold = cf.getfloat('Parameters', 'coef_threshold', fallback=scpara.coef_threshold)
        scpara.nw = cf.getint('Parameters', 'nw', fallback=scpara.nw)

        return scpara

