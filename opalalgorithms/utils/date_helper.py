"""Utility functions to help manipulate dates within different algorithms."""
import time

date_format = '%Y-%m-%d %H:%M:%S'


def is_date_between(start, end, date):
    """Check if data is between start and end datetime.

    Args:
        start (string): Starting datetime, must be of form '%Y-%m-%d %H:%M:%S'
        end (string): Ending datetime, must be of form '%Y-%m-%d %H:%M:%S'
        date (string): Date to be checked, must be of form '%Y-%m-%d %H:%M:%S'

    Returns:
        bool: Whether date is between end and start date.

    """
    stime = time.mktime(time.strptime(start, date_format))
    etime = time.mktime(time.strptime(end, date_format))
    ptime = time.mktime(time.strptime(date, date_format))
    return stime < ptime < etime


def is_date_greater(ref, date):
    """Check if date is greate than reference time.

    Args:
        ref (string): Reference datetime against which we need to check,
            must be of form '%Y-%m-%d %H:%M:%S'.
        date (string): Date which is to be checked, must be of form
            '%Y-%m-%d %H:%M:%S'

    Returns:
        bool: Whether date is greater than reference.

    """
    stime = time.mktime(time.strptime(ref, date_format))
    ptime = time.mktime(time.strptime(date, date_format))
    return stime < ptime
