"""Sample algorithm 1 to check there is no issue of imports, etc."""
from __future__ import division, print_function
from opalalgorithms.core import OPALAlgorithm


def helper(x):
    """Just a helper function."""
    return __helper(x)


def __helper(x):
    """Private function."""
    return x


class SampleAlgo1(OPALAlgorithm):
    """Calculate population density."""

    def __init__(self):
        """Initialize population density."""
        super(SampleAlgo1, self).__init__()

    def map(self, params, bandicoot_user):
        """Get home of the bandicoot user.

        Args:
            params (dict): Request parameters.
            bandicoot_user (bandicoot.core.User): Bandicoot user object.

        """
        # TODO: Use aggregation level setting from
        # antenna_id, location_level_1 or location_level_2
        home = bandicoot_user.recompute_home()
        if not home:
            return None
        return {home.antenna: 1}

    def __helper(self, x):
        """Private helper function."""
        return self._helper(x)

    def _helper(self, x):
        """Fake Private helper function."""
        return helper(x)
