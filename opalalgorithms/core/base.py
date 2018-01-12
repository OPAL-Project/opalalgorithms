# -*- coding: utf-8 -*-
"""Base class for implementing any algorithms for OPAL computation.

Author: Shubham Jain

"""


class OPALAlgorithm(object):
    """Base class for OPAL Algorithms."""

    def __init__(self):
        """Initialize the base class."""
        pass

    def map(self, user_csv_file):
        """Map users data to a single result.

        Args:
            users_csv_files(string): Path to csv file for a user.

        Returns:
            obj: single object representing computed result for the user.

        """
        raise NotImplementedError

    def reduce(self, results_csv_file):
        """Reduce all user results to a single result object.

        Args:
            results_csv_file: csv file containing results received from map.

        Returns:
            obj: single object obtained as part of reduction of results.

        """
        raise NotImplementedError
