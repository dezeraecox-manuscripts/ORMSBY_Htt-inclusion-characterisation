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

input_path = 'halotag_flowcytometry/calculate_inclusions/summary_data.xlsx'
output_folder = 'halotag_flowcytometry/plotting/'

if not os.path.exists(output_folder):
    os.mkdir(output_folder)

# Read in summary_df from excel
raw_summary = pd.read_excel(input_path, sheet_name=None)

cer_channel = '[405]450_50-A'
ht_channel = '[561]610_20-A'

# Generate copy to plot from
inclusions = raw_summary['total__binned_inclusions'].copy()


# Plot expression level versus % inclusions
control_df = inclusions[inclusions['sample'] == '97Q+Ch']
for sample_name, sample_df in inclusions.groupby('sample'):
    fig, ax = plt.subplots()
    sns.lineplot(x='cer_bin_start', y='inc_percent', data=control_df, marker='o',
                 color='black', markeredgecolor=None, label='97Q_Cherry', ci='sd')
    sns.lineplot(x='cer_bin_start', y='inc_percent', data=sample_df, marker='o',
                 color='forestgreen', markeredgecolor=None, label=sample_name, ci='sd')
    # plt.legend(bbox_to_anchor=(1.05, 1.0))
    plt.ylim(-5, 105)
    plt.xlim(0, 2500)
    plt.legend(loc='upper left')
    plt.ylabel('Percentage of inclusions (%)')
    plt.xlabel('Cerulean Fluorescence Intensity (A.U.)')
    plt.tight_layout()
    plt.savefig(f'{output_folder}{sample_name}_inclusion_percentage.png')

# Add additional plot to plot on single graph
fig, ax = plt.subplots()
for sample_name, sample_df in inclusions.groupby('sample'):
    sns.lineplot(x='cer_bin_start', y='inc_percent', data=sample_df,
                 marker='o', markeredgecolor=None, label=sample_name, ci='sd')
plt.legend(loc='upper left', bbox_to_anchor=(1.05, 1.0))
plt.ylim(-5, 105)
plt.xlim(0, 2500)
plt.ylabel('Percentage of inclusions (%)')
plt.xlabel('Cerulean Fluorescence Intensity (A.U.)')
plt.tight_layout()
plt.savefig(f'{output_folder}inclusion_percentage_combined.png')

# # Create zoomed section
# fig, ax = plt.subplots()
# for sample_name, sample_df in inclusions.groupby('sample_name'):
#     if sample_name != '25Q':
#         sns.lineplot(x='cer_bin_start', y='i_percent', data=sample_df,
#                      marker='o', markeredgecolor=None, label=sample_name, ci='sd')
# plt.legend(loc='upper left', bbox_to_anchor=(1.05, 1.0))
# plt.ylim(-5, 40)
# plt.xlim(0, 1000)
# plt.ylabel('Percentage of cells with inclusions (%)')
# plt.xlabel('Cerulean Fluorescence Intensity (A.U.)')
# plt.tight_layout()
# plt.savefig(f'{output_folder}inclusion_percentage_combined_zoom.svg')

# Define colour palette for plotting ht_binned datasets
sns.palplot(sns.color_palette('bright'))
col_pal = [sns.color_palette('bright')[x] for x in [4, 0, 1, 3]]
sns.palplot(col_pal)

# Plot scatter plot for individual samples according to HaloTag bins
# Collect raw data for all cells and samples
binned = raw_summary['binned_raw']
sample_test = ['HSPB1_001', 'UPF1_002']

for sample, df in binned.groupby('sample_name'):
    # if sample in sample_test:
    fig, ax = plt.subplots()
    sns.scatterplot(x=cer_channel, y=ht_channel, data=df,
                    hue='ht_bin', palette=col_pal)  # , linewidth=0)
    plt.title(sample)
    labels = ['None', 'Low', 'Medium', 'High']
    legend_elements = []
    for x in range(0, 4):
        legend_elements.append(
            (Line2D([0], [0], marker='o', color=col_pal[x], label=labels[x], markersize=10)))
    plt.legend(handles=legend_elements, title='Halotag')
    plt.xlim(-50, 6000)
    plt.ylim(-5000, 120000)
    plt.tight_layout()
    plt.savefig(f'{output_folder}{sample}_scatterplot.svg')


# Plot expression level versus % inclusions in HaloTag bins
# Collect HaloTag dataset
ht_inclusions = raw_summary['ht_binned_inclusions'].copy()
sample_test = ['HSPB1', 'UPF1']


for sample_name, df in ht_inclusions.groupby('sample'):
    # if sample_name in sample_test:
    fig, ax = plt.subplots()
    sns.lineplot(x='cer_bin_start', y='inc_percent', data=df, marker='o',
                    hue='ht_bin', markeredgecolor=None, ci='sd', palette=col_pal)
    # plt.legend(bbox_to_anchor=(1.05, 1.0))
    plt.ylim(-5, 100)
    plt.xlim(-100, 4000)
    plt.ylabel('Percentage of inclusions (%)')
    plt.xlabel('Cerulean Fluorescence Intensity (A.U.)')
    plt.title(sample_name)
    handles, labels = ax.get_legend_handles_labels()
    plt.legend(handles, labels=['None', 'Low',
                                'Medium', 'High'], title='Halotag')
    plt.tight_layout()
    plt.savefig(
        f'{output_folder}{sample_name}_inclusion_percentage_ht.svg')
