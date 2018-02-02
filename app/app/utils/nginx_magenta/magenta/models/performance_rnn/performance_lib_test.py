# Copyright 2017 Google Inc. All Rights Reserved.
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
"""Tests for performance_lib."""

# internal imports
import tensorflow as tf

from magenta.models.performance_rnn import performance_lib
from magenta.music import sequences_lib
from magenta.music import testing_lib
from magenta.protobuf import music_pb2


class PerformanceLibTest(tf.test.TestCase):

  def setUp(self):
    self.maxDiff = None

    self.note_sequence = music_pb2.NoteSequence()
    self.note_sequence.ticks_per_quarter = 220

  def testFromQuantizedNoteSequence(self):
    testing_lib.add_track_to_sequence(
        self.note_sequence, 0,
        [(60, 100, 0.0, 4.0), (64, 100, 0.0, 3.0), (67, 100, 1.0, 2.0)])
    quantized_sequence = sequences_lib.quantize_note_sequence_absolute(
        self.note_sequence, steps_per_second=100)
    performance = list(performance_lib.Performance(quantized_sequence))

    pe = performance_lib.PerformanceEvent
    expected_performance = [
        pe(pe.NOTE_ON, 60),
        pe(pe.NOTE_ON, 64),
        pe(pe.TIME_SHIFT, 100),
        pe(pe.NOTE_ON, 67),
        pe(pe.TIME_SHIFT, 100),
        pe(pe.NOTE_OFF, 67),
        pe(pe.TIME_SHIFT, 100),
        pe(pe.NOTE_OFF, 64),
        pe(pe.TIME_SHIFT, 100),
        pe(pe.NOTE_OFF, 60),
    ]
    self.assertEqual(expected_performance, performance)

  def testFromQuantizedNoteSequenceWithVelocity(self):
    testing_lib.add_track_to_sequence(
        self.note_sequence, 0,
        [(60, 100, 0.0, 4.0), (64, 100, 0.0, 3.0), (67, 127, 1.0, 2.0)])
    quantized_sequence = sequences_lib.quantize_note_sequence_absolute(
        self.note_sequence, steps_per_second=100)
    performance = list(performance_lib.Performance(
        quantized_sequence, num_velocity_bins=127))

    pe = performance_lib.PerformanceEvent
    expected_performance = [
        pe(pe.VELOCITY, 100),
        pe(pe.NOTE_ON, 60),
        pe(pe.NOTE_ON, 64),
        pe(pe.TIME_SHIFT, 100),
        pe(pe.VELOCITY, 127),
        pe(pe.NOTE_ON, 67),
        pe(pe.TIME_SHIFT, 100),
        pe(pe.NOTE_OFF, 67),
        pe(pe.TIME_SHIFT, 100),
        pe(pe.NOTE_OFF, 64),
        pe(pe.TIME_SHIFT, 100),
        pe(pe.NOTE_OFF, 60),
    ]
    self.assertEqual(expected_performance, performance)

  def testFromQuantizedNoteSequenceWithQuantizedVelocity(self):
    testing_lib.add_track_to_sequence(
        self.note_sequence, 0,
        [(60, 100, 0.0, 4.0), (64, 100, 0.0, 3.0), (67, 127, 1.0, 2.0)])
    quantized_sequence = sequences_lib.quantize_note_sequence_absolute(
        self.note_sequence, steps_per_second=100)
    performance = list(performance_lib.Performance(
        quantized_sequence, num_velocity_bins=16))

    pe = performance_lib.PerformanceEvent
    expected_performance = [
        pe(pe.VELOCITY, 13),
        pe(pe.NOTE_ON, 60),
        pe(pe.NOTE_ON, 64),
        pe(pe.TIME_SHIFT, 100),
        pe(pe.VELOCITY, 16),
        pe(pe.NOTE_ON, 67),
        pe(pe.TIME_SHIFT, 100),
        pe(pe.NOTE_OFF, 67),
        pe(pe.TIME_SHIFT, 100),
        pe(pe.NOTE_OFF, 64),
        pe(pe.TIME_SHIFT, 100),
        pe(pe.NOTE_OFF, 60),
    ]
    self.assertEqual(expected_performance, performance)

  def testToSequence(self):
    testing_lib.add_track_to_sequence(
        self.note_sequence, 0,
        [(60, 100, 0.0, 4.0), (64, 100, 0.0, 3.0), (67, 100, 1.0, 2.0)])
    quantized_sequence = sequences_lib.quantize_note_sequence_absolute(
        self.note_sequence, steps_per_second=100)
    performance = performance_lib.Performance(quantized_sequence)
    performance_ns = performance.to_sequence()

    # Make comparison easier by sorting.
    performance_ns.notes.sort(key=lambda n: (n.start_time, n.pitch))
    self.note_sequence.notes.sort(key=lambda n: (n.start_time, n.pitch))

    self.assertEqual(self.note_sequence, performance_ns)

  def testToSequenceWithVelocity(self):
    testing_lib.add_track_to_sequence(
        self.note_sequence, 0,
        [(60, 100, 0.0, 4.0), (64, 115, 0.0, 3.0), (67, 127, 1.0, 2.0)])
    quantized_sequence = sequences_lib.quantize_note_sequence_absolute(
        self.note_sequence, steps_per_second=100)
    performance = performance_lib.Performance(
        quantized_sequence, num_velocity_bins=127)
    performance_ns = performance.to_sequence()

    # Make comparison easier by sorting.
    performance_ns.notes.sort(key=lambda n: (n.start_time, n.pitch))
    self.note_sequence.notes.sort(key=lambda n: (n.start_time, n.pitch))

    self.assertEqual(self.note_sequence, performance_ns)

  def testToSequenceWithUnmatchedNoteOffs(self):
    performance = performance_lib.Performance(steps_per_second=100)

    pe = performance_lib.PerformanceEvent
    perf_events = [
        pe(pe.NOTE_ON, 60),
        pe(pe.NOTE_ON, 64),
        pe(pe.TIME_SHIFT, 50),
        pe(pe.NOTE_OFF, 60),
        pe(pe.NOTE_OFF, 64),
        pe(pe.NOTE_OFF, 67),  # Was not started, should be ignored.
    ]
    for event in perf_events:
      performance.append(event)

    performance_ns = performance.to_sequence()

    testing_lib.add_track_to_sequence(
        self.note_sequence, 0,
        [(60, 100, 0.0, 0.5), (64, 100, 0.0, 0.5)])

    # Make comparison easier by sorting.
    performance_ns.notes.sort(key=lambda n: (n.start_time, n.pitch))
    self.note_sequence.notes.sort(key=lambda n: (n.start_time, n.pitch))

    self.assertEqual(self.note_sequence, performance_ns)

  def testToSequenceWithUnmatchedNoteOns(self):
    performance = performance_lib.Performance(steps_per_second=100)

    pe = performance_lib.PerformanceEvent
    perf_events = [
        pe(pe.NOTE_ON, 60),
        pe(pe.NOTE_ON, 64),
        pe(pe.TIME_SHIFT, 100),
    ]
    for event in perf_events:
      performance.append(event)

    performance_ns = performance.to_sequence()

    testing_lib.add_track_to_sequence(
        self.note_sequence, 0,
        [(60, 100, 0.0, 1.0), (64, 100, 0.0, 1.0)])

    # Make comparison easier by sorting.
    performance_ns.notes.sort(key=lambda n: (n.start_time, n.pitch))
    self.note_sequence.notes.sort(key=lambda n: (n.start_time, n.pitch))

    self.assertEqual(self.note_sequence, performance_ns)

  def testToSequenceWithRepeatedNotes(self):
    performance = performance_lib.Performance(steps_per_second=100)

    pe = performance_lib.PerformanceEvent
    perf_events = [
        pe(pe.NOTE_ON, 60),
        pe(pe.NOTE_ON, 64),
        pe(pe.TIME_SHIFT, 100),
        pe(pe.NOTE_ON, 60),
        pe(pe.TIME_SHIFT, 100),
    ]
    for event in perf_events:
      performance.append(event)

    performance_ns = performance.to_sequence()

    testing_lib.add_track_to_sequence(
        self.note_sequence, 0,
        [(60, 100, 0.0, 2.0), (64, 100, 0.0, 2.0), (60, 100, 1.0, 2.0)])

    # Make comparison easier by sorting.
    performance_ns.notes.sort(key=lambda n: (n.start_time, n.pitch))
    self.note_sequence.notes.sort(key=lambda n: (n.start_time, n.pitch))

    self.assertEqual(self.note_sequence, performance_ns)

  def testSetLengthAddSteps(self):
    performance = performance_lib.Performance(steps_per_second=100)

    performance.set_length(50)
    self.assertEqual(50, performance.num_steps)

    pe = performance_lib.PerformanceEvent
    perf_events = [pe(pe.TIME_SHIFT, 50)]
    self.assertEqual(perf_events, list(performance))

    performance.set_length(150)
    self.assertEqual(150, performance.num_steps)

    pe = performance_lib.PerformanceEvent
    perf_events = [
        pe(pe.TIME_SHIFT, 100),
        pe(pe.TIME_SHIFT, 50),
    ]
    self.assertEqual(perf_events, list(performance))

    performance.set_length(200)
    self.assertEqual(200, performance.num_steps)

    pe = performance_lib.PerformanceEvent
    perf_events = [
        pe(pe.TIME_SHIFT, 100),
        pe(pe.TIME_SHIFT, 100),
    ]
    self.assertEqual(perf_events, list(performance))

  def testSetLengthRemoveSteps(self):
    performance = performance_lib.Performance(steps_per_second=100)

    pe = performance_lib.PerformanceEvent
    perf_events = [
        pe(pe.NOTE_ON, 60),
        pe(pe.TIME_SHIFT, 100),
        pe(pe.NOTE_OFF, 60),
        pe(pe.NOTE_ON, 64),
        pe(pe.TIME_SHIFT, 100),
        pe(pe.NOTE_OFF, 64),
        pe(pe.NOTE_ON, 67),
        pe(pe.TIME_SHIFT, 100),
        pe(pe.NOTE_OFF, 67),
    ]
    for event in perf_events:
      performance.append(event)

    performance.set_length(200)
    perf_events = [
        pe(pe.NOTE_ON, 60),
        pe(pe.TIME_SHIFT, 100),
        pe(pe.NOTE_OFF, 60),
        pe(pe.NOTE_ON, 64),
        pe(pe.TIME_SHIFT, 100),
        pe(pe.NOTE_OFF, 64),
        pe(pe.NOTE_ON, 67),
    ]
    self.assertEqual(perf_events, list(performance))

    performance.set_length(50)
    perf_events = [
        pe(pe.NOTE_ON, 60),
        pe(pe.TIME_SHIFT, 50),
    ]
    self.assertEqual(perf_events, list(performance))

  def testNumSteps(self):
    performance = performance_lib.Performance(steps_per_second=100)

    pe = performance_lib.PerformanceEvent
    perf_events = [
        pe(pe.NOTE_ON, 60),
        pe(pe.NOTE_ON, 64),
        pe(pe.TIME_SHIFT, 100),
        pe(pe.NOTE_OFF, 60),
        pe(pe.NOTE_OFF, 64),
    ]
    for event in perf_events:
      performance.append(event)

    self.assertEqual(100, performance.num_steps)

  def testPerformanceNoteDensitySequence(self):
    performance = performance_lib.Performance(steps_per_second=100)

    pe = performance_lib.PerformanceEvent
    perf_events = [
        pe(pe.NOTE_ON, 60),
        pe(pe.NOTE_ON, 64),
        pe(pe.NOTE_ON, 67),
        pe(pe.TIME_SHIFT, 50),
        pe(pe.NOTE_OFF, 60),
        pe(pe.NOTE_OFF, 64),
        pe(pe.TIME_SHIFT, 25),
        pe(pe.NOTE_OFF, 67),
        pe(pe.NOTE_ON, 64),
        pe(pe.TIME_SHIFT, 25),
        pe(pe.NOTE_OFF, 64)
    ]
    for event in perf_events:
      performance.append(event)

    expected_density_sequence = [
        4.0, 4.0, 4.0, 4.0, 2.0, 2.0, 2.0, 4.0, 4.0, 4.0, 0.0]

    density_sequence = performance_lib.performance_note_density_sequence(
        performance, window_size_seconds=1.0)

    self.assertEqual(expected_density_sequence, density_sequence)

  def testPerformancePitchHistogramSequence(self):
    performance = performance_lib.Performance(steps_per_second=100)

    pe = performance_lib.PerformanceEvent
    perf_events = [
        pe(pe.NOTE_ON, 60),
        pe(pe.NOTE_ON, 64),
        pe(pe.NOTE_ON, 67),
        pe(pe.TIME_SHIFT, 50),
        pe(pe.NOTE_OFF, 60),
        pe(pe.NOTE_OFF, 64),
        pe(pe.TIME_SHIFT, 25),
        pe(pe.NOTE_OFF, 67),
        pe(pe.NOTE_ON, 64),
        pe(pe.TIME_SHIFT, 25),
        pe(pe.NOTE_OFF, 64)
    ]
    for event in perf_events:
      performance.append(event)

    expected_histogram_sequence = [
        [0.25, 0, 0, 0, 0.375, 0, 0, 0.375, 0, 0, 0, 0],
        [0.25, 0, 0, 0, 0.375, 0, 0, 0.375, 0, 0, 0, 0],
        [0.25, 0, 0, 0, 0.375, 0, 0, 0.375, 0, 0, 0, 0],
        [0.25, 0, 0, 0, 0.375, 0, 0, 0.375, 0, 0, 0, 0],
        [0.0, 0, 0, 0, 0.5, 0, 0, 0.5, 0, 0, 0, 0],
        [0.0, 0, 0, 0, 0.5, 0, 0, 0.5, 0, 0, 0, 0],
        [0.0, 0, 0, 0, 0.5, 0, 0, 0.5, 0, 0, 0, 0],
        [0.0, 0, 0, 0, 1.0, 0, 0, 0.0, 0, 0, 0, 0],
        [0.0, 0, 0, 0, 1.0, 0, 0, 0.0, 0, 0, 0, 0],
        [0.0, 0, 0, 0, 1.0, 0, 0, 0.0, 0, 0, 0, 0],
        [1.0 / 12.0] * 12
    ]

    histogram_sequence = performance_lib.performance_pitch_histogram_sequence(
        performance, window_size_seconds=1.0, prior_count=0)

    self.assertEqual(expected_histogram_sequence, histogram_sequence)

  def testExtractPerformances(self):
    testing_lib.add_track_to_sequence(
        self.note_sequence, 0, [(60, 100, 0.0, 4.0)])
    quantized_sequence = sequences_lib.quantize_note_sequence_absolute(
        self.note_sequence, steps_per_second=100)

    perfs, _ = performance_lib.extract_performances(quantized_sequence)
    self.assertEqual(1, len(perfs))

    perfs, _ = performance_lib.extract_performances(
        quantized_sequence, min_events_discard=1, max_events_truncate=10)
    self.assertEqual(1, len(perfs))

    perfs, _ = performance_lib.extract_performances(
        quantized_sequence, min_events_discard=8, max_events_truncate=10)
    self.assertEqual(0, len(perfs))

    perfs, _ = performance_lib.extract_performances(
        quantized_sequence, min_events_discard=1, max_events_truncate=3)
    self.assertEqual(1, len(perfs))
    self.assertEqual(3, len(perfs[0]))

  def testExtractPerformancesMultiProgram(self):
    testing_lib.add_track_to_sequence(
        self.note_sequence, 0,
        [(60, 100, 0.0, 4.0), (64, 100, 0.0, 3.0), (67, 100, 1.0, 2.0)])
    self.note_sequence.notes[0].program = 2
    quantized_sequence = sequences_lib.quantize_note_sequence_absolute(
        self.note_sequence, steps_per_second=100)

    perfs, _ = performance_lib.extract_performances(quantized_sequence)
    self.assertEqual(0, len(perfs))

  def testExtractNonZeroStart(self):
    testing_lib.add_track_to_sequence(
        self.note_sequence, 0, [(60, 100, 0.0, 4.0)])
    quantized_sequence = sequences_lib.quantize_note_sequence_absolute(
        self.note_sequence, steps_per_second=100)

    perfs, _ = performance_lib.extract_performances(
        quantized_sequence, start_step=400, min_events_discard=1)
    self.assertEqual(0, len(perfs))
    perfs, _ = performance_lib.extract_performances(
        quantized_sequence, start_step=0, min_events_discard=1)
    self.assertEqual(1, len(perfs))


if __name__ == '__main__':
  tf.test.main()
