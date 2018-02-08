#!/bin/bash

rm -rf data
mkdir data
python generate_data.py --config datagen.conf && python test_algos.py data 2 && rm -r data