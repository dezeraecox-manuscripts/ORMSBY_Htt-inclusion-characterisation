import os, re, string
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.lines import Line2D

from loguru import logger
from GEN_Utils import FileHandling

logger.info('Import OK')

input_folder = 'halotag_flowcytometry/example_data/'
output_folder = 'halotag_flowcytometry/initial_cleanup/'

if not os.path.exists(output_folder):
    os.mkdir(output_folder)

file_list = [('_').join(filename.split('_')[1:]) for filename in os.listdir(input_folder)]

# Read in each matched pair of i and ni data, store in single df in dict
clean_dict = {}
for filename in file_list:
    sample = filename.split('.')[0]
    i_raw = pd.read_csv(f'{input_folder}i_{filename}')
    i_clean = i_raw.copy()
    i_clean['inclusion'] = 1

    ni_raw = pd.read_csv(f'{input_folder}ni_{filename}')
    ni_clean = ni_raw.copy()
    ni_clean['inclusion'] = 0

    sample_df = pd.concat([i_clean, ni_clean])
    sample_df['sample_name'] = sample
    clean_dict[sample] = sample_df

clean_dict.keys()


compiled_df = pd.concat(list(clean_dict.values()))

FileHandling.df_to_excel(data_frames=[compiled_df], sheetnames=['compiled_all cells'], output_path=f'{output_folder}cleaned_summary.xlsx')
