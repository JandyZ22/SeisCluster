from seiscluster.sc import seiscluster,pick_by_cluster
from seiscluster.function import pkl_read

# cluster
seiscluster('Sc.cfg')

# pick
pick_by_cluster('Sc.cfg')
# pick_by_cluster('Sc.cfg',no_criterion=True,output_mod='sac')  # figure 4a result

# pick mod = 'df', default mod = 'sac', default no_criterion= False
# pick_by_cluster('Sc.cfg',no_criterion=True,output_mod='sac')
# pick_by_cluster('Sc.cfg',no_criterion=True,output_mod='df')

# df_read
# path = 'E:\\workspace\\py\\testSC\\seiscluster\\example\\output\\'
# df = pkl_read(path,'Allevt_sc_df')
# print(df)
