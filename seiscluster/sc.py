import os
import pandas as pd
from .function import pkl_read
from .check_data import check_data
from .dis_matrix_cal import matrix_cal
from .cluster import wave_cluster
from .para import SCPara
from .coef_cal import coef_cal
from .pick import pickdf,pickwaves
from tqdm import tqdm


def seiscluster(par_path):
    scpar = SCPara.get_par(par_path)
    # para
    metric = scpar.metric
    wp = scpar.wp
    tmarker = scpar.tmarker
    # File path
    data_path = scpar.data_path
    out_path = scpar.cluster_result_path
    Suffix = scpar.Suffix
    onlydata = scpar.onlydata
    #"""
    all_items = sorted(os.listdir(data_path))
    # Keep only entries that are folders
    evt_lst = [item for item in all_items if os.path.isdir(os.path.join(data_path, item))]
    for evt in tqdm(evt_lst):
        evt_wave_path = os.path.join(data_path, evt)
        wave_nb_in_evt = len(os.listdir(evt_wave_path))
        if wave_nb_in_evt <= 2:
            print(f'evt:{evt} only {wave_nb_in_evt} wave(s) ,no cluster!')
        else:
            # check data
            check_data(evt_wave_path,Suffix)

            # cal matrix
            matrix_cal(evt_wave_path,Suffix,metric,wp,tmarker,out_path,onlydata)
            # cluster
            pkloutpath = os.path.join(out_path,'pkl')
            mtr = pkl_read(pkloutpath, evt + 'mtr')
            sac_df = pkl_read(pkloutpath, evt + 'df')
            wave_cluster(evt_wave_path, mtr, sac_df, out_path)
            # coef_cal (cc)
            cls_sac_df = pkl_read(pkloutpath, evt + 'cls_df')
            coef_cal(evt_wave_path, cls_sac_df, out_path)


def pick_by_cluster(par_path,no_criterion=False,output_mod='sac'):
    scpar = SCPara.get_par(par_path)
    # setting in cfg
    coef_threshold = scpar.coef_threshold
    nw = scpar.nw
    # File Path
    data_path = scpar.data_path
    out_path = scpar.cluster_result_path
    #
    pick_resultpath = os.path.join(out_path,'pick')
    all_items = sorted(os.listdir(data_path))
    # Keep only entries that are folders
    evt_lst = [item for item in all_items if os.path.isdir(os.path.join(data_path, item))]
    pick_df = pd.DataFrame()
    for evt in tqdm(evt_lst):
        evt_wave_path = os.path.join(data_path, evt)
        wave_nb_in_evt = len(os.listdir(evt_wave_path))
        if wave_nb_in_evt <= 2:
            print(f'evt:{evt} only {wave_nb_in_evt} wave(s) ,no cluster!')
        else:
            pkloutpath = os.path.join(out_path, 'pkl')
            coefdf = pkl_read(pkloutpath, evt + 'coef_df')
            if no_criterion:
                pdf = coefdf
                if output_mod == 'sac':
                # Save the clustering results as a sac file
                    if not pdf.empty:
                        pickwaves(pdf,evt_wave_path,pick_resultpath,evt)
                elif output_mod == 'df':
                    if not pdf.empty:
                        pdf_copy = pdf.copy()
                        pdf_copy['event'] = evt
                        pick_df = pd.concat([pick_df, pdf_copy])
                        # Save the clustering results all evt (.pkl)
                        last_df_path = os.path.join(out_path, 'Allevt_sc_df.pkl')
                        pick_df.to_pickle(last_df_path)
                else:
                    print(f'Unknown output mode: {output_mod},output_mod only have sac(default) or df.')
                pass
            else:
                pdf = pickdf(coefdf, coef_threshold, nw)
                if output_mod == 'sac':
                # Save the clustering results as a sac file
                    if not pdf.empty:
                        pickwaves(pdf,evt_wave_path,pick_resultpath,evt)
                elif output_mod == 'df':
                    if not pdf.empty:
                        pdf_copy = pdf.copy()
                        pdf_copy['event'] = evt
                        pick_df = pd.concat([pick_df, pdf_copy])
                        # Save the clustering results all evt (.pkl)
                        last_df_path = os.path.join(out_path, 'Allevt_sc_df.pkl')
                        pick_df.to_pickle(last_df_path)
                else:
                    print(f'Unknown output mode: {output_mod},output_mod only have sac(default) or df.')