#!/bin/bash

rm -rf data
rm -rf results
mkdir data
mkdir results
python generate_data.py --config datagen.conf && python test_algos.py data 2 results/results.csv && rm -r data results