# -*- coding: utf-8 -*-
"""Calculate population density.

Author: Shubham Jain

"""
from .core.base import OPALAlgorithm
import csv
import os
import operator


class PopulationDensity(OPALAlgorithm):
    """Calculate population density."""

    def __init__(self):
        """Initialize population density."""
        super(PopulationDensity, self).__init__()

    def map(self, user_csv_file):
        """Mapping user_csv_file to user and most used antenna."""
        antennas = dict()
        with open(user_csv_file, 'r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                a = str(row[5])
                if a in antennas:
                    antennas[a] += 1
                else:
                    antennas[a] = 1
        username = os.path.splitext(os.path.basename(user_csv_file))[0]
        antenna = max(antennas.items(), key=operator.itemgetter(1))[0]
        return (username, antenna)

    def reduce(self, results_csv_file):
        """Convert results to count of population per antenna."""
        density = dict()
        with open('density.csv', 'r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=' ')
            for row in csv_reader:
                a = str(row[1])
                if a in density:
                    density[a] += 1
                else:
                    density[a] = 1
        return density
