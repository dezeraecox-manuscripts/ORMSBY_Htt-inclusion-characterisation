import os, re
import glob
import numpy as np


import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from GEN_Utils import FileHandling
from GEN_Utils.CalcUtils import sorted_nicely
from frap.scripts.analysis_scripts.pixel_functions import image_plotter, pixel_cleaner, image_processor, roi_matcher

from loguru import logger


logger.info("Import OK")

#This functionality has been moved to this 'master' file to make processing simpler
# collect list of files in the input_folder that have .csv extension
input_folder = 'frap/example_data/bleached/timepoints/Results_/'
output_path = 'frap/example_data/bleached/Summary_calculations/'

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
    pos_dict = {}
    pos_files = [filename for filename in file_list if filename.split('_')[0] == position]
    timepoint_names = sorted_nicely(list(set([name.split("_")[1] for name in pos_files])))
    logger.info(f'The following timepoints were detected:\n {timepoint_names}')

    for timepoint in timepoint_names:
        image_dict = image_processor(input_folder, position, timepoint, results_type, output_path, do_plot=False, save_file=False)
        # add position, time
        df = image_dict['mean_summary']
        df['pos'] = position
        df['timepoint'] = timepoint

        image_dict['mean_summary'] = df
        pos_dict[timepoint] = image_dict
    summary_dict[position] = pos_dict


###-------------------------------------
# position = '5'
# timepoint = '19'
# image_processor(input_folder, position, timepoint, results_type, output_path, do_plot=True, save_file=True)

## -----------------------test outputs----------------------------
# Checking out the summary results
summary_dict.keys() # shows the image names that were processed i.e. key 1

# generate summary df for each
summary_dfs = []
for position in pos_names:
    pos_dict = {}
    pos_files = [filename for filename in file_list if filename.split('_')[0] == position]
    timepoint_names = sorted_nicely(list(set([name.split("_")[1] for name in pos_files])))
    logger.info(f'The following timepoints were detected:\n {timepoint_names}')

    for timepoint in timepoint_names:

        summary_dfs.append(summary_dict[position][timepoint]['mean_summary'])
summary = pd.concat(summary_dfs)

# map matching ROIs across timepoints
#---> group according to position, timepoints
position_mapped = {}
for position in pos_names:
    pos_files = [filename for filename in file_list if filename.split('_')[0] == position]
    timepoint_names = sorted_nicely(list(set([name.split("_")[1] for name in pos_files])))
    logger.info(f'The following timepoints were detected:\n {timepoint_names}')
    #define empty df to store tracking info, set column 1 to be cell_ids from t0
    roi_mapped = pd.DataFrame()
    roi_mapped[timepoint_names[0]] = summary_dict[position][timepoint_names[0]]['mean_summary']['cell_id']
    for x, timepoint in enumerate(timepoint_names[:-1]):
        # select ROI in first timepoint --> find matching ROI in second timepoint
        # repeat up to second last timepoint i.e. x matched with x+1 up to (len(timepoints)-1)
        df_a = summary_dict[position][timepoint_names[x]]['mean_summary']
        df_b = summary_dict[position][timepoint_names[x+1]]['mean_summary']
        # find matching ROIs between two timepoints - can play with the tolerance here!
        matched_rois = roi_matcher(df_a.set_index('cell_id'), df_b.set_index('cell_id'), col='coords_roi', x_tolerance=20, y_tolerance=20)
        #Add new column to the dataframe for new timepoint by mapping the previous timepoint with the matched rois
        roi_mapped[timepoint_names[x+1]] = roi_mapped[timepoint_names[x]].map(matched_rois)
    # add new column with updated cell id for a single track
    roi_mapped['cell_track_id'] = [f'pos_{position}_cell_{x}' for x in range(0, len(roi_mapped))]
    position_mapped[position] = roi_mapped

# generate a dictionary mapping the cell_id to cell_track_id
track_dict = {}
for position in pos_names:
    pos_dict = {}
    pos_files = [filename for filename in file_list if filename.split('_')[0] == position]
    timepoint_names = sorted_nicely(list(set([name.split("_")[1] for name in pos_files])))
    logger.info(f'The following timepoints were detected:\n {timepoint_names}')

    mapped_rois = position_mapped[position]
    for timepoint in timepoint_names:
        track_dict.update(dict(zip(mapped_rois[timepoint], mapped_rois['cell_track_id'])))
# remove nan key, update background key as unnecessary
track_dict.pop(np.nan, None)
track_dict.update({'background': 'background'})

# add cell tracking to summary table, sort by pos, cell track then timepoint to give nice chunks of cell data
summary['cell_track_id'] = summary['cell_id'].map(track_dict)
summary['timepoint'] = summary['timepoint'].astype('int')
summary_sorted = summary.sort_values(['pos','cell_track_id', 'timepoint'])

plottable = summary_sorted[['cell_track_id', 'timepoint', 'FRAP_val']].set_index('cell_track_id').drop('background', axis=0)
plottable = plottable.reset_index().pivot(index='timepoint', columns='cell_track_id', values='FRAP_val').reset_index().sort_values('timepoint', axis=0)

FileHandling.df_to_excel(output_path+f'mean_summmary.xlsx', ['for_plotting', 'summary_sorted'], data_frames=[plottable, summary_sorted])

# to plot image of bleached/non-bleached pixels for first timepoint, with cell_track_id labelled
for position in pos_names:
    pos_files = [filename for filename in file_list if filename.split('_')[0] == position]
    timepoint_names = sorted_nicely(list(set([name.split("_")[1] for name in pos_files])))
    logger.info(f'The following timepoints were detected:\n {timepoint_names}')

    dfs = [summary_dict[position][timepoint_names[0]]['pixels']['mCherry'], summary_dict[position][timepoint_names[0]]['pixels']['bleached']]

    # generate list of ROIs to annotate
    label_df = summary_sorted[summary_sorted['timepoint'] == int(timepoint_names[0])]
    label_df = label_df[label_df['pos'] == position][['cell_track_id', 'X_pos_roi', 'Y_pos_roi']].set_index('cell_track_id')
    # plot figure
    fig = image_plotter(dfs, colour_col='mCherry', cmaps=['Reds', 'Blues'])
    for label in label_df.index.tolist():
        plt.annotate(label, (round(label_df.loc[label,'X_pos_roi'], 0), round(label_df.loc[label,'Y_pos_roi'], 0)))
    plt.savefig(f'{output_path}{position}_t0_cells.png')

# Generate plots for individual cell tracks
for group, df in summary_sorted.groupby('cell_track_id'):
    fig = plt.subplots()
    sns.scatterplot('timepoint', 'FRAP_val', data=df)
    plt.title(group)
    plt.show()
