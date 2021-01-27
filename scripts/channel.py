# imports
import ntpath
from datetime import datetime

import numpy as np

# _____CONSTANTS_____

MILLISECOND_TO_SECOND_FACTOR = 1e+6


class Channel:

    # A class that holds all information from a neuralynx .ncs file

    def __init__(self, channel_number, time_stamps, raw_readings, header):
        """

        Returns:

            A channel object with the following properties:
                sampling_frequency: sampling frequency of the channel
                channel_number: number of the channel
                channel_name: name of the channel
                readings: readings for a given time frame in microvolts

        """

        # properties that can be directly set from source
        self._time_stamps = time_stamps
        self._header = header

        # properties that must be indexed from source
        self.sampling_frequency = float(self._header['SamplingFrequency'])
        self.channel_number = channel_number
        self.channel_name = self._header['AcqEntName']

        # properties that must be computed from source
        self._raw_readings = raw_readings.ravel()
        self.readings = self._raw_readings * float(self._header['ADBitVolts'])

    # _____PROPERTIES_____

    @property
    def duration(self):
        """

        Returns:
            the duration of the recording (in seconds)

        """

        return self.readings.shape[0] / self.sampling_frequency

    @property
    def time_vector(self):
        """

        Returns:

            a 1d time vector on which to map the recordings

        """

        return np.linspace(0, self.duration, self.readings.shape[0])

    @property
    def index(self):
        """

        Determines the index of the channel. In effect, whether the channel is stand-alone or a continuation of another

        Returns:

            Index of a channel

        """

        # strip file name of all superfluous data
        file_name = self._header['OriginalFileName']
        file_name_without_extension = ntpath.basename(file_name).split('.ncs')[0]

        # if the channel is part of a series, return the index. Otherwise, return 0.
        try:
            index = file_name_without_extension.split('_')[1]
            return int(index)
        except:
            return 0

    @property
    def date_and_time(self):
        """
        Returns:
             A tuple of time stamps denoting (start time, end time)
        """

        # note that the timestamps obtained from ncs files are in milliseconds. must be converted to seconds.
        created = datetime.utcfromtimestamp(self._time_stamps[0] / MILLISECOND_TO_SECOND_FACTOR)
        closed = datetime.utcfromtimestamp(self._time_stamps[-1] / MILLISECOND_TO_SECOND_FACTOR)

        return created, closed
