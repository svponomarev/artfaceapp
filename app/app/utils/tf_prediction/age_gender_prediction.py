#!/usr/bin/env python
# # -*- coding: utf-8 -*-
""" === age_gender_prediction.py: script for exporting age/gender prediction model into pb format === """
import os
import tensorflow as tf
import numpy as np

from model import select_model, get_checkpoint
from tensorflow.python.framework import graph_util
from tensorflow.contrib.learn.python.learn.utils import export
from tensorflow.python.saved_model import builder as saved_model_builder
from tensorflow.python.saved_model import signature_constants
from tensorflow.python.saved_model import signature_def_utils
from tensorflow.python.saved_model import tag_constants
from tensorflow.python.saved_model import utils

import inception_resnet_v1

RESIZE_FINAL = 160 # final sizes for face rectangles

tf.app.flags.DEFINE_string('checkpoint', 'savedmodel',
                           'Checkpoint basename')

tf.app.flags.DEFINE_string('model_dir', './models',
                           'Model directory (where training data lives)')

tf.app.flags.DEFINE_integer('model_version', 1,
                            """Version number of the model.""")

tf.app.flags.DEFINE_string('output_dir', './export_model/',
                           'Export directory')

FLAGS = tf.app.flags.FLAGS

def preproc_jpeg(image_buffer):
    '''
    Preprocess JPEG encoded bytes to 3D float Tensor and rescales
    it so that pixels are in a range of [-1, 1]
    :param image_buffer: Buffer that contains JPEG image
    :return: 4D image tensor (1, width, height,channels) with pixels scaled
             to [-1, 1]. First dimension is a batch size (1 is our case)
    '''
    image = tf.image.decode_jpeg(image_buffer, channels=3)
    crop = tf.image.resize_images(image, (RESIZE_FINAL, RESIZE_FINAL))    
    image_out = tf.image.per_image_standardization(crop)
    return image_out

def main(argv=None):
    with tf.Graph().as_default():

        serialized_tf_example = tf.placeholder(tf.string, name='tf_example')
        feature_configs = {
            'image/encoded': tf.FixedLenFeature(shape=[], dtype=tf.string),
        }
        tf_example = tf.parse_example(serialized_tf_example, feature_configs)
        jpegs = tf_example['image/encoded']

        images = tf.map_fn(preproc_jpeg, jpegs, dtype=tf.float32)
        
        config = tf.ConfigProto(allow_soft_placement=True)
        with tf.Session(config=config) as sess:
            # Get prediction results
            age_logits, gender_logits, _ = inception_resnet_v1.inference(images, keep_probability=0.8,
            phase_train=False,
            weight_decay=1e-5)
            gender = tf.argmax(tf.nn.softmax(gender_logits), 1)
            gender_certainty = tf.reduce_max(tf.nn.softmax(gender_logits))
            gender = tf.reshape(gender, gender_certainty.get_shape()) 

            age_ = tf.cast(tf.constant([i for i in range(0, 101)]), tf.float32)
            age = tf.reduce_sum(tf.multiply(tf.nn.softmax(age_logits), age_), axis=1)
            age_certainty = 1 - tf.reduce_max(tf.nn.softmax(age_logits))
            age = tf.reshape(age, age_certainty.get_shape()) 

            gender = tf.cast(gender, tf.float32)
            values = tf.stack([age, age_certainty, gender, gender_certainty], axis=0)

            init_op = tf.group(tf.global_variables_initializer(),
            tf.local_variables_initializer())
            sess.run(init_op)
            checkpoint_path = '%s' % (FLAGS.model_dir)
            model_checkpoint_path, global_step = get_checkpoint(checkpoint_path, None, FLAGS.checkpoint)
            
            # Restore the model from last checkpoints
            saver = tf.train.Saver()
            saver.restore(sess, model_checkpoint_path)
            print('Restored model checkpoint %s' % model_checkpoint_path)

            output_path = os.path.join(
                tf.compat.as_bytes(FLAGS.output_dir),
                tf.compat.as_bytes(str(FLAGS.model_version)))
            print('Exporting trained model to %s' % output_path)

            # create model builder
            builder = tf.saved_model.builder.SavedModelBuilder(output_path)

            # Build the signature_def_map.
            classify_inputs_tensor_info = tf.saved_model.utils.build_tensor_info(
                serialized_tf_example)
            scores_output_tensor_info = tf.saved_model.utils.build_tensor_info(values)
            classification_signature = (
                tf.saved_model.signature_def_utils.build_signature_def(
                    inputs={
                        tf.saved_model.signature_constants.CLASSIFY_INPUTS:
                    classify_inputs_tensor_info
                    },
                    outputs={
                        tf.saved_model.signature_constants.CLASSIFY_OUTPUT_SCORES:
                        scores_output_tensor_info
                    },
                    method_name=tf.saved_model.signature_constants.
                    CLASSIFY_METHOD_NAME))
            
            
            predict_inputs_tensor_info = tf.saved_model.utils.build_tensor_info(jpegs)
            prediction_signature = (
                tf.saved_model.signature_def_utils.build_signature_def(
                    inputs={'images': predict_inputs_tensor_info},
                    outputs={
                        'scores': scores_output_tensor_info
                    },
                    method_name=tf.saved_model.signature_constants.PREDICT_METHOD_NAME
                ))

            # save the model
            legacy_init_op = tf.group(tf.tables_initializer(), name='legacy_init_op')
            builder.add_meta_graph_and_variables(
                sess, [tf.saved_model.tag_constants.SERVING],
                signature_def_map={
                    'predict_images':
                    prediction_signature,
                    tf.saved_model.signature_constants.
                    DEFAULT_SERVING_SIGNATURE_DEF_KEY:
                    classification_signature,
                },
                legacy_init_op=legacy_init_op)
            
            builder.save()
            print('Successfully exported model to %s' % FLAGS.output_dir)

if __name__ == '__main__':
    tf.app.run()
