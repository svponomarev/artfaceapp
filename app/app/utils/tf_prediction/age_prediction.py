#!/usr/bin/env python
# # -*- coding: utf-8 -*-
""" === age_prediction.py: script for exporting age prediction model into pb format === """
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import sys
import shutil

import tensorflow as tf
from model import select_model, get_checkpoint
from data import standardize_image 
from utils import *

RESIZE_FINAL = 227 # final size of input images for neural net
MAX_BATCH_SZ = 128 # maximum number of images in batch

AGE_LIST = ['0 - 2','4 - 6','8 - 12','15 - 20','25 - 32','38 - 43','48 - 53','60 - 100'] 

tf.app.flags.DEFINE_string('model_dir_age', 'models/checkpoints/22801',
                           'Age model directory (where training data lives)')

tf.app.flags.DEFINE_string('device_id', '/cpu:0',
                           'What processing unit to execute inference on')

tf.app.flags.DEFINE_string('checkpoint', 'checkpoint',
                          'Checkpoint basename')

tf.app.flags.DEFINE_string('model_type', 'inception',
                           'Type of convnet')

tf.app.flags.DEFINE_string('output_dir', './age_est-export',
                           """Directory where to export the model.""")

tf.app.flags.DEFINE_integer('model_version', 1,
"""Version number of the model.""")

FLAGS = tf.app.flags.FLAGS

def preprocess_image(image_buffer):
    '''
    Preprocess JPEG encoded bytes to 3D float Tensor and rescales
    it so that pixels are in a range of [-1, 1]
    :param image_buffer: Buffer that contains JPEG image
    :return: 4D image tensor (1, width, height,channels) with pixels scaled
             to [-1, 1]. First dimension is a batch size (1 is our case)
    '''

    # Decode the string as an RGB JPEG.
    # Note that the resulting image contains an unknown height and width
    # that is set dynamically by decode_jpeg. In other words, the height
    # and width of image is unknown at compile-time.
    image = tf.image.decode_jpeg(image_buffer, channels=3)

    # After this point, all image pixels reside in [0,1)
    # until the very end, when they're rescaled to (-1, 1).  The various
    # adjust_* ops all require this range for dtype float.
    image = tf.image.convert_image_dtype(image, dtype=tf.float32)
    
    image = standardize_image(image)

    image = tf.image.resize_images(image, [RESIZE_FINAL, RESIZE_FINAL])

    # Networks accept images in batches.
    # The first dimension usually represents the batch size.
    # In our case the batch size is one.
    image = tf.expand_dims(image, 0)

    return image
   
def main(_):
    
    config = tf.ConfigProto(allow_soft_placement=True)
           
    with tf.Graph().as_default(), tf.Session(config=config) as sess:

        serialized_tf_example = tf.placeholder(tf.string, name='input_image')
        feature_configs = {
            'image/encoded': tf.FixedLenFeature(
                shape=[], dtype=tf.string),
        }
        tf_example = tf.parse_example(serialized_tf_example, feature_configs)
        
        jpegs = tf_example['image/encoded']
        images = tf.map_fn(preprocess_image, jpegs, dtype=tf.float32)
        images = tf.squeeze(images, [0])

        label_list_age = AGE_LIST
        nlabelsa = len(label_list_age)

        model_fn = select_model(FLAGS.model_type)
            
        with tf.device(FLAGS.device_id):
            
            logits = model_fn(nlabelsa, images, 1, False)
            init = tf.global_variables_initializer()
            
            # Restore the model from last checkpoints

            requested_step = None
        
            checkpoint_path = '%s' % (FLAGS.model_dir_age)

            model_checkpoint_path, global_step = get_checkpoint(checkpoint_path, requested_step, FLAGS.checkpoint)
            
            saver = tf.train.Saver()

            saver.restore(sess, model_checkpoint_path)
            
            # Get prediction results
            softmax_output = tf.nn.softmax(logits)

            # (re-)create export director
            export_path = os.path.join(
                tf.compat.as_bytes(FLAGS.output_dir),
                tf.compat.as_bytes(str(FLAGS.model_version)))
            if os.path.exists(export_path):
                shutil.rmtree(export_path)
            
             # create model builder
            builder = tf.saved_model.builder.SavedModelBuilder(export_path)
        
             # create tensors info
            predict_tensor_inputs_info = tf.saved_model.utils.build_tensor_info(jpegs)
            predict_tensor_scores_info = tf.saved_model.utils.build_tensor_info(softmax_output)
            
            # build prediction signature
            prediction_signature = (
                tf.saved_model.signature_def_utils.build_signature_def(
                    inputs={'images': predict_tensor_inputs_info},
                    outputs={'scores': predict_tensor_scores_info},
                    method_name=tf.saved_model.signature_constants.PREDICT_METHOD_NAME
                )
            )

            # save the model
            legacy_init_op = tf.group(tf.tables_initializer(), name='legacy_init_op')
            builder.add_meta_graph_and_variables(
                sess, [tf.saved_model.tag_constants.SERVING],
                signature_def_map={
                    'predict_images': prediction_signature
                },
                legacy_init_op=legacy_init_op)

            builder.save()

            print("Successfully exported AGE-EST model version '{}' into '{}'".format(FLAGS.model_version, FLAGS.output_dir))

if __name__ == '__main__':
    tf.app.run()
