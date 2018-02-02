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
"""Import NoteSequences from MusicNet.

This file is py2only compatible because the original musicnet dataset
was pickled using py2 and therefore cannot be deserialized with py3.

"""

import StringIO

# internal imports
import numpy as np
import tensorflow as tf

from magenta.protobuf import music_pb2

MUSICNET_SAMPLE_RATE = 44100
MUSICNET_NOTE_VELOCITY = 100


def note_interval_tree_to_sequence_proto(note_interval_tree, sample_rate):
  """Convert MusicNet note interval tree to a NoteSequence proto.

  Args:
    note_interval_tree: An intervaltree.IntervalTree containing note intervals
        and data as found in the MusicNet archive. The interval begin and end
        values are audio sample numbers.
    sample_rate: The sample rate for which the note intervals are defined.

  Returns:
    A NoteSequence proto containing the notes in the interval tree.
  """
  sequence = music_pb2.NoteSequence()

  # Sort note intervals by onset time.
  note_intervals = sorted(note_interval_tree,
                          key=lambda note_interval: note_interval.begin)

  # MusicNet represents "instruments" as MIDI program numbers. Here we map each
  # program to a separate MIDI instrument.
  instruments = {}

  for note_interval in note_intervals:
    note_data = note_interval.data

    note = sequence.notes.add()
    note.pitch = note_data[1]
    note.velocity = MUSICNET_NOTE_VELOCITY
    note.start_time = float(note_interval.begin) / sample_rate
    note.end_time = float(note_interval.end) / sample_rate
    note.program = note_data[0]
    note.is_drum = False

    if note.program not in instruments:
      instruments[note.program] = len(instruments)
    note.instrument = instruments[note.program]

    if note.end_time > sequence.total_time:
      sequence.total_time = note.end_time

  return sequence


def musicnet_iterator(musicnet_file):
  """An iterator over the MusicNet archive that yields audio and NoteSequences.

  The MusicNet archive (in .npz format) can be downloaded from:
  https://homes.cs.washington.edu/~thickstn/media/musicnet.npz

  Args:
    musicnet_file: The path to the MusicNet NumPy archive (.npz) containing
        audio and transcriptions for 330 classical recordings.

  Yields:
    Tuples where the first element is a NumPy array of sampled audio (at 44.1
    kHz) and the second element is a NoteSequence proto containing the
    transcription.
  """
  with tf.gfile.FastGFile(musicnet_file, 'rb') as f:
    # Unfortunately the gfile seek function breaks the reading of NumPy
    # archives, so we read the archive first then load as StringIO.
    musicnet_string = f.read()
    musicnet_stringio = StringIO.StringIO(musicnet_string)
    musicnet = np.load(musicnet_stringio)

  for file_id in musicnet.files:
    audio, note_interval_tree = musicnet[file_id]
    sequence = note_interval_tree_to_sequence_proto(
        note_interval_tree, MUSICNET_SAMPLE_RATE)

    sequence.filename = file_id
    sequence.collection_name = 'MusicNet'
    sequence.id = '/id/musicnet/%s' % file_id

    sequence.source_info.source_type = (
        music_pb2.NoteSequence.SourceInfo.PERFORMANCE_BASED)
    sequence.source_info.encoding_type = (
        music_pb2.NoteSequence.SourceInfo.MUSICNET)
    sequence.source_info.parser = (
        music_pb2.NoteSequence.SourceInfo.MAGENTA_MUSICNET)

    yield audio, sequence
