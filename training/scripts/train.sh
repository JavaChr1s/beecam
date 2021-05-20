#!/bin/bash

mkdir temp

echo "Generating TFRecord for training objects..."
python3 xml_to_csv.py /training/images/train/ TRAINING

echo "Generating TFRecord for testing objects..."
python3 xml_to_csv.py /training/images/test/ TEST

echo "Start training..."
python3 train.py
echo "Training done!"

echo "Cleaning temp files"
rm temp -R

echo "DONE!"