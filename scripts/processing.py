import matplotlib.pyplot as plt


# _____PUBLIC FUNCTIONS____

def merge(channels):
    # todo: implement a function to take channels and elides them
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
        return_channels: [Channels]
            array of channels with desired frequency
    """

    # instantiate return
    return_channels = []

    # sort each channel by sampling frequency
    for channel in channels:
        if channel.sampling_frequency == desired_frequency:
            return_channels.append(channel)

    return return_channels


def plot_channels(channels, output_directory):
    """

    Plots the trace for a given time channel

    Args:
        channels: [channels]
            array of channels to be plotted
        output_directory: str
            the directory at which to save the plots

    """

    for channel in channels:
        # create figure
        fig, ax = plt.subplots(figsize=(32, 12))

        # customise figure
        ax.set_title('{}'.format(channel.channel_name))
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Voltage (v)')

        # plot trace
        ax.plot(channel.time_vector, channel.readings)

        # save figure and close
        plt.savefig('{}/{}.png'.format(output_directory, channel.channel_name))
        plt.close('all')


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

    # print expected values to user
    print(
        'Expected date: {} \n Expected number of readings: {} \n Expected sampling frequency: {} \n Expected first timestamp: {} \n Expected last timestamp: {}'.format(
            date, number_of_readings, sampling_frequency, first_timestamp, last_timestamp))

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


def extract_records(channels):
    """

    Create data and metadata records from Channels.

    Args:
        channels: [Channels]
            array of Channels

    Returns:
        channel_data: [float]
            MxN matrix of channel readings where M is the channel id and N is a reading
        channel_names: [str]
            the channel names
        channel_names: [str]
            the type of channel -- either 'eog' 'ecg' 'eeg' or 'seeg'

    """

    # instantiate metadata for mne
    channel_data = []
    channel_names = []
    channel_types = []

    # instantiate channel data
    for channel in channels:
        channel_data.append(channel.readings)
        channel_names.append(channel.channel_name)
        channel_types.append(_get_channel_type(channel.channel_name))

    return channel_data, channel_names, channel_types


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
    if channel_name in surface_electrode_names:
        return 'eeg'
    if channel_name in ocular_electrode_names:
        return 'eog'
    return 'seeg'
