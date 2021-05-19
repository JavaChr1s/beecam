# Lint as: python3
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#	 https://www.apache.org/licenses/LICENSE-2.0

# Based on https://github.com/google-coral/tflite/blob/master/python/examples/detection/detect_image.py
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os
import sys
# sys.path.append(os.path.dirname("{os.getcwd()}/notif"))
# sys.path.append(os.path.dirname("{os.getcwd()}/utils"))
# sys.path.append(os.path.dirname("{os.getcwd()}"))

import random
import datetime
import numpy as np
import cv2
import time
import argparse
import logging

import tflite_runtime.interpreter as tflite

import json

EDGETPU_SHARED_LIB="libedgetpu.so.1"

def setupLogger():
	# create logger with 'spam_application'
	myLogger = logging.getLogger('analyzer')
	myLogger.setLevel(logging.INFO)
	# create console handler with a higher log level
	ch = logging.StreamHandler()
	ch.setLevel(logging.INFO)
	# create formatter and add it to the handlers
	formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	ch.setFormatter(formatter)
	# add the handlers to the logger
	myLogger.addHandler(ch)
	return myLogger

def findFileWithExtension(extension,dir_path):
	labelFile = None
	for f in os.listdir(dir_path):
		# List files with .py
		if f.endswith(extension):
			labelFile = os.path.join(dir_path, f)
			break
	return labelFile
	
def load_labels(modelDir, encoding='utf-8'):

	"""Loads labels from file (with or without index numbers).
	Args:
	modelDir: path to directory containing model.
	encoding: label file encoding.
	Returns:
	Dictionary mapping indices to labels.
	"""
	label_file = findFileWithExtension(".txt", modelDir)
	with open(label_file, 'r', encoding=encoding) as f:
		lines = f.readlines()
	if not lines:
		return {}

	category_index = {}
	for index, label in enumerate(lines):
		category = { "id": index, "name": label }
		category_index[index] = category
	return category_index

def make_interpreter(model_dir, enable_tpu):
	model_file = findFileWithExtension(".tflite", model_dir)
	model_file, *device = model_file.split('@')
	print(f"device={device}")
	# is edgetpu enabled
	if enable_tpu:
		return tflite.Interpreter(
			model_path=model_file,
			experimental_delegates=[
				tflite.load_delegate(EDGETPU_SHARED_LIB,
									 {'device': device[0]} if device else {})
			])
	else:
		return tflite.Interpreter(
			model_path=model_file
		)


def main():
	parser = argparse.ArgumentParser(
		formatter_class=argparse.ArgumentDefaultsHelpFormatter)


	parser.add_argument('-t', '--threshold', type=float, default=0.5,
						help='Score threshold for detected objects.')
	parser.add_argument('-c', '--count', type=int, default=5,
						help='Number of times to run inference')
	parser.add_argument('-tpu', '--enable-tpu', action='store_true',
						help='Whether TPU is enabled or not')
	parser.add_argument('-objects', '--detect-objects', type=str, default="bird")
	parser.add_argument('-debug', '--enable-debug', action='store_true',
						help='Whether Debug is enabled or not - Webcamera viewed is displayed when in this mode')

	parser.add_argument("-cslack", "--clear-slack-files", action='store_true',
					help="clears files in slack")

	parser.add_argument("-slack", "--slack-credentials", type=str, default="config.ini",
					help="path to optional slack configuration")

	args = parser.parse_args()


	objects_to_detect = args.detect_objects

	model_dir = "/app/models"

	labels = load_labels(model_dir)

	interpreter = make_interpreter(model_dir, args.enable_tpu)

	interpreter.allocate_tensors()

	# Get model details
	input_details = interpreter.get_input_details()
	output_details = interpreter.get_output_details()
	height = input_details[0]['shape'][1]
	width = input_details[0]['shape'][2]

	floating_model = (input_details[0]['dtype'] == np.float32)

	input_mean = 127.5
	input_std = 127.5
	
	
	results = {}
	for attr, value in labels.items():
		result = {"id": attr, "name": value.get("name"), "value": 0}
		results[attr] = result
	
	frame_count = 0
	
	debug_threshold = 0.5
	
	input_folder = "/app/input"
	input_filename = "smurf_input.avi"
	done_folder = "/app/done"
	cap = cv2.VideoCapture(input_folder + "/" + input_filename)
# Loop over every image and perform detection
	start_time = time.time()
	while(cap.isOpened()):
		start_time_frame = time.time()
		ret, image = cap.read()
		if not	ret:
			print("end of the video file...")
			break
			
		frame_count = frame_count+1

		image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
		imH, imW, _ = image.shape 
		image_resized = cv2.resize(image_rgb, (width, height))
		input_data = np.expand_dims(image_resized, axis=0)

		# Normalize pixel values if using a floating model (i.e. if model is non-quantized)
		if floating_model:
			input_data = (np.float32(input_data) - input_mean) / input_std

		# Perform the actual detection by running the model with the image as input
		interpreter.set_tensor(input_details[0]['index'],input_data)
		interpreter.invoke()

		# Retrieve detection results
		boxes = interpreter.get_tensor(output_details[0]['index'])[0] # Bounding box coordinates of detected objects
		classes = interpreter.get_tensor(output_details[1]['index'])[0] # Class index of detected objects
		scores = interpreter.get_tensor(output_details[2]['index'])[0] # Confidence of detected objects
		#num = interpreter.get_tensor(output_details[3]['index'])[0]	# Total number of detected objects (inaccurate and not needed)

		# initialize frame results
		frameResults = {}
		for index, value in enumerate(classes):
			if value in results:
				frameResults[value] = 0

		# check frame for results
		for index, value in enumerate(classes):
			if value in results:
				if scores[index] > debug_threshold:
					print ("debug: ", (results[value]["name"] + ": "), scores[index])
	
				if scores[index] > args.threshold:
					frameResults[value] = (frameResults[value] + 1)
	
		# add frame results to global results
		for attr, value in frameResults.items():
			if results[attr]["value"] < value:
				results[attr]["value"] = value

		for attr, result in results.items():
			if result["value"] > 0:
				print ((result["name"] + ": "), result["value"])

		print ("speed: " + str(1 / (time.time() - start_time_frame)) + " fps")
	
	cap.release()
	cv2.destroyAllWindows()

	print ("Moved file " + input_filename + " to " + done_folder)
	os.rename(input_folder + "/" + input_filename, done_folder + "/" + input_filename)

	elapsed_time = time.time() - start_time
	print('Object detection done! Elapsed time: ' + str(elapsed_time) + 's, number of frames: ' + str(frame_count) + ', fps: ' + str(frame_count / elapsed_time))

if __name__ == '__main__':
	logger = setupLogger()
	main()

































