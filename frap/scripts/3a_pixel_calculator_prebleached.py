import os, re
import glob
import numpy as np


import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from GEN_Utils import FileHandling
from frap.scripts.analysis_scripts.pixel_functions import image_plotter, pixel_cleaner, image_processor, roi_matcher

from loguru import logger


logger.info("Import OK")

#This functionality has been moved to this 'master' file to make processing simpler
# collect list of files in the input_folder that have .csv extension
input_folder = 'frap/example_data/prebleached/timepoints/Results_/'
output_path = 'frap/example_data/prebleached/Summary_calculations/'

# Check output folder exists - if not, create it
if not os.path.exists(output_path):
    os.mkdir(output_path)

file_list = [filename for filename in os.listdir(input_folder) if 'pixels.csv' in filename]
logger.info(f'The following files were detected from {input_folder}:\n {file_list}')

# collect list of positions in the input_folder
pos_names = list(set(sorted_nicely([name.split("_")[0] for name in file_list])))
logger.info(f'The following positions were detected:\n {pos_names}')

# Clean ROI pixels to simple dataframe for each image
results_type = ['FlAsH', 'mCherry']
summary_dict = {}

for position in pos_names:
    pos_files = [filename for filename in file_list if filename.split('_')[0] == position]
    # timepoint_names = sorted_nicely(list(set([name.split("_")[1] for name in pos_files])))
    # logger.info(f'The following timepoints were detected:\n {timepoint_names}')
    #
    # for timepoint in timepoint_names:
    image_dict = image_processor(input_folder, position, str(0), results_type, output_path, do_plot=False, save_file=False)
    # add position, time
    df = image_dict['mean_summary']
    df['pos'] = position

    image_dict['mean_summary'] = df
    summary_dict[position] = image_dict

## -----------------------test outputs----------------------------
# Checking out the summary results
summary_dict.keys() # shows the image names that were processed i.e. key 1

# generate summary df for each
summary_dfs = []
for position in pos_names:
    pos_dict = {}
    pos_files = [filename for filename in file_list if filename.split('_')[0] == position]
    # timepoint_names = sorted_nicely(list(set([name.split("_")[1] for name in pos_files])))
    # logger.info(f'The following timepoints were detected:\n {timepoint_names}')
    #
    # for timepoint in timepoint_names:

    summary_dfs.append(summary_dict[position]['mean_summary'])
summary = pd.concat(summary_dfs)

FileHandling.df_to_excel(output_path+f'mean_summmary_prebleached.xlsx', ['summary_sorted'], data_frames=[summary])

# to plot image of bleached/non-bleached pixels for first timepoint, with cell_track_id labelled
for position in pos_names:
    pos_files = [filename for filename in file_list if filename.split('_')[0] == position]
    # timepoint_names = sorted_nicely(list(set([name.split("_")[1] for name in pos_files])))
    # logger.info(f'The following timepoints were detected:\n {timepoint_names}')

    dfs = [summary_dict[position]['pixels']['mCherry'], summary_dict[position]['pixels']['bleached']]

    # generate list of ROIs to annotate
    label_df = summary.copy()
    summary.columns.tolist()
    label_df = label_df[label_df['pos'] == position][['cell_id', 'X_pos_roi', 'Y_pos_roi']].set_index('cell_id')
    # plot figure
    fig = image_plotter(dfs, colour_col='mCherry', cmaps=['Reds', 'Blues'])
    for label in label_df.index.tolist():
        plt.annotate(label, (round(label_df.loc[label,'X_pos_roi'], 0), round(label_df.loc[label,'Y_pos_roi'], 0)))
    plt.savefig(f'{output_path}{position}_prebleached_cells.png')
