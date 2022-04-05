# %%

# imports

import gc

import matplotlib
import matplotlib.pyplot as plt
import mne

from scripts.neuralynxIO import read_neuralynx_continuous_files
from scripts.processing import sort_by_sampling_frequency, check_metadata, extract_records
from utils.io import get_all_files_with_extension

# set matplotlib backend
matplotlib.use('agg')

# CONSTANTS
PATIENT_IDs = [1, 2, 3]
SAMPLING_FREQUENCY = 4000.0
FILE_EXTENSION = '.ncs'

for patient_id in PATIENT_IDs:

    DIRECTORY_PATH = '/path/to/data/{}'.format(patient_id)

    # READ ALL NCS FILES IN A GIVEN DIRECTORY
    file_paths = get_all_files_with_extension(DIRECTORY_PATH, FILE_EXTENSION)
    channels = read_neuralynx_continuous_files(file_paths)
    DESCRIPTION = 'Patient: {}. Recordings from {} to {}'.format(patient_id, channels[0].date_and_time[0],
                                                                 channels[0].date_and_time[1])

    # SORT BY SAMPLING FREQUENCY
    channels = sort_by_sampling_frequency(channels, SAMPLING_FREQUENCY)

    # CHECK METADATA AND CREATE MNE OBJECTS
    if channels:

        # test metadata
        check_metadata(channels)

        # create records
        channel_data, channel_names, channel_types = extract_records(channels)

        # pass records to mne info object
        info = mne.create_info(channel_names, SAMPLING_FREQUENCY, channel_types)
        info['description'] = DESCRIPTION
        info['sfreq'] = SAMPLING_FREQUENCY

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

        # save mne data alongside psd
        figure = raw.plot_psd(fmax=SAMPLING_FREQUENCY / 2, average=True)
        plt.savefig('{}/twh{}_psd.png'.format(DIRECTORY_PATH, patient_id))
        raw.save('{}/twh{}_raw.fif'.format(DIRECTORY_PATH, patient_id), overwrite=True, fmt='double')

        # last memory clean-up
        del raw
        gc.collect()
