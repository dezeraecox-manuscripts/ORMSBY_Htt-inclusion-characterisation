import os, re
import glob
import numpy as np

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from functools import wraps
from scipy.spatial import distance
import string

import time
from loguru import logger

from GEN_Utils import FileHandling

logger.info('Import OK')

def timed(func):
    """This decorator prints the execution time for the decorated function."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        logger.debug("{} ran in {}s".format(func.__name__, round(end - start, 2)))
        return result
    return wrapper

@timed
def image_plotter(dataframes, colour_col=None, cmaps=None):
    if isinstance(cmaps, str):
        cmaps = [cmaps]

    fig, ax = plt.subplots(figsize=(10.24, 10.24))
    for x, dataframe in enumerate(dataframes):
        if colour_col:
            c = dataframe[colour_col]
        else:
            c = None
        plt.scatter(dataframe['X_pos'], dataframe['Y_pos'], c=c, cmap=cmaps[x], s=1)
    plt.xlim(0, 512)
    plt.ylim(0, 512)

    return fig

@timed
def pixel_cleaner(results_path, image_name):
    # read into pandas df
    raw_pixels = pd.read_csv(results_path)
    raw_pixels

    # Clean pixels info to generate single list with ROI, coords and intensity
    cleaning_pixels = raw_pixels.T.reset_index()
    cleaning_pixels

    cleaning_pixels['ROI_name'] = cleaning_pixels['index'].str.split('_').str[0]
    #logger.info(f'Cleaned pixels: {cleaning_pixels}')
    grouped_ROI = cleaning_pixels.set_index('ROI_name', drop=True).groupby('ROI_name')

    ROI_data_list = []
    for ROI, group in grouped_ROI:
        new_col_list = list(group['index'].str.split('_').str[1:3])
        ROI_data = group.T
        # Rename columns and drop previous column names
        ROI_data.columns = ['_'.join(x) for x in new_col_list]
        #ROI_data.columns = ['pos_X', 'pos_Y', 'Intensity_C1', 'Intensity_C2', 'Intensity_C3', 'Intensity_C4']
        ROI_data.drop('index', axis=0, inplace=True)
        # Remove leftover pixels from where imageJ assigns 0, 0 to the row - if all values are zero, we assume this is what happened
        ROI_data = ROI_data.replace(0, np.nan)
        ROI_data = ROI_data.dropna(how='all')
        ROI_data = ROI_data.replace(np.nan, 0)
        # add description columns for ROI name and image name
        ROI_data['ROI_name'] = ROI
        ROI_data['image_name'] = image_name
        ROI_data_list.append(ROI_data)

    ROI_pixels = pd.concat(ROI_data_list)
    ROI_pixels.reset_index(inplace=True, drop=True)
    ROI_pixels['X,Y'] = list(zip(ROI_pixels.X_pos, ROI_pixels.Y_pos))

    return ROI_pixels

@timed
def image_processor(input_folder, position, timepoint, results_type, output_path, do_plot=False, save_file=False):
    channel_dict = {}
    pixel_dict = {}
    image_name = ("_").join([position, timepoint])
    for channel in results_type:
        results_path = input_folder+image_name+f'_{channel}_pixels.csv'
        logger.info(f'Processing ROI pixels from {image_name}')
        df = pixel_cleaner(results_path, image_name)
        pixel_dict[channel] = df
        #logger.info(f'pixel_df for {channel}: {df.head()}')
        # calculate total number of pixels, save to dict
        num_pixels_df = df.groupby('ROI_name').count()
        pixel_count = dict(zip(num_pixels_df.index.tolist(), round(num_pixels_df.X_pos, 0)))
        # caluclate mean values
        mean_df = df.groupby('ROI_name').mean().reset_index()
        mean_df['coords'] = list(zip(round(mean_df.X_pos, 0), round(mean_df.Y_pos, 0)))
        mean_df['dist_from_origin'] = [distance.euclidean(coord, (0, 0)) for coord in mean_df['coords']]
        mean_df['pixel_count'] = mean_df['ROI_name'].map(pixel_count)
        channel_dict[channel] = mean_df.set_index('ROI_name')

    # Filter ROI_pixels to remove nb pixels, leaving bleached pixels
    logger.info(f'Filtering non-bleached pixels from ROI pixels for {image_name}')
    pixel_dict['bleached'] = pixel_dict['FlAsH'][~pixel_dict['FlAsH']['X,Y'].isin(pixel_dict['mCherry']['X,Y'])]
    mean_df = pixel_dict['bleached'].groupby('ROI_name').mean().reset_index()
    mean_df['coords'] = list(zip(round(mean_df.X_pos, 0), round(mean_df.Y_pos, 0)))
    mean_df['dist_from_origin'] = [distance.euclidean(coord, (0, 0)) for coord in mean_df['coords']]
    mean_df.set_index('ROI_name', inplace=True)
    channel_dict['bleached'] = mean_df

    channel_dict.keys()

    # Match ROI's between two channels according to x_pos and distance from origin (to account for ROIs that are lost between channels)

    roi_dict = roi_matcher(channel_dict['FlAsH'], channel_dict['mCherry'])
    #rename columns before combining df according to mapped ROIs

    # Calculate proportion of bleached pixels to enable removing any ROIs that were not bleached
    # copy dfs and relabel columns
    percent_bleached_ROI = channel_dict['FlAsH'].copy().reset_index()
    percent_bleached_ROI.columns = [f'{col}_roi' for col in percent_bleached_ROI.columns.tolist()]
    percent_bleached_nb = channel_dict['mCherry'].copy().reset_index()
    percent_bleached_nb.columns = [f'{col}_nb' for col in percent_bleached_nb.columns.tolist()]
    percent_bleached = channel_dict['bleached'].copy().reset_index()
    percent_bleached.columns = [f'{col}_b' for col in percent_bleached.columns.tolist()]
    # map both channels ROI
    percent_bleached_ROI['ROI_name_nb'] = percent_bleached_ROI['ROI_name_roi'].map(roi_dict)
    percent_bleached['ROI_name_nb'] = percent_bleached['ROI_name_b'].map(roi_dict)
    # drop any cells that dont have mapped ROI
    percent_bleached = percent_bleached.dropna()
    percent_bleached_ROI = percent_bleached_ROI.dropna()

    # merge on mapped ROI
    mean_summary = pd.concat([df.set_index('ROI_name_nb') for df in [percent_bleached, percent_bleached_nb, percent_bleached_ROI]], axis=1).reset_index().rename(columns={'index': 'ROI_name_nb'})
    #calculate % bleaching
    mean_summary['percent_bleached'] = 100 - (mean_summary['pixel_count_nb'] / mean_summary['pixel_count_roi'] * 100)

    # add ID to track individual cells
    mean_summary['cell_id'] = [f'{position}_{letter}_{timepoint}' for letter in list(string.ascii_lowercase)[0:mean_summary.shape[0]]]
    mean_summary.set_index('ROI_name_roi', inplace=True)
    for roi in mean_summary.index.tolist():
        if mean_summary.loc[roi, 'mCherry_roi'] ==  mean_summary.loc[roi, 'mCherry_nb']:
            mean_summary.loc[roi, 'cell_id'] = 'background'
    mean_summary.reset_index(inplace=True)

    # map new cell IDs to old ROI names
    cell_id_dict = {}
    cell_id_dict['roi'] = dict(zip(mean_summary['ROI_name_roi'], mean_summary['cell_id']))
    cell_id_dict['nb'] = dict(zip(mean_summary['ROI_name_nb'], mean_summary['cell_id']))

    excl_ids = list(mean_summary[(mean_summary['percent_bleached'] < 30)].reset_index()['cell_id'])
    excl_ids.remove('background')

    if len(excl_ids) > 0:
        logger.info(f'Nonbleached regions found: {excl_ids}')
        mean_summary = mean_summary[~mean_summary['cell_id'].isin(excl_ids)]

    # Calculate background-corrected values
    back_val = mean_summary.set_index('cell_id').loc['background', 'mCherry_roi']
    mean_summary['Mean_b_corrected'] = mean_summary['mCherry_b'] - back_val
    mean_summary['Mean_nb_corrected'] = mean_summary['mCherry_nb'] - back_val

    mean_summary['FRAP_val'] = mean_summary['Mean_b_corrected'] / mean_summary['Mean_nb_corrected']

    if save_file:
        # Save to excel file:
        logger.info(f'Saving individual excel files for {image_name}')
        FileHandling.df_to_excel(output_path+f'{image_name}_pixel_filtered.xlsx', ['ROI', 'non_bleached', 'bleached'], data_frames=[ROI_pixels, nb_pixels, bleached_pixels])

    if do_plot:
        # plot individual images
        logger.info(f'Generating example images for {image_name}')
        fig = image_plotter([summary_dict[image_name]['Non-bleached'], summary_dict[image_name]['Bleached']], colour_col='mCherry', cmaps=['Reds', 'Blues'])
        plt.savefig(output_path+f'{image_name}_fig.jpg')
        logger.info('Plot successfully generated.')

    logger.info(f'Pixels processed successfully for {image_name}! Results saved to {output_path}')

    return {'pixels':pixel_dict, 'mean_summary':mean_summary, 'excl_rois':excl_ids}

def sorted_nicely( l ):
    """ Sorts the given iterable in the way that is expected.

    Required arguments:
    l -- The iterable to be sorted.

    """
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(l, key = alphanum_key)

@timed
def roi_matcher(df_a, df_b, col='coords', x_tolerance=20, y_tolerance=10):
    roi_dict = {}
    for roi in df_a.index.tolist():
        x_pos, y_pos = df_a.loc[roi, col]
        matching_coords = [(x_new, y_new) for (x_new, y_new) in df_b[col] if abs(x_new - x_pos) < x_tolerance if abs(y_new - y_pos) < y_tolerance ]
        if len(matching_coords) == 1:
            roi_dict[roi] = df_b[df_b[col] == matching_coords[0]].index.tolist()[0]
        elif len(matching_coords) > 1:
            logger.info(f'Multiple matching coordinates found. Unable to match ambiguous ROI at {roi}')
        else:
            logger.info(f'No matching coordinates found for {roi}.')
    return roi_dict


if __name__ == '__main__':
    input_folder = 'C:/Users/Dezerae/Documents/Current Analysis/190429_AO_Analysis_Inclusion FRAP calculations/ImageJ_results/timepoints/Results_/'
    output_path = 'C:/Users/Dezerae/Documents/Current Analysis/190429_AO_Analysis_Inclusion FRAP calculations/Python_results/Summary_calculations/'
    position = '2'
    timepoint = '0'
    image_name = ("_").join([position, timepoint])
    image_processor(input_folder, image_name, output_path)
