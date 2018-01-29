# -*- coding: utf-8 -*-
"""Base class for implementing any algorithms for OPAL computation."""


class OPALAlgorithm(object):
    """Base class for OPAL Algorithms."""

    def __init__(self):
        """Initialize the base class."""
        pass

    def map(self, params, user_csv_file):
        """Map users data to a single result.

        Args:
            params(dict): Parameters to be used by each map of the algorithm.
            users_csv_files(string): Path to csv file for a user.

        Returns:
            obj: single object representing computed result for the user.

        """
        raise NotImplementedError

    def reduce(self, params, results_csv_file):
        """Reduce all user results to a single result object.

        Args:
            params(dict): Parameters to be used by each map of the algorithm.
            results_csv_file(string): csv file containing results received from map.

        Returns:
            obj: single object obtained as part of reduction of results.

        """
        raise NotImplementedError
