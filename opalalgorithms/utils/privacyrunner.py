"""Privacy algorithm runner."""


class PrivacyAlgorithmRunner(object):
    """Run privacy algorithm.

    Args:
        algorithm (opalalgorithms.core.OPALPrivacy): OPALPrivacy object
        params (dict): Dictionary of parameters
        salt (string): Salt for the algorithm

    Notes:
        To use the class, initialize and then call the instance with the
        result object.
    """

    def __init__(self, algorithm, params, salt):
        """Initialize the algorithm runner."""
        self.algorithm = algorithm
        self.params = params
        self.salt = salt

    def __call__(self, result):
        """Run the algorithm, check if result is valid and return.

        Args:
            result (dict): Result over which privacy algorithm is to be applied

        Return:
            dict: Privacy ensured dictionary
        """
        result = self.algorithm(self.params, result, self.seed)
        if self._validate_result(result):
            return result
        return {}

    def _validate_result(self, result):
        return isinstance(result, dict)
