# imports

from datetime import datetime

import numpy as np

# _____CONSTANTS_____

MICROSECOND_TO_SECOND_FACTOR = 1e+6


class Channel:

    # A class that holds all information from a neuralynx .ncs file

    def __init__(self, channel_number, time_stamps, raw_readings, header, scaling):
        """

        Returns:

            A channel object with the following properties:
                sampling_frequency: sampling frequency of the channel
                channel_number: number of the channel
                channel_name: name of the channel
                readings: readings for a given time frame in volts

        """

        # properties defined by the user
        self.scaling_factor = self.set_scaling_factor(scaling)

        # properties that can be directly set from source
        self._time_stamps = time_stamps
        self._header = header

        # properties that must be indexed from source
        self.sampling_frequency = float(self._header['SamplingFrequency'])
        self.channel_number = int(channel_number)
        self.channel_name = self._header['AcqEntName']

        # properties that must be computed from source
        self._raw_readings = raw_readings.ravel()
        self.readings = self._raw_readings * float(self._header['ADBitVolts']) * self.scaling_factor[0]

    # _____PROPERTIES_____

    @property
    def duration(self):
        """

        Returns:
            the duration of the recording (in seconds)

        """

        return len(self.readings) / self.sampling_frequency

    @property
    def date_and_time(self):
        """

        Returns:
             A tuple of time stamps denoting (start time, end time)
             
        """

        # note that the timestamps obtained from ncs files are in microseconds - must be converted to seconds
        # also note that the timestamps obtained from the readings are different from those written in the header
        created = datetime.utcfromtimestamp(self.time_stamps[0] / MICROSECOND_TO_SECOND_FACTOR)
        closed = datetime.utcfromtimestamp(self.time_stamps[-1] / MICROSECOND_TO_SECOND_FACTOR)

        return {'created': created, 'closed': closed}

    @property
    def time_stamps(self):
        """

        Returns:
             Timestamp (in microsecond) corresponding to each sample

        """

        return np.interp(np.arange(len(self.readings)), np.arange(0, len(self.readings), 512),
                         self._time_stamps).astype(np.uint64)

    # _____CLASS METHODS_____

    @staticmethod
    def set_scaling_factor(scaling):
        # determine the scaling factor
        if scaling is None:
            return 1, 'V'
        elif scaling == 'milli':
            return 1000, u'mV'
        elif scaling == 'micro':
            return 1000000, u'µV'
        else:
            raise Exception("Unknown scaling factor")
