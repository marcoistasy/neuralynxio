# %%

# imports

import gc

import mne

from scripts.neuralynxIO import read_neuralynx_files
from scripts.processing import sort_by_sampling_frequency, check_metadata, create_mne_data_and_metadata
from utils.io import get_all_files_with_extension, remove_paths_with_continuation

# CONSTANTS

SAMPLING_FREQUENCY = 4000.0
DESCRIPTION = 'Test'
DIRECTORY_PATH = '/path/to/directory'
FILE_EXTENSION = '.ncs'

# READ ALL NCS FILES IN A GIVEN DIRECTORY
file_paths = get_all_files_with_extension(DIRECTORY_PATH, FILE_EXTENSION)
file_paths = remove_paths_with_continuation(file_paths)  # remove any files which are a continuation of another
channels = read_neuralynx_files(file_paths)  # todo pick 20 channels per patient before reading

# SORT BY SAMPLING FREQUENCY
channels = sort_by_sampling_frequency(channels, SAMPLING_FREQUENCY)

# CHECK METADATA AND CREATE MNE OBJECTS
if channels:
    # test metadata and produce mne data and metadata objects
    check_metadata(channels)
    channel_data, info = create_mne_data_and_metadata(channels, SAMPLING_FREQUENCY, DESCRIPTION)

    # memory clean-up
    channels_memory_id = id(channels)
    del channels_memory_id, channels, file_paths
    gc.collect()

    # create mne object
    raw = mne.io.RawArray(channel_data, info)

    # another memory clean-up
    channel_data_id = id(channel_data)
    info_id = id(info)
    del channel_data, info, channel_data_id, info_id
    gc.collect()
