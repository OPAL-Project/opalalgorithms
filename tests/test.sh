#!/bin/bash

rm -rf data
mkdir data
python generate_data.py --config datagen.conf && python test_algos.py data 3 5 && rm -r data