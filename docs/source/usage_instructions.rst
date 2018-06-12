usage instructions
==================

Creating algorithm has two main parts to it

* implementation
* testing

`opalalgorithms <https://github.com/OPAL-Project/opalalgorithms>`_ provides you with utilities to do both.

implementation
----------------------

We use :any:`opalalgorithms.core.base` that provides utilities for implementing an algorithm for OPAL. An algorithm will look like as follows:

.. code-block:: python

    """Sample algorithm 1 to return home of users."""
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


testing
----------------------

We provide utilities to test the algorithm you create. Before running the algorithm, it is advised you setup the apparmor and codejail as mentioned `here <https://github.com/shubhamjain0594/opalalgorithms>`_.

Use `tests/generate_data.py <https://github.com/OPAL-Project/opalalgorithms/blob/master/tests/generate_data.py>`_ to generate data after installing the opalalgorithms library. You can run your algorithm with the following code:

.. code-block:: python

    """Test population density algorithm."""
    from __future__ import division, print_function
    from opalalgorithms.utils import AlgorithmRunner


    num_threads = 3
    data_path = 'data'


    def get_algo(filename):
        algorithm = dict(
            code=open(filename).read(),
            className='ClassNameOfYourAlgo'
        )
        return algorithm


    def run_algo(algorithm_filename, params):
        """Run an algorithm."""
        algorithm = get_algo(algorithm_filename)
        algorunner = AlgorithmRunner(
            algorithm, dev_mode=False, multiprocess=True, sandboxing=True)
        result = algorunner(params, data_path, num_threads)
        return result


    if __name__ == '__main__':
        """Test that algorithm runner runs successfully."""
        params = dict(
            sample=0.2,
            resolution='location_level_1')
        assert run_algo('/path/to/your/algo.py', params)

