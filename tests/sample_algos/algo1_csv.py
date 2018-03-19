"""Old CSV based algorithm implementation."""
from __future__ import division, print_function
from opalalgorithms.core import OPALAlgorithm
import csv
import operator


class SampleAlgo1(OPALAlgorithm):
    """Calculate population density."""

    def __init__(self):
        """Initialize population density."""
        super(SampleAlgo1, self).__init__()

    def map(self, params, user_csv_file):
        """Map user_csv_file to user and most used antenna.

        Args:
            params(dict): Parameters to be used by each map of the algorithm.
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
        return {antenna: 1}
