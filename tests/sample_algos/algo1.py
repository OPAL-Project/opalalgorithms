"""Sample algorithm 1 to check there is no issue of imports, etc."""
from __future__ import division, print_function
from opalalgorithms.core import OPALAlgorithm
import csv
import operator


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

    def map(self, user_csv_file):
        """Map user_csv_file to user and most used antenna.

        Args:
            user_csv_file (str): Path to user_csv_file.
        """
        antennas = dict()
        with open(user_csv_file, 'r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                a = str(row[5])
                if a in antennas:
                    antennas[a] += 1
                else:
                    antennas[a] = 1
        antenna = max(antennas.items(), key=operator.itemgetter(1))[0]
        return self.__helper(antenna)

    def reduce(self, results_csv_file):
        """Convert results to count of population per antenna.

        Args:
            results_csv_file (int): Read results file and reduce to a result.
        """
        density = dict()
        with open(results_csv_file, 'r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=' ')
            for row in csv_reader:
                a = str(row[1])
                if a in density:
                    density[a] += 1
                else:
                    density[a] = 1
        return density

    def __helper(self, x):
        """Private helper function."""
        return self._helper(x)

    def _helper(self, x):
        """Fake Private helper function."""
        return helper(x)
