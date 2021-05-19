import numpy as np
import os

from tflite_model_maker.config import ExportFormat
from tflite_model_maker import model_spec
from tflite_model_maker import object_detector

import tensorflow as tf
assert tf.__version__.startswith('2')

tf.get_logger().setLevel('ERROR')
from absl import logging
logging.set_verbosity(logging.ERROR)

spec = model_spec.get('efficientdet_lite2')

train_data = object_detector.DataLoader.from_csv("temp/TRAINING_labels.csv", "/training/images/train",",","\\",10)[0]
test_data = object_detector.DataLoader.from_csv("temp/TEST_labels.csv", "/training/images/test",",","\\",10)[2]

print ("Creating model...")
model = object_detector.create(train_data, model_spec=spec, batch_size=8, train_whole_model=True, do_train=True)

print ("Evaluating...")
result = model.evaluate(test_data)
print (result)

print ("Exporting...")
model.export(export_dir='/training/model', export_format=[ExportFormat.TFLITE, ExportFormat.LABEL]) #ExportFormat.SAVED_MODEL

print ("Evaluating tflite...")
result = model.evaluate_tflite('/training/model/model.tflite', test_data)
print (result)
