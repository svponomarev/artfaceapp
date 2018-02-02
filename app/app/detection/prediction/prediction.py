#!/usr/bin/env python
# # -*- coding: utf-8 -*-
""" === prediction.py: script for prediction of age & gender by face image using tensorflow serving === """
from __future__ import print_function

import numpy as np
import tensorflow as tf
import gc

# Communication to TensorFlow server via gRPC
from grpc.beta import implementations
# TensorFlow serving stuff to send messages
from tensorflow_serving.apis import predict_pb2
from tensorflow_serving.apis import prediction_service_pb2

# Command line arguments
tf.app.flags.DEFINE_string('prediction_server', '172.18.0.12:9000',
                           'PredictionService host:port')
FLAGS = tf.app.flags.FLAGS

AGE_LIST = ['0-2','4-6','8-12','15-20','25-32','38-43','48-53','60-100'] # intervals for predicted age
GENDER_LIST =['Male','Female'] # labels for predicted gender

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
        

def params_prediction(img_path):
    """predicts age and gender of person using input image with cropped face rectangle"""
    host, port = FLAGS.prediction_server.split(':')
    client = TensorflowServingClient(host, int(port))

    # Send request
    with open(img_path, 'rb') as f:
        data = f.read()     
        age_probs = client.make_prediction(data, 'images', 60.0, 'age')["scores"].float_val
        best_index = np.argmax(age_probs)
        age = AGE_LIST[best_index]
        age_prob = age_probs[best_index]

        gender_probs = client.make_prediction(data, 'images', 60.0, 'gender')["scores"].float_val
        best_index = np.argmax(gender_probs)
        gender = GENDER_LIST[best_index]
        gender_prob = gender_probs[best_index]
        
        return (age, age_prob, gender, gender_prob) 
   
