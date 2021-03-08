import os
import typing
import unittest

from mutwo import converters
from mutwo import events
from mutwo import parameters


class NoteLikeWithText(events.music.NoteLike):
    """NoteLike with additional consonants and vowel attributes.

    Mocking class (only for testing purposes).
    """

    def __init__(
        self,
        pitch_or_pitches,
        duration: parameters.abc.DurationType,
        volume,
        consonants: typing.Tuple[str],
        vowel: str,
    ):
        super().__init__(pitch_or_pitches, duration, volume)
        self.consonants = consonants
        self.vowel = vowel


class IsisScoreConverterTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.converter = converters.frontends.isis.IsisScoreConverter(
            "tests/converters/frontends/isis-score",
        )

    @classmethod
    def tearDownClass(cls):
        # remove score files
        os.remove(cls.converter.path)

    def test_convert_simple_event(self):
        simple_event = NoteLikeWithText(
            parameters.pitches.WesternPitch(), 2, 0.5, ("t",), "a"
        )
        self.converter.convert(simple_event)

        expected_score = (
            "[lyrics]\nxsampa: {} {}\n\n[score]\nmidiNotes: {}\nglobalTransposition:"
            " 0\nrhythm: {}\nloud_accents: {}\ntempo: {}".format(
                simple_event.consonants[0],
                simple_event.vowel,
                simple_event.pitch_or_pitches[0].midi_pitch_number,
                simple_event.duration,
                simple_event.volume.amplitude,
                self.converter._tempo,
            )
        )

        with open(self.converter.path, "r") as f:
            self.assertEqual(f.read(), expected_score)

    def test_convert_rest(self):
        simple_event = events.basic.SimpleEvent(3)
        self.converter.convert(simple_event)

        expected_score = (
            "[lyrics]\nxsampa: _\n\n[score]\nmidiNotes: 0.0\nglobalTransposition:"
            " 0\nrhythm: {}\nloud_accents: 0\ntempo: {}".format(
                simple_event.duration,
                self.converter._tempo,
            )
        )

        with open(self.converter.path, "r") as f:
            self.assertEqual(f.read(), expected_score)


if __name__ == "__main__":
    unittest.main()
