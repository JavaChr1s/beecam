FROM ubuntu:20.04
LABEL version=1.1

#RUN pip3 install pycoral
#RUN pip3 install --index-url https://google-coral.github.io/py-repo/ tflite_runtime
#RUN pip3 install imutils

RUN apt-get update
RUN apt-get install curl gnupg2 -y

# installs Tensorflow Lite And Google Coral Edge TPU
RUN echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | tee /etc/apt/sources.list.d/coral-edgetpu.list \
    && echo "deb https://packages.cloud.google.com/apt coral-cloud-stable main" | tee /etc/apt/sources.list.d/coral-cloud.list \
    && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add - \
    && apt-get update \
    && apt-get install -y python3-pycoral python3-tflite-runtime python3-distutils

RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py \
	&& python3 get-pip.py \
	&& rm get-pip.py

RUN pip3 install imutils
RUN pip3 install opencv-python
RUN apt-get install -y ffmpeg

WORKDIR /app/python

ENV PYTHONUNBUFFERED 1

#CMD ["tail","-f","/dev/null"]
CMD ["python3", "object_detection.py"]
