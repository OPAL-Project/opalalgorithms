#!/bin/bash

rm -rf data
mkdir data
python generate_data.py --config datagen.conf && pytest && rm -r data