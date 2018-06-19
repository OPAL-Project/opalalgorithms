# -*- coding: utf-8 -*-
"""Base class for implementing any privacy algorithms for OPAL computation."""


class OPALPrivacy(object):
    """Base class for OPAL Privacy Algorithms.

    The class can be used in the following way::

        privacyalgo = OPALPrivacy()
        result = privacyalgo(params, result, salt)

    """

    def __init__(self):
        """Initialize the base class."""
        pass

    def __call__(self, params, result, salt):
        """Processes result to make it differentially private.

        Args:
            params(dict): Parameters to be used by each map of the algorithm.
            result(dict): Result to be made differentially private.
            salt(text): An unique salt to be used for computation.

        Returns:
            dict: Returns result by making it differentially private.

        """
        raise NotImplementedError
