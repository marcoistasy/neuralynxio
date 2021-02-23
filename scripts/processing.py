# imports

import mne


# _____PUBLIC FUNCTIONS____

def merge(channels):
    # todo: implement a function to take channels and elide them
    pass


def sort_by_sampling_frequency(channels, desired_frequency):
    """

    Sort an array of channels by a given frequency

    Args:
        channels: [channels]
            array of channels to be sorted
        desired_frequency: float
            frequency of desired channels

    Returns:
        return_channels: array
            array of channels with desired frequency
    """

    # instantiate return
    return_channels = []

    # sort each channel by sampling frequency
    for channel in channels:
        if channel.sampling_frequency == desired_frequency:
            return_channels.append(channel)

    return return_channels


# noinspection PyProtectedMember
def check_metadata(channels):
    """

    Test all channels to make sure that they are the same in date, number of readings, sampling frequency, index, and timestamps.
    This is a sanity check as neuralynx is known to be iffy.

    Args:
        channels: [channels]
            array of channels to be checked

    """

    # get expected data from the first channel
    date, number_of_readings, sampling_frequency, index, first_timestamp, last_timestamp = _get_expected_data(
        channels[0])

    # for all subsequent channel, make sure there metadata is the same
    for i, channel in enumerate(channels):
        assert date == channel.date_and_time, 'Dates do not match for channel {}'.format(i)
        assert number_of_readings == channel.readings.shape[0], 'Number of readings do not match for channel {}'.format(
            i)
        assert index == channel.index, 'Indices do not match for channel {}'.format(i)
        assert sampling_frequency == channel.sampling_frequency, 'Sampling frequencies do not match for channel {}'.format(
            i)
        assert first_timestamp == channel._time_stamps[0], 'First timestamps do not match for channel {}'.format(i)
        assert last_timestamp == channel._time_stamps[-1], 'Last timestamps do not match for channel {}'.format(i)

    # data is okay
    print('Data is okay.')


def create_mne_data_and_metadata(channels, sampling_frequency, description):
    """

    Create MNE data and metadata objects from Channels.

    Args:
        channels: [channels]
            array of channels
        sampling_frequency: float
            sampling frequency of channels
        description: str
            description of dataset

    Returns:
        channel_data: [float]
            n-dimensional array of channel readings
        info: mne.info
            info object containing all metadata

    """

    # instantiate metadata for mne
    channel_names = []
    channel_types = []
    channel_data = []

    # instantiate channel data
    for channel in channels:
        channel_names.append(channel.channel_name)
        channel_types.append(_get_channel_type(channel.channel_name))
        channel_data.append(channel.readings)

    # create mne data and metadata objects
    info = mne.create_info(channel_names, sampling_frequency, channel_types)
    info['description'] = description
    info['sfreq'] = sampling_frequency

    return channel_data, info


# _____PRIVATE FUNCTIONS____

# noinspection PyProtectedMember
def _get_expected_data(channel):
    # get all relevant metadata from a single channel object

    date = channel.date_and_time
    number_of_readings = channel.readings.shape[0]
    sampling_frequency = channel.sampling_frequency
    index = channel.index
    first_timestamp = channel._time_stamps[0]
    last_timestamp = channel._time_stamps[-1]

    return date, number_of_readings, sampling_frequency, index, first_timestamp, last_timestamp


def _get_channel_type(channel_name):
    # get name of electrodes and corresponding electrode type

    surface_electrode_names = ['A11', 'A21', 'Zg11', 'Zg21', 'C31', 'C41', 'Cz1', 'E11', 'E21', 'F31', 'F41', 'Fz1',
                               'P31', 'P41', 'Pz1']
    ocular_electrode_names = ['O1', 'O11', 'O2', 'O21']

    if channel_name == 'EKG1':
        return 'ecg'
    elif channel_name in surface_electrode_names:
        return 'eeg'
    elif channel_name in ocular_electrode_names:
        return 'eog'
    else:
        return 'seeg'
