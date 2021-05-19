FROM "nvidia/cuda:11.2.0-cudnn8-runtime-ubuntu20.04"
RUN apt-get update && yes | apt-get upgrade
RUN mkdir -p /tensorflow/models
RUN apt-get install -y git python3-pip
RUN pip3 install --upgrade pip
RUN pip3 install tflite-model-maker
RUN pip3 install pycocotools

RUN mkdir /training/scripts -p

COPY scripts /training/scripts

WORKDIR /training/scripts

CMD ["./train.sh"]
#CMD ["tail","-f","/dev/null"]