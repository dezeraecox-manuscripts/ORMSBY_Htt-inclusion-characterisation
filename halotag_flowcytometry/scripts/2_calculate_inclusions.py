import os
import re
import string
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.lines import Line2D

from loguru import logger
from GEN_Utils import FileHandling

logger.info('Import OK')

input_path = 'halotag_flowcytometry/initial_cleanup/cleaned_summary.xlsx'
output_folder = 'halotag_flowcytometry/calculate_inclusions/'

if not os.path.exists(output_folder):
    os.mkdir(output_folder)


def inclusion_proportion_calculator(df, bin_col, count_col, inclusion_type=1):
    # Count number of i and ni cells in each bin,
    count = df.groupby([bin_col, 'inclusion']).count().reset_index()

    inc_count = count[count['inclusion'] == inclusion_type]
    inc_map = dict(zip(inc_count[bin_col], inc_count[count_col]))

    proportion = count[count['inclusion'] != inclusion_type]
    proportion.rename(columns={count_col: 'ni_count'}, inplace=True)
    proportion['inc_count'] = proportion[bin_col].map(inc_map).fillna(0)

    proportion = proportion[[bin_col, 'ni_count', 'inc_count']]

    # Calculate % of i cells in each bin
    proportion['total_cells'] = proportion['inc_count'] + \
        proportion['ni_count']
    proportion['inc_percent'] = proportion['inc_count'] / \
        proportion['total_cells'] * 100

    return proportion


# Read in summary df
raw_compiled = pd.read_excel(input_path)
compiled = raw_compiled.copy()

# define some sample-specific information
cer_channel = '[405]450_50-A'
ht_channel = '[561]610_20-A'

# Check out the histograms of the Cer and HT
for tag, df in compiled.groupby('sample_name'):
    fig, ax = plt.subplots()
    sns.distplot(df[ht_channel], color='r')

# Generate list of bins for cer channel
# cer_bins = np.arange(0, 5000, 100)
# cer_bins = np.geomspace(start=100, stop=100000, num=10, endpoint=True, dtype=None, axis=0)
cer_bins = np.logspace(start=0, stop=3.77815125038, num=20,
                       endpoint=True, base=10.0, dtype=None, axis=0)
cer_bin_mapper = dict(zip(np.arange(0, 20, 1), cer_bins))


# Assign bins to df
compiled['cer_bin'] = np.digitize(compiled[cer_channel], cer_bins)
# compiled.ht_bin.unique()

# calculate % of inclusions (ignoring HT inclusions)
inclusion_calcs = []
for sample, df in compiled.groupby('sample_name'):
    count_df = df.dropna(subset=['inclusion'], axis=0)
    inclusions = inclusion_proportion_calculator(df=count_df, bin_col='cer_bin', count_col=ht_channel, inclusion_type=1)
    inclusions['sample_name'] = sample
    inclusion_calcs.append(inclusions)
# Add back sample info
inc_per_cer_total = pd.concat(inclusion_calcs)
inc_per_cer_total[['sample', 'replicate']] = inc_per_cer_total['sample_name'].str.split('_', expand=True)
inc_per_cer_total['cer_bin_start'] = inc_per_cer_total['cer_bin'].map(cer_bin_mapper)

# Repeat for each HT bin
raw_cells = []
# Cannot calulcate the min and max bins for the 25Q, 97Q with the new binning system, therefore exclude
# sample_ignore = ['B07', 'B08', 'B09', 'C07', 'C08', 'C09']
sample_list = []
for sample, df in compiled.groupby('sample_name'):
    # if sample not in sample_ignore:
    bin_width = (np.max(df[ht_channel]) - 100)/3
    # ht_bins = [np.min(df[ht_channel]), 100, 100+bin_width, 100+bin_width*2, np.max(df[ht_channel])+1]
    ht_bins = [np.min(df[ht_channel])] + list(np.logspace(start=2, stop=np.log10(np.max(df[ht_channel])), num=4, endpoint=True, base=10.0, dtype=None, axis=0))
    # replace final bin with max value of ht
    ht_bins.pop(-1)
    ht_bins.append(np.max(df[ht_channel])+1)

    # ht_bin_mapper = dict(zip(np.arange(0, 4, 1), ht_bins))
    df['ht_bin'] = np.digitize(df[ht_channel], ht_bins)
    raw_cells.append(df)

    for ht_bin, ht_df in df.groupby('ht_bin'):
        ht_bin
        count_df = ht_df.dropna(subset=['inclusion'], axis=0)
        inclusions = inclusion_proportion_calculator(df=count_df, bin_col='cer_bin', count_col=ht_channel, inclusion_type=1)
        inclusions['sample_name'] = sample
        inclusions['ht_bin'] = ht_bin

        sample_list.append(inclusions)
        # inclusion_calcs.append(pd.concat(sample_list))
    
# Add back sample info to inclusion df
inc_per_ht_cer_ht = pd.concat(sample_list) 
inc_per_ht_cer_ht[['sample', 'replicate']] = inc_per_ht_cer_ht['sample_name'].str.split('_', expand=True)
inc_per_ht_cer_ht['cer_bin_start'] = inc_per_ht_cer_ht['cer_bin'].map(cer_bin_mapper)

# Repair ht_binned raw_cells df with ht bins
ht_compiled = pd.concat(raw_cells)


# Save summary dfs
FileHandling.df_to_excel(data_frames=[ht_compiled, inc_per_cer_total, inc_per_ht_cer_ht], sheetnames=['binned_raw', 'total__binned_inclusions', 'ht_binned_inclusions'], output_path=f'{output_folder}summary_data.xlsx')
