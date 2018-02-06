# -*- coding: utf-8 -*-
"""Base class for implementing any algorithms for OPAL computation."""


class OPALAlgorithm(object):
    """Base class for OPAL Algorithms.

    The class can be used in the following way::

        algo = OPALAlgorithm()
        result = algo.map(params, bandicoot_user)

    """

    def __init__(self):
        """Initialize the base class."""
        pass

    def map(self, params, bandicoot_user):
        """Map users data to a single result.

        Args:
            params(dict): Parameters to be used by each map of the algorithm.
            bandicoot_user (bandicoot.user): `Bandicoot user <http://
                bandicoot.mit.edu/docs/reference/generated/bandicoot.User.html#bandicoot.User>`_.

        Returns:
            dict: A dictionary representing with keys as string or tuple, and
            values as int or float which will be aggregated by the reducer.

        """
        raise NotImplementedError
