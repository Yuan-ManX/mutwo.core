"""This module adds several constants that are used for the midi converter module.

There are basically two types of constants:
    1. Default values for `MidiFileConverter` arguments.
    2. Values that are defined by the midi file standard.
"""

from mutwo import events
from mutwo import parameters

DEFAULT_AVAILABLE_MIDI_CHANNELS = tuple(range(16))
"""default value for ``available_midi_channels`` in `MidiFileConverter`"""

DEFAULT_MAXIMUM_PITCH_BEND_DEVIATION_IN_CENTS = 200
"""default value for ``maximum_pitch_bend_deviation_in_cents`` in `MidiFileConverter`"""

DEFAULT_MIDI_FILE_TYPE = 1
"""default value for ``midi_file_type`` in `MidiFileConverter`"""

DEFAULT_MIDI_INSTRUMENT_NAME = "Acoustic Grand Piano"
"""default value for ``midi_instrument_name`` in `MidiFileConverter`"""

DEFAULT_N_MIDI_CHANNELS_PER_TRACK = 1
"""default value for ``n_midi_channels_per_track`` in `MidiFileConverter`"""

DEFAULT_TEMPO_EVENTS = events.basic.SequentialEvent(
    [events.basic.EnvelopeEvent(1, parameters.tempos.TempoPoint(120, 1))]
)
"""default value for ``tempo_events`` in `MidiFileConverter`"""

DEFAULT_TICKS_PER_BEAT = 480
"""default value for ``ticks_per_beat`` in `MidiFileConverter`"""

ALLOWED_MIDI_CHANNELS = tuple(range(16))
"""midi channels that are allowed (following the standard
midi file definition)."""

MAXIMUM_MICROSECONDS_PER_BEAT = 16777215

MINIMUM_VELOCITY = 0
"""the lowest allowed midi velocity value"""

MAXIMUM_VELOCITY = 127
"""the highest allowed midi velocity value"""

MIDI_TEMPO_FACTOR = 1000000
"""factor to multiply beats-in-seconds to get
beats-in-microseconds (which is the tempo unit for midi)"""

NEUTRAL_PITCH_BEND = 8191
"""the value for midi pitch bend when the resulting pitch
doesn't change"""

MAXIMUM_PITCH_BEND = 16382
"""the highest allowed value for midi pitch bend"""