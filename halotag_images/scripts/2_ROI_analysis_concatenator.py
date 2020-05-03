import os, re
from functools import reduce
import pandas as pd
from GEN_Utils import FileHandling

# Utility function for sorting numerical strings nicely
def sorted_nicely( l ):
    """ Sorts the given iterable in the way that is expected.

    Required arguments:
    l -- The iterable to be sorted.

    """
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(l, key = alphanum_key)


input_folder = 'halotag_images/example_data/Results/'


file_list = os.listdir(input_folder)

# collect list of files in the input_folder that have .csv extension
results_file_list = [filename for filename in file_list if '.csv' in filename]
results_file_list

# Establish empty list to store dataframes
raw_data = []

# read in each csv file, add image name and add df to list
for filename in results_file_list:
    data = pd.read_csv(input_folder+filename)
    data['image_name'] = filename.split('_')[0]
    raw_data.append(data)

# join all dataframes in list underneath one another
compiled_data = pd.concat(raw_data)
compiled_data.reset_index(inplace=True, drop=True)

# calculate number of cells
num_cells = int(compiled_data.shape[0]/3)

# add descriptors and calculations to df
compiled_data['ROI_type'] = ['Incl', 'outer', 'cyto'] * num_cells
compiled_data['Flash/Cer'] = compiled_data['c3_intensity']/compiled_data['c1_intensity']
compiled_data['cell_num'] = sorted_nicely([f'Cell_{x}' for x in range(1, num_cells+1)] * 3)

# Collect adj and inclusion dataframes separately
outer_data = compiled_data.set_index(['image_name', 'cell_num']).groupby('ROI_type').get_group('outer')
outer_data.columns = [f'{col}_outer' for col in outer_data.columns.tolist()]

cyto_data = compiled_data.set_index(['image_name', 'cell_num'], drop=True).groupby('ROI_type').get_group('cyto')
cyto_data.columns = [f'{col}_cyto' for col in cyto_data.columns.tolist()]

incl_data = compiled_data.set_index(['image_name', 'cell_num'], drop=True).groupby('ROI_type').get_group('Incl')
incl_data.columns = [f'{col}_incl' for col in incl_data.columns.tolist()]

# Join on cell number
df_list = [incl_data, outer_data, cyto_data]
sorted_data = reduce(lambda df1,df2: pd.merge(df1,df2,on=['image_name', 'cell_num']), df_list)

# save to excel
FileHandling.df_to_excel(input_folder+'Compiled.xlsx', data_frames=[sorted_data, compiled_data], sheetnames=["Sorted", 'Compiled'])
