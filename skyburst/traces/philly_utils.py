import datetime
import numpy as np

DATE_FORMAT_STR = '%Y-%m-%d %H:%M:%S'
MINUTES_PER_DAY = (24 * 60)
MICROSECONDS_PER_MINUTE = (60 * 1000)


def parse_date(date_str):
    """Parses a date string and returns a datetime object if possible.

       Args:
           date_str: A string representing a date.

       Returns:
           A datetime object if the input string could be successfully
           parsed, None otherwise.
    """
    if date_str is None or date_str == '' or date_str == 'None':
        return None
    return datetime.datetime.strptime(date_str, DATE_FORMAT_STR)


def timedelta_to_minutes(timedelta):
    """Converts a datetime timedelta object to minutes.

       Args:
           timedelta: The timedelta to convert.

       Returns:
           The number of minutes captured in the timedelta.
    """
    minutes = 0.0
    minutes += timedelta.days * MINUTES_PER_DAY
    minutes += timedelta.seconds / 60.0
    minutes += timedelta.microseconds / MICROSECONDS_PER_MINUTE
    return minutes


def get_cdf(data):
    """Returns the CDF of the given data.

       Args:
           data: A list of numerical values.

       Returns:
           An pair of lists (x, y) for plotting the CDF.
    """
    sorted_data = sorted(data)
    p = 100. * np.arange(len(sorted_data)) / (len(sorted_data) - 1)
    return sorted_data, p
