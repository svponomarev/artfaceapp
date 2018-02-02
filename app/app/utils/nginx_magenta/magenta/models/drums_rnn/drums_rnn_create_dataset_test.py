# Copyright 2016 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Tests for drums_rnn_create_dataset."""

# internal imports
import tensorflow as tf
import magenta

from magenta.models.drums_rnn import drums_rnn_create_dataset
from magenta.models.shared import events_rnn_model
from magenta.pipelines import drum_pipelines
from magenta.pipelines import note_sequence_pipelines
from magenta.protobuf import music_pb2


FLAGS = tf.app.flags.FLAGS


class DrumsRNNPipelineTest(tf.test.TestCase):

  def setUp(self):
    self.config = events_rnn_model.EventSequenceRnnConfig(
        None,
        magenta.music.OneHotEventSequenceEncoderDecoder(
            magenta.music.MultiDrumOneHotEncoding()),
        tf.contrib.training.HParams())

  def testDrumsRNNPipeline(self):
    note_sequence = magenta.common.testing_lib.parse_test_proto(
        music_pb2.NoteSequence,
        """
        time_signatures: {
          numerator: 4
          denominator: 4}
        tempos: {
          qpm: 120}""")
    magenta.music.testing_lib.add_track_to_sequence(
        note_sequence, 0,
        [(36, 100, 0.00, 2.0), (40, 55, 2.1, 5.0), (44, 80, 3.6, 5.0),
         (41, 45, 5.1, 8.0), (64, 100, 6.6, 10.0), (55, 120, 8.1, 11.0),
         (39, 110, 9.6, 9.7), (53, 99, 11.1, 14.1), (51, 40, 12.6, 13.0),
         (55, 100, 14.1, 15.0), (54, 90, 15.6, 17.0), (60, 100, 17.1, 18.0)],
        is_drum=True)

    quantizer = note_sequence_pipelines.Quantizer(steps_per_quarter=4)
    drums_extractor = drum_pipelines.DrumsExtractor(min_bars=7, gap_bars=1.0)
    one_hot_encoding = magenta.music.OneHotEventSequenceEncoderDecoder(
        magenta.music.MultiDrumOneHotEncoding())
    quantized = quantizer.transform(note_sequence)[0]
    drums = drums_extractor.transform(quantized)[0]
    one_hot = one_hot_encoding.encode(drums)
    expected_result = {'training_drum_tracks': [one_hot],
                       'eval_drum_tracks': []}

    pipeline_inst = drums_rnn_create_dataset.get_pipeline(self.config,
                                                          eval_ratio=0.0)
    result = pipeline_inst.transform(note_sequence)
    self.assertEqual(expected_result, result)


if __name__ == '__main__':
  tf.test.main()
