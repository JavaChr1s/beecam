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
import shutil
import tflite_runtime.interpreter as tflite

import traceback
import logging

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
		category = { "id": index, "name": label.replace('\n','') }
		category_index[index] = category
	return category_index

def make_interpreter(model_dir, num_threads):
	model_file = findFileWithExtension(".tflite", model_dir)
	model_file, *device = model_file.split('@')
	print(f"threads={num_threads}")
	return tflite.Interpreter(
		model_path=model_file,
		num_threads=num_threads
	)
	
def change_file_permission(file_path):
	os.system('chmod -R 777 "' + file_path + '"')


def main():
	num_threads = 1
	if os.getenv('OBJECT_DETECTION_THREADS'):
		num_threads = int(os.getenv('OBJECT_DETECTION_THREADS'))
		
	model_dir = "/app/models"
	
	general_frames_folder = True
	draw_box = True
	
	threshold = 0.7
	debug_threshold = 0.5
	
	input_folder = "/app/input"
	error_folder = "/app/error"
	done_folder = "/app/done"
	output_folder = "/app/output"
	output_file = output_folder + "/detected_objects.csv"
	
	with open('/app/config.json') as config_file:
		config = json.load(config_file)
		general_frames_folder = config["general_frames_folder"]
		draw_box = config["draw_box"]
		threshold = config["threshold"]
		debug_threshold = config["debug_threshold"]
		input_folder = config["input_folder"]
		done_folder = config["done_folder"]
		error_folder = config["error_folder"]
		output_folder = config["output_folder"]
		model_dir = config["model_dir"]
		if config["threads"]:
			num_threads = config["threads"]
		
	print ("general_frames_folder: ", general_frames_folder)
	print ("draw_box: ", draw_box)
	print ("threshold: ", threshold)
	print ("debug_threshold: ", debug_threshold)
	print ("input_folder: ", input_folder)
	print ("done_folder: ", done_folder)
	print ("error_folder: ", error_folder)
	print ("output_folder: ", output_folder)
	print ("model_dir: ", model_dir)
		
	labels = load_labels(model_dir)

	interpreter = make_interpreter(model_dir, num_threads)
	interpreter.allocate_tensors()

	# Get model details
	input_details = interpreter.get_input_details()
	output_details = interpreter.get_output_details()
	height = input_details[0]['shape'][1]
	width = input_details[0]['shape'][2]

	floating_model = (input_details[0]['dtype'] == np.float32)

	input_mean = 127.5
	input_std = 127.5
	
	print ("Tool loaded!")

	while True:
		for input_filename in os.listdir(input_folder):
			try:
				input_file = os.path.join(input_folder, input_filename)
				if os.path.isfile(input_file) and input_file.endswith(".mp4"):

					movie = input_filename.split(".")[0]

					movie_date = None
					movie_time = None
					if "__" in movie:
						movie_date = movie.split("__")[0]
						movie_time = movie.split("__")[1]
			
					results = {}
					for attr, value in labels.items():
						result = {"id": attr, "name": value.get("name"), "value": 0, "frames": 0 }
						results[attr] = result
					
					cap = cv2.VideoCapture(input_file)
				# Loop over every image and perform detection
					start_time = time.time()
					frame_count = 0
					multiple_results_on_one_frame = False
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
								classification = results[value]["name"]
								if scores[index] > debug_threshold:
									print ("debug: ", (classification + ": "), scores[index])
					
								if scores[index] > threshold:
									frameResults[value] = (frameResults[value] + 1)								
									if draw_box:
										ymin, xmin, ymax, xmax = boxes[index]
										xmin = int(xmin * image.shape[1])
										xmax = int(xmax * image.shape[1])
										ymin = int(ymin * image.shape[0])
										ymax = int(ymax * image.shape[0])
										
										color = (0, 155, 0)
										cv2.rectangle(image, (xmin, ymin), (xmax, ymax), color, 2)

										y = ymin - 15 if ymin - 15 > 15 else ymin + 15
										label = "{}: {:.0f}%".format(classification, scores[index] * 100)
										cv2.putText(image, label, (xmin, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
									frame_folder = output_folder
									frame_filename = str(frame_count) 
									if general_frames_folder:
										frame_folder = frame_folder + "/frames/" + movie
										frame_filename = frame_filename + "__" + classification + "_" + str(int(scores[index] * 100))
									else:
										frame_folder = frame_folder + "/" + classification
										frame_filename = movie + "__" + frame_filename
									if not os.path.exists(frame_folder):
										os.makedirs(frame_folder)
										change_file_permission(frame_folder)
									frame_path = os.path.join(frame_folder, frame_filename + ".jpg")
									cv2.imwrite(frame_path, image)
									change_file_permission(frame_path)
									print ("Frame saved to ", frame_path)
					
						results_on_frame = 0
						for attr, value in frameResults.items():
							results_on_frame = results_on_frame + value
						if results_on_frame > 1:
							multiple_results_on_one_frame = True
							print ("found multiple results on this frame: " + str(frameResults) + str(len (frameResults)))

						# add frame results to global results
						for attr, value in frameResults.items():
							if results[attr]["value"] < value:
								results[attr]["value"] = value
							if value > 0:
								results[attr]["frames"] = results[attr]["frames"] + value

						for attr, result in results.items():
							if result["value"] > 0:
								print ((result["name"] + ": "), result["value"])

						print ("speed: " + str(1 / (time.time() - start_time_frame)) + " fps")
					
					cap.release()
					cv2.destroyAllWindows()

					# flatten results
					flattened_result = None
					if not multiple_results_on_one_frame:
						max_result = { 'frames': 0 }
						for attr, value in labels.items():
							if results[attr].get("frames") > max_result.get("frames"):
								max_result = results[attr]
						if max_result.get("frames") > 0:
							flattened_result = max_result
						print ("flatten results " + str(results) + " since there was only one result per frame: " + str(flattened_result.get("name")))

					
					# write csv header
					if not os.path.isfile(output_file):
						with open(output_file, "x") as output:
							line = "file;date;time;sum"
							for attr, value in labels.items():
								line = line + ";" + str(results[attr].get("name"))
							output.write(line)
						change_file_permission(output_file)
					
					objects_found = 0

					# write csv values
					with open(output_file, "a") as output:
						line = "\n" + input_filename + ";" + movie_date + ";" + movie_time
						values = ""
						for attr, value in labels.items():
							result = 0
							if flattened_result is None:
								result = results[attr].get("value")
							elif results[attr].get("name") == flattened_result.get("name"):
								result = 1
							values = values + ";" + str(result)
							objects_found = objects_found + result
						line = line + ";" + str(objects_found) + values
						output.write(line)
					
					# Move output frames into classified folders
					classification = "unspecific"
					if flattened_result is not None:
						classification = flattened_result.get("name")
					classified_frame_path = output_folder + "/frames/"
					if movie_date is not None:
						classified_frame_path = classified_frame_path + movie_date + "/"
					classified_frame_path = classified_frame_path + classification
					if not os.path.exists(classified_frame_path):
						os.makedirs(classified_frame_path)
						change_file_permission(classified_frame_path)
					shutil.move(frame_folder, classified_frame_path + "/" + movie)
					change_file_permission(classified_frame_path + "/" + movie)
					
					# Move movie into positive/negative folders
					target_path = done_folder
					if objects_found > 0:
						target_path = target_path + "/positive/"
					else:
						target_path = target_path + "/negative/"
					if not os.path.exists(target_path):
						os.mkdir(target_path)
						change_file_permission(target_path)
					shutil.move(input_folder + "/" + input_filename, target_path + input_filename)
					change_file_permission(target_path + input_filename)
					print ("Moved file " + input_filename + " to " + target_path)

					# log statistics
					elapsed_time = time.time() - start_time
					print('Object detection done! Elapsed time: ' + str(elapsed_time) + 's, number of frames: ' + str(frame_count) + ', fps: ' + str(frame_count / elapsed_time))
			except Exception as e:
				print("There was an error while analyzing file " + input_filename)
				logging.error(traceback.format_exc())
				shutil.move(input_folder + "/" + input_filename, error_folder + "/" + input_filename)
				change_file_permission(error_folder + "/" + input_filename)
				print ("Moved file " + input_filename + " to " + error_folder + "/")
		time.sleep(1)

if __name__ == '__main__':
	logger = setupLogger()
	main()

































