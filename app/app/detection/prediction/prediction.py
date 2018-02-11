#!/usr/bin/env python
# # -*- coding: utf-8 -*-
""" === prediction.py: script for prediction of age & gender by face image using tensorflow serving === """
from __future__ import print_function
import os
import gc
import cv2
import dlib
import numpy as np
import tensorflow as tf

# Communication to TensorFlow server via gRPC
from grpc.beta import implementations
# TensorFlow serving stuff to send messages
from tensorflow_serving.apis import predict_pb2
from tensorflow_serving.apis import prediction_service_pb2

from imutils.face_utils import rect_to_bb

# Command line arguments
tf.app.flags.DEFINE_string('prediction_server', '172.18.0.12:9000',
                           'PredictionService host:port')
FLAGS = tf.app.flags.FLAGS

def get_dlib_largest_rect(rects):
    largest = 0
    max_area = 0
    rect_nums = len(rects)
    for i in range(rect_nums):
        (x, y, w, h) = rect_to_bb(rects[i])
        area = w * h
        if area > max_area:
            max_area = area
            largest = i
    return largest

def copy_message(src, dst):
    """
    Copy the contents of a src proto message to a destination proto message via string serialization
    :param src: Source proto
    :param dst: Destination proto
    :return:
    """
    dst.ParseFromString(src.SerializeToString())
    return dst

class TensorflowServingClient(object):

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.channel = implementations.insecure_channel(self.host, self.port)
        self.stub = prediction_service_pb2.beta_create_PredictionService_stub(self.channel)

    def execute(self, request, timeout=10.0):
        return self.stub.Predict(request, timeout)

    def make_prediction(self, input_data, input_tensor_name, timeout=10.0, model_name=None):
        request = predict_pb2.PredictRequest()
        request.model_spec.name = model_name or 'model'
        request.model_spec.signature_name = 'predict_images'
        copy_message(tf.contrib.util.make_tensor_proto(input_data, shape=[1]), request.inputs[input_tensor_name])
        response = self.execute(request, timeout=timeout)
        return response.outputs

    def __exit__(self, exc_type, exc_value, traceback):
        del self.channel
        del self.stub
        self.channel = None
        self.stub = None
        gc.collect()
        

def params_prediction(img_path, img_crop_path, face_aligner):
    """predicts age and gender of person using input image with cropped face rectangle"""
    # trying to detect face with dlib and process it for neural net
    detector = dlib.get_frontal_face_detector()
    imagecv = cv2.imread(img_path, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(imagecv, cv2.COLOR_BGR2GRAY)
    rects = detector(gray, 2)
    rect_nums = len(rects)
    if rect_nums != 0:
        largest = get_dlib_largest_rect(rects) # get face rectangle with the biggest area (dlib)
        aligned_image = face_aligner.align(imagecv, gray, rects[largest]) 
        cv2.imwrite(img_crop_path, aligned_image) # cropping image to save only face rectangle for age/gender prediction

    host, port = FLAGS.prediction_server.split(':')
    client = TensorflowServingClient(host, int(port))
    # Send request
    with open(img_crop_path, 'rb') as f:
        data = f.read()     
        scores = client.make_prediction(data, 'images', 60.0, 'age_gender')["scores"].float_val
        age = int(scores[0])
        age_prob = scores[1]
        if int(scores[2]) == 0:
            gender = 'Female'
        else:
            gender = 'Male'
        gender_prob = scores[3]
        return (age, age_prob, gender, gender_prob) 
   
