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
"""Tests for melody_pipelines."""

# internal imports
import tensorflow as tf

from magenta.common import testing_lib as common_testing_lib
from magenta.music import constants
from magenta.music import melodies_lib
from magenta.music import sequences_lib
from magenta.music import testing_lib
from magenta.pipelines import melody_pipelines
from magenta.protobuf import music_pb2


NOTE_OFF = constants.MELODY_NOTE_OFF
NO_EVENT = constants.MELODY_NO_EVENT


class MelodyPipelinesTest(tf.test.TestCase):

  def _unit_transform_test(self, unit, input_instance,
                           expected_outputs):
    outputs = unit.transform(input_instance)
    self.assertTrue(isinstance(outputs, list))
    common_testing_lib.assert_set_equality(self, expected_outputs, outputs)
    self.assertEqual(unit.input_type, type(input_instance))
    if outputs:
      self.assertEqual(unit.output_type, type(outputs[0]))

  def testMelodyExtractor(self):
    note_sequence = common_testing_lib.parse_test_proto(
        music_pb2.NoteSequence,
        """
        time_signatures: {
          numerator: 4
          denominator: 4}
        tempos: {
          qpm: 60}""")
    testing_lib.add_track_to_sequence(
        note_sequence, 0,
        [(12, 100, 2, 4), (11, 1, 6, 7)])
    testing_lib.add_track_to_sequence(
        note_sequence, 1,
        [(12, 127, 2, 4), (14, 50, 6, 8)])
    quantized_sequence = sequences_lib.quantize_note_sequence(
        note_sequence, steps_per_quarter=1)
    expected_events = [
        [NO_EVENT, NO_EVENT, 12, NO_EVENT, NOTE_OFF, NO_EVENT, 11],
        [NO_EVENT, NO_EVENT, 12, NO_EVENT, NOTE_OFF, NO_EVENT, 14, NO_EVENT]]
    expected_melodies = []
    for events_list in expected_events:
      melody = melodies_lib.Melody(
          events_list, steps_per_quarter=1, steps_per_bar=4)
      expected_melodies.append(melody)
    unit = melody_pipelines.MelodyExtractor(
        min_bars=1, min_unique_pitches=1, gap_bars=1)
    self._unit_transform_test(unit, quantized_sequence, expected_melodies)


if __name__ == '__main__':
  tf.test.main()
