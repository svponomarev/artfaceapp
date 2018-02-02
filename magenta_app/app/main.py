#!/usr/bin/env python
# # -*- coding: utf-8 -*-
""" === magenta_app/app/main.py: script for mantaining Flask server with magenta neural style transfer=== """
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import ast
import os
import time
import base64
import io
import numpy as np
import tensorflow as tf
import scipy
import scipy.misc

from PIL import Image

from flask import Flask, jsonify, request
from magenta.models.arbitrary_image_stylization import arbitrary_image_stylization_build_model as build_model
from magenta.models.image_stylization import image_utils

slim = tf.contrib.slim

checkpoint_path = '/magenta-models/arbitrary_style_transfer/model.ckpt' # path to the learned model for arbitrary style transfer

app = Flask(__name__) # initialize Flask application
app.config.from_object(__name__)

class Transferer:
    def __init__(self, model_path):
        """load neural net in memory"""
        #print("LOAD NEURAL")
        # Note, if you don't want to leak this, you'll want to turn Model into
        # a context manager. In practice, you probably don't have to worry
        # about it.
        self.session = tf.Session()
        # Defines place holder for the style image.
        self.style_img_ph = tf.placeholder(tf.float32, shape=[None, None, 3], name="style_img_ph")
        style_img_preprocessed = image_utils.resize_image(self.style_img_ph, 256) # resize style image to smallest side equal 256 px
        # Defines place holder for the content image.
        self.content_img_ph = tf.placeholder(tf.float32, shape=[None, None, 3], name="content_img_ph")
        content_img_preprocessed = tf.to_float(self.content_img_ph) / 255.0
        content_img_preprocessed = tf.expand_dims(content_img_preprocessed, 0)
        #content_img_preprocessed = image_utils.resize_image(self.content_img_ph, 384) # don't resize content image, input image is already resized
        # Defines the model.
        self.stylized_images, _, _, self.bottleneck_feat = build_model.build_model(
            content_img_preprocessed,
            style_img_preprocessed,
            trainable=False,
            is_training=False,
            inception_end_point='Mixed_6e',
            style_prediction_bottleneck=100,
            adds_losses=False)
        if tf.gfile.IsDirectory(model_path):
          checkpoint = tf.train.latest_checkpoint(model_path)
        else:
          checkpoint = model_path
          tf.logging.info('loading latest checkpoint file: {}'.format(checkpoint))

        self.session.run([tf.local_variables_initializer()])
        
        init_fn = slim.assign_from_checkpoint_fn(checkpoint,
                                             slim.get_variables_to_restore())
        init_fn(self.session)

        
    def transfer(self, content_image, style_image):
        """transfer style with running net for specific images"""
        image_bytes = io.BytesIO(base64.b64decode(content_image))
        im = Image.open(image_bytes)
        content_img_np = np.array(im)[:, :, : 3]

        style_bytes = io.BytesIO(base64.b64decode(style_image))
        st = Image.open(style_bytes)
        style_img_np = np.array(st)[:, :, : 3]

        style_params = self.session.run(self.bottleneck_feat, feed_dict={self.style_img_ph: style_img_np})
        stylized_image_res = self.session.run(self.stylized_images, feed_dict={
                                                   self.bottleneck_feat:
                                                       style_params,
                                                   self.content_img_ph:
                                                       content_img_np
                                                         }
                             )
        # save stylized image.
        image = np.uint8(stylized_image_res * 255.0)
        buf = io.BytesIO()
        scipy.misc.imsave(buf, np.squeeze(image, 0), format='jpeg')
        buf.seek(0)
          
        return base64.b64encode(buf.getvalue()).decode("utf-8") # returns image in form of base64 encoded string

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' # disable warnings for tensorflow

@app.before_first_request
def add_transferer_to_globals():
    global tr
    tr = Transferer(checkpoint_path) # load neural net in memory and wait for post requests with images

@app.route('/',  methods=['GET', 'POST'])
def style_transfer():
    """ stylize content image from post request using specific style image"""
    dataToReturn = {'Error':'Failed to process POST request'}
    if request.method == "POST":
        input_json = request.get_json(force=True)
        content_img = input_json['content_img']
        style_img = input_json['style_img']

        # Generate stylized images for these content and style images
        t = time.time()
        out_img = tr.transfer(content_img, style_img)
        dt = time.time() - t

        dataToReturn = {'Processing time':dt * 1000., 'out_img' : out_img}
    
        #app.logger.info("Execution time: %0.2f" % (dt * 1000.))

    return jsonify(dataToReturn)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=6006) # start Flask server on specific port
