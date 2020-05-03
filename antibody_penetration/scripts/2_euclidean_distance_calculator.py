import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os, re
from scipy.spatial import distance

from loguru import logger
from GEN_Utils.CalcUtils import sorted_nicely
from GEN_Utils import FileHandling


logger.info("Import OK")

input_folder = 'antibody_penetration/example_data/Results/'
output_path = 'antibody_penetration/example_data/Summary_results/'

if not os.path.exists(output_path):
    os.mkdir(output_path)

file_list = os.listdir(input_folder)
logger.info(f'The following files were detected from {input_folder}:\n {file_list}')

# collect list of files in the input_folder that have .csv extension
position_names = sorted_nicely(set([name.split("_")[3] for name in file_list if '.csv' in name]))
centroid_files = sorted_nicely([name for name in file_list if 'centroids' in name])
coord_files = sorted_nicely([name for name in file_list if 'pixel_cords' in name])

logger.info(f'The following position names were detected:\n {position_names}')

# Generate dictionary to store data
distance_dict = {}
# iterate through all positions
for pos in position_names:

    # import ROI pixels
    pixel_file = os.path.join(input_folder, f'Channel_1_Position_{pos}_pixel_cords.csv')

    pixels_raw = pd.read_csv(pixel_file)
    pixels = pixels_raw.copy()
    # Collect ROI names from column headers
    ROI_names = list(set([col_name.split("_")[0] for col_name in pixels.columns.tolist()]))

    # Determine outer ROI according to max x value

    max_pos = np.max(pixels[[col for col in pixels.columns.tolist() if 'X_pos' in col]])

    outer_ROI_name = max_pos[max_pos == np.max(max_pos)].index[0].split("_")[0]

    inner_ROI_name = [name for name in ROI_names if outer_ROI_name not in name][0]

    # import centroid info, select centroid according to outer ROI name
    centroid_file = os.path.join(input_folder, f'Channel_1_Position_{pos}_centroids.csv')
    centroid_raw = pd.read_csv(centroid_file)

    outer_centroid = centroid_raw[centroid_raw['ROI_name'] == outer_ROI_name]
    outer_centroid_pos = list(zip(outer_centroid.Centroid_X_pos, outer_centroid.Centroid_Y_pos))[0]

    # Generate x,y coord for each ROI and calculate boundary pixels for each ROI
    boundary_pixels = {}
    for ROI in ROI_names:
        ROI_all = pixels[[col for col in pixels.columns.tolist() if ROI in col]].replace(0, np.nan).dropna(axis=0, how='all')

        ROI_pixels = ROI_all[[col for col in ROI_all.columns.tolist() if '_s' not in col]]

        ROI_pixels['X,Y'] = list(zip(ROI_pixels[f'{ROI}_X_pos'], ROI_pixels[f'{ROI}_Y_pos']))

        shrink_pixels = ROI_all[[col for col in ROI_all.columns.tolist() if '_s' in col]].dropna(axis=0, how='all')

        shrink_pixels['X,Y'] = list(zip(shrink_pixels[f'{ROI}_X_pos_s'], shrink_pixels[f'{ROI}_Y_pos_s']))

        # determine boundary pixels by removing shrunken pixels
        boundary = ROI_pixels[~ROI_pixels['X,Y'].isin(shrink_pixels['X,Y'])]
        boundary.columns = ['X_pos', 'Y_pos', 'X,Y']

        # Calculate distance for every pixel in the boundary pixels
        pixel_tuples = list(zip(boundary['X_pos'], boundary['Y_pos']))
        boundary['dist_to_outer_centroid'] = [distance.euclidean(coord, outer_centroid_pos) for coord in pixel_tuples]

        boundary_pixels[ROI] = boundary

    FileHandling.df_to_excel(output_path+f'pos_{pos}_summary.xlsx', data_frames=list(boundary_pixels.values()), sheetnames=list(boundary_pixels.keys()))

    outer_mean_dist = boundary_pixels[outer_ROI_name]['dist_to_outer_centroid'].mean()

    inner_mean_dist = boundary_pixels[inner_ROI_name]['dist_to_outer_centroid'].mean()

    mean_diff = outer_mean_dist - inner_mean_dist

    distance_dict[pos] = mean_diff

    # Plot the boundary pixels
    fig_1, ax = plt.subplots()
    sns.scatterplot('X_pos', 'Y_pos', data=boundary_pixels[outer_ROI_name], linewidth=0)
    sns.scatterplot('X_pos', 'Y_pos', data=boundary_pixels[inner_ROI_name], linewidth=0)
    sns.scatterplot('Centroid_X_pos', 'Centroid_Y_pos', data=outer_centroid, linewidth=0)
    fig_1.savefig(output_path+f'pos_{pos}.png')

mean_distances = pd.DataFrame()
mean_distances['Position_names'] = list(distance_dict.keys())
mean_distances['Mean_distance_outer_centroid'] = list(distance_dict.values())

FileHandling.df_to_excel(output_path+f'Summary_distances.xlsx', data_frames=[mean_distances], sheetnames=['Dist. to outer centroid'])
