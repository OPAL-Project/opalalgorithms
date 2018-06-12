"""Sample algorithm 1 to check there is no issue of imports, etc."""
from __future__ import division, print_function
from opalalgorithms.core import OPALAlgorithm


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
        home = bandicoot_user.recompute_home()
        if not home:
            return None
        return {getattr(home, params["resolution"]): 1}
