import pandas as pd
import glob
import sys


"""
Python script to combine all the output files into a single file
Run as:
python3 combine_files.py output_folder_name
"""

# Read in the output folder as a filename
path = sys.argv[1]

# Get the names of all files
all_files = glob.glob(path+'/*.csv')

# Develop a python data frame to store the code
frame = pd.DataFrame()
file_list = []
for file_ in all_files:
    df = pd.read_csv(file_, index_col='advantage_prob')
    file_list.append(df)

# Concatenate all files together
df = pd.concat(file_list)

# Sort the df
df.sort_index(inplace=True)

# Write out to a .CSV
df.to_csv(path + '.csv')
