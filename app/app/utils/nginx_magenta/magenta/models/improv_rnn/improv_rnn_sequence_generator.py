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
"""Melody-over-chords RNN generation code as a SequenceGenerator interface."""

from functools import partial

# internal imports

from magenta.models.improv_rnn import improv_rnn_model
import magenta.music as mm


class ImprovRnnSequenceGenerator(mm.BaseSequenceGenerator):
  """Improv RNN generation code as a SequenceGenerator interface."""

  def __init__(self, model, details, steps_per_quarter=4, checkpoint=None,
               bundle=None):
    """Creates an ImprovRnnSequenceGenerator.

    Args:
      model: Instance of ImprovRnnModel.
      details: A generator_pb2.GeneratorDetails for this generator.
      steps_per_quarter: What precision to use when quantizing the melody and
          chords. How many steps per quarter note.
      checkpoint: Where to search for the most recent model checkpoint. Mutually
          exclusive with `bundle`.
      bundle: A GeneratorBundle object that includes both the model checkpoint
          and metagraph. Mutually exclusive with `checkpoint`.
    """
    super(ImprovRnnSequenceGenerator, self).__init__(
        model, details, checkpoint, bundle)
    self.steps_per_quarter = steps_per_quarter

  def _generate(self, input_sequence, generator_options):
    if len(generator_options.input_sections) > 1:
      raise mm.SequenceGeneratorException(
          'This model supports at most one input_sections message, but got %s' %
          len(generator_options.input_sections))
    if len(generator_options.generate_sections) != 1:
      raise mm.SequenceGeneratorException(
          'This model supports only 1 generate_sections message, but got %s' %
          len(generator_options.generate_sections))

    qpm = (input_sequence.tempos[0].qpm
           if input_sequence and input_sequence.tempos
           else mm.DEFAULT_QUARTERS_PER_MINUTE)
    steps_per_second = mm.steps_per_quarter_to_steps_per_second(
        self.steps_per_quarter, qpm)

    generate_section = generator_options.generate_sections[0]
    if generator_options.input_sections:
      # Use primer melody from input section only. Take backing chords from
      # beginning of input section through end of generate section.
      input_section = generator_options.input_sections[0]
      primer_sequence = mm.trim_note_sequence(
          input_sequence, input_section.start_time, input_section.end_time)
      backing_sequence = mm.trim_note_sequence(
          input_sequence, input_section.start_time, generate_section.end_time)
      input_start_step = mm.quantize_to_step(
          input_section.start_time, steps_per_second, quantize_cutoff=0.0)
    else:
      # No input section. Take primer melody from the beginning of the sequence
      # up until the start of the generate section.
      primer_sequence = mm.trim_note_sequence(
          input_sequence, 0.0, generate_section.start_time)
      backing_sequence = mm.trim_note_sequence(
          input_sequence, 0.0, generate_section.end_time)
      input_start_step = 0

    last_end_time = (max(n.end_time for n in primer_sequence.notes)
                     if primer_sequence.notes else 0)
    if last_end_time >= generate_section.start_time:
      raise mm.SequenceGeneratorException(
          'Got GenerateSection request for section that is before or equal to '
          'the end of the input section. This model can only extend melodies. '
          'Requested start time: %s, Final note end time: %s' %
          (generate_section.start_time, last_end_time))

    # Quantize the priming and backing sequences.
    quantized_primer_sequence = mm.quantize_note_sequence(
        primer_sequence, self.steps_per_quarter)
    quantized_backing_sequence = mm.quantize_note_sequence(
        backing_sequence, self.steps_per_quarter)

    # Setting gap_bars to infinite ensures that the entire input will be used.
    extracted_melodies, _ = mm.extract_melodies(
        quantized_primer_sequence, search_start_step=input_start_step,
        min_bars=0, min_unique_pitches=1, gap_bars=float('inf'),
        ignore_polyphonic_notes=True)
    assert len(extracted_melodies) <= 1

    start_step = mm.quantize_to_step(
        generate_section.start_time, steps_per_second, quantize_cutoff=0.0)
    # Note that when quantizing end_step, we set quantize_cutoff to 1.0 so it
    # always rounds down. This avoids generating a sequence that ends at 5.0
    # seconds when the requested end time is 4.99.
    end_step = mm.quantize_to_step(
        generate_section.end_time, steps_per_second, quantize_cutoff=1.0)

    if extracted_melodies and extracted_melodies[0]:
      melody = extracted_melodies[0]
    else:
      # If no melody could be extracted, create an empty melody that starts 1
      # step before the request start_step. This will result in 1 step of
      # silence when the melody is extended below.
      steps_per_bar = int(
          mm.steps_per_bar_in_quantized_sequence(quantized_primer_sequence))
      melody = mm.Melody([],
                         start_step=max(0, start_step - 1),
                         steps_per_bar=steps_per_bar,
                         steps_per_quarter=self.steps_per_quarter)

    extracted_chords, _ = mm.extract_chords(quantized_backing_sequence)
    chords = extracted_chords[0]

    # Make sure that chords and melody start on the same step.
    if chords.start_step < melody.start_step:
      chords.set_length(len(chords) - melody.start_step + chords.start_step)

    assert chords.end_step == end_step

    # Ensure that the melody extends up to the step we want to start generating.
    melody.set_length(start_step - melody.start_step)

    # Extract generation arguments from generator options.
    arg_types = {
        'temperature': lambda arg: arg.float_value,
        'beam_size': lambda arg: arg.int_value,
        'branch_factor': lambda arg: arg.int_value,
        'steps_per_iteration': lambda arg: arg.int_value
    }
    args = dict((name, value_fn(generator_options.args[name]))
                for name, value_fn in arg_types.items()
                if name in generator_options.args)

    generated_melody = self._model.generate_melody(melody, chords, **args)
    generated_lead_sheet = mm.LeadSheet(generated_melody, chords)
    generated_sequence = generated_lead_sheet.to_sequence(qpm=qpm)
    assert (generated_sequence.total_time - generate_section.end_time) <= 1e-5
    return generated_sequence


def get_generator_map():
  """Returns a map from the generator ID to a SequenceGenerator class creator.

  Binds the `config` argument so that the arguments match the
  BaseSequenceGenerator class constructor.

  Returns:
    Map from the generator ID to its SequenceGenerator class creator with a
    bound `config` argument.
  """
  def create_sequence_generator(config, **kwargs):
    return ImprovRnnSequenceGenerator(
        improv_rnn_model.ImprovRnnModel(config), config.details,
        steps_per_quarter=config.steps_per_quarter, **kwargs)

  return {key: partial(create_sequence_generator, config)
          for (key, config) in improv_rnn_model.default_configs.items()}
