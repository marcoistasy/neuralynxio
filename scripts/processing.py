# imports

import mne


# _____PUBLIC FUNCTIONS____

def merge(channels):
    # todo

    # variable for holding the return
    merged_channels = []

    #
    for channel in channels:
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
        assert date == channel.timestamp[0], 'Dates do not match for channel {}'.format(i)
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
        channel_types.append(
            'seeg')  # note, this will have to be manually changed later as some EOG data will also be collected
        channel_data.append(channel.readings)

    # create mne data and metadata objects
    info = mne.create_info(channel_names, sampling_frequency, channel_types)
    info['description'] = description

    return channel_data, info


# _____PRIVATE FUNCTIONS____

# noinspection PyProtectedMember
def _get_expected_data(channel):
    # get all relevant metadata from a single channel object

    date = channel.timestamp[0]
    number_of_readings = channel.readings.shape[0]
    sampling_frequency = channel.sampling_frequency
    index = channel.index
    first_timestamp = channel._time_stamps[0]
    last_timestamp = channel._time_stamps[-1]

    return date, number_of_readings, sampling_frequency, index, first_timestamp, last_timestamp
