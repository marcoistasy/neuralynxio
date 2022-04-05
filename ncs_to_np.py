# imports

import gc

import numpy as np

from scripts.neuralynxIO import read_neuralynx_continuous_files
from scripts.processing import check_metadata, extract_records, plot_channels
from utils.io import get_all_files_with_extension

# CONSTANTS
PATIENT_IDs = [1, 2, 3]
FILE_EXTENSION = '.ncs'

for patient_id in PATIENT_IDs:

    DIRECTORY_PATH = '/path/to/data/{}'.format(patient_id)
    OUTPUT_PATH = 'path/to/output{}.npz'.format(patient_id)

    # READ ALL NCS FILES IN A GIVEN DIRECTORY
    file_paths = get_all_files_with_extension(DIRECTORY_PATH, FILE_EXTENSION)
    channels = read_neuralynx_continuous_files(file_paths)
    
    # print description for user
    print('Creating records for Patient: {}. Recordings from {} to {}'.format(patient_id, channels[0].date_and_time[0], channels[0].date_and_time[1]))

    # CHECK METADATA AND CREATE NP OBJECTS
    if channels:

        # test metadata
        check_metadata(channels)

        # plot
        plot_channels(channels, OUTPUT_PATH)

        # create records
        channel_data, channel_names, _ = extract_records(channels)

        # memory clean-up
        channels_memory_id = id(channels)
        del channels_memory_id, channels, file_paths
        gc.collect()

        # save np records
        print('starting to save data file at {}'.format(OUTPUT_PATH))
        np.savez_compressed(OUTPUT_PATH, traces=channel_data, names=channel_names)
        print('finished saving data file.')
        
        # another memory clean-up
        channel_data_id = id(channel_data)
        del channel_data, channel_data_id
        gc.collect()
