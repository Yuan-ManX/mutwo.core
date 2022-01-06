"""Render sound files from mutwo data via Csound.

Csound is a `"domain-specific computer programming language
for audio programming" <http://www.csounds.com/>`_.
"""

import numbers
import os
import typing
import warnings

import natsort  # type: ignore

from mutwo import converters
from mutwo import events
from mutwo import parameters
from mutwo.utilities import constants

__all__ = ("CsoundScoreConverter", "CsoundConverter")

SupportedPFieldTypes = typing.Union[constants.Real, str]
SupportedPFieldTypesForTypeChecker = typing.Union[numbers.Real, str]
PFieldFunction = typing.Callable[[events.basic.SimpleEvent], SupportedPFieldTypes]
PFieldDict = dict[str, typing.Optional[PFieldFunction]]


class CsoundScoreConverter(converters.abc.EventConverter):
    """Class to convert mutwo events to a Csound score file.

    :param pfield: p-field / p-field-extraction-function pairs.

    This class helps generating score files for the `"domain-specific computer
    programming language for audio programming" Csound <http://www.csounds.com/>`_.

    :class:`CsoundScoreConverter` extracts data from mutwo Events and assign it to
    specific p-fields. The mapping of Event attributes to p-field values has
    to be defined by the user via keyword arguments during class initialization.

    By default, mutwo already maps the following p-fields to the following values:

    - p1 (instrument name) to 1
    - p2 (start time) to the absolute start time of the event
    - p3 (duration) to the :attr:`duration` attribute of the event

    If p2 shall be assigned to the absolute entry delay of the event,
    it has to be set to None.

    The :class:`CsoundScoreConverter` ignores any p-field that returns
    any unsupported p-field type (anything else than a string
    or a number). If the returned type is a string, :class:`CsoundScoreConverter`
    automatically adds quotations marks around the string in the score file.

    All p-fields can be overwritten in the following manner:

    >>> my_converter = CsoundScoreConverter(
    >>>     p1=lambda event: 2,
    >>>     p4=lambda event: event.pitch.frequency,
    >>>     p5=lambda event: event.volume
    >>> )

    For easier debugging of faulty score files, :mod:`mutwo` adds annotations
    when a new :class:`SequentialEvent` or a new :class:`SimultaneousEvent`
    starts.
    """

    _default_p_field_dict: PFieldDict = {
        "p1": lambda event: 1,  # default instrument name "1"
        "p2": None,  # default to absolute start time
        "p3": lambda event: event.duration  # type: ignore
        if event.duration > 0
        else None,  # default key for duration
    }

    def __init__(self, **pfield: PFieldFunction):
        concatenated_p_field_dict: PFieldDict = dict([])
        for (
            default_p_field,
            default_p_field_function,
        ) in self._default_p_field_dict.items():
            if default_p_field not in pfield:
                concatenated_p_field_dict.update(
                    {default_p_field: default_p_field_function}
                )

        concatenated_p_field_dict.update(pfield)
        self.pfield_tuple = self._generate_pfield_mapping(concatenated_p_field_dict)

    # ###################################################################### #
    #                          static methods                                #
    # ###################################################################### #

    @staticmethod
    def _generate_pfield_mapping(
        pfield_key_to_function_mapping: PFieldDict,
    ) -> tuple[typing.Optional[PFieldFunction], ...]:
        """Maps p-fields to their respective p_field_function."""

        sorted_pfield_keys = natsort.natsorted(pfield_key_to_function_mapping.keys())
        pfield_list = []
        for key0, key1 in zip(sorted_pfield_keys, sorted_pfield_keys[1:]):
            number0, number1 = (int(pfield_name[1:]) for pfield_name in (key0, key1))
            try:
                assert number0 >= 0
            except AssertionError:
                message = "Can't assign p-field '{}'. P-field number has to bigger than 0.".format(
                    key0
                )
                raise ValueError(message)

            pfield_list.append(pfield_key_to_function_mapping[key0])

            difference = number1 - number0
            if difference > 1:
                for _ in range(difference - 1):
                    pfield_list.append(lambda event: 0)
                message = "Couldn't find any mapping for p-fields between '{}' and '{}'. ".format(
                    key0, key1
                )
                message += "Assigned these p-fields to 0."
                warnings.warn(message)

        pfield_list.append(pfield_key_to_function_mapping[key1])
        return tuple(pfield_list)

    @staticmethod
    def _process_p_field_value(
        nth_p_field: int, p_field_value: typing.Any
    ) -> typing.Optional[str]:
        """Makes sure pfield value is of correct type & adds quotation marks for str."""

        if isinstance(p_field_value, SupportedPFieldTypesForTypeChecker.__args__):  # type: ignore
            # silently adding quotation marks
            if isinstance(p_field_value, str):
                p_field_value = '"{}"'.format(p_field_value)

            else:
                p_field_value = "{}".format(p_field_value)

            return p_field_value

        else:
            ignored_p_field = nth_p_field + 1
            message = (
                "Can't assign returned value '{}' of type '{}' to p-field {}.".format(
                    p_field_value, type(p_field_value), ignored_p_field
                )
            )
            message += " Supported types for p-fields include '{}'. ".format(
                repr(SupportedPFieldTypes)
            )
            message += "Ignored p-field {}.".format(ignored_p_field)
            warnings.warn(message)
            return None

    # ###################################################################### #
    #           private methods (conversion of different event types)        #
    # ###################################################################### #

    def _convert_simple_event(
        self,
        simple_event: events.basic.SimpleEvent,
        absolute_entry_delay: parameters.abc.DurationType,
    ) -> tuple[str, ...]:
        """Extract p-field data from simple event and write one Csound-Score line."""

        csound_score_line = "i"
        for nth_p_field, p_field_function in enumerate(self.pfield_tuple):
            # special case of absolute start time initialization
            if nth_p_field == 1 and p_field_function is None:
                csound_score_line += " {}".format(absolute_entry_delay)

            else:
                try:
                    p_field_value = p_field_function(simple_event)  # type: ignore

                except AttributeError:
                    # if attribute couldn't be found, just make a rest
                    return tuple([])

                p_field_value = CsoundScoreConverter._process_p_field_value(
                    nth_p_field, p_field_value
                )
                if p_field_value is not None:
                    csound_score_line += " {}".format(p_field_value)

        return (csound_score_line,)

    def _convert_sequential_event(
        self,
        sequential_event: events.basic.SequentialEvent,
        absolute_entry_delay: parameters.abc.DurationType,
    ) -> tuple[str, ...]:
        csound_score_line_list = [
            converters.frontends.csound_constants.SEQUENTIAL_EVENT_ANNOTATION
        ]
        csound_score_line_list.extend(
            super()._convert_sequential_event(sequential_event, absolute_entry_delay)
        )

        for _ in range(
            converters.frontends.csound_constants.N_EMPTY_LINES_AFTER_COMPLEX_EVENT
        ):
            csound_score_line_list.append("")

        return tuple(csound_score_line_list)

    def _convert_simultaneous_event(
        self,
        simultaneous_event: events.basic.SimultaneousEvent,
        absolute_entry_delay: parameters.abc.DurationType,
    ) -> tuple[str, ...]:
        csound_score_line_list = [
            converters.frontends.csound_constants.SIMULTANEOUS_EVENT_ANNOTATION
        ]
        csound_score_line_list.extend(
            super()._convert_simultaneous_event(
                simultaneous_event, absolute_entry_delay
            )
        )
        for _ in range(
            converters.frontends.csound_constants.N_EMPTY_LINES_AFTER_COMPLEX_EVENT
        ):
            csound_score_line_list.append("")
        return tuple(csound_score_line_list)

    # ###################################################################### #
    #                             public api                                 #
    # ###################################################################### #

    def convert(self, event_to_convert: events.abc.Event, path: str) -> None:
        """Render csound score file (.sco) from the passed event.

        :param event_to_convert: The event that shall be rendered to a csound score
            file.
        :type event_to_convert: events.abc.Event
        :param path: where to write the csound score file
        :type path: str

        >>> import random
        >>> from mutwo.parameters import pitches
        >>> from mutwo.events import basic
        >>> from mutwo.converters.frontends import csound
        >>> converter = csound.CsoundScoreConverter(
        >>>    p4=lambda event: event.pitch.frequency
        >>> )
        >>> events = basic.SequentialEvent(
        >>>    [
        >>>        basic.SimpleEvent(random.uniform(0.3, 1.2)) for _ in range(15)
        >>>    ]
        >>> )
        >>> for event in events:
        >>>     event.pitch = pitches.DirectPitch(random.uniform(100, 500))
        >>> converter.convert(events, 'score.sco')
        """

        csound_score_line_tuple = self._convert_event(event_to_convert, 0)
        # convert events to strings (where each string represents one csound score line)
        # write csound score lines to file
        with open(path, "w") as f:
            f.write("\n".join(csound_score_line_tuple))


class CsoundConverter(converters.abc.Converter):
    """Generate audio files with `Csound <http://www.csounds.com/>`_.

    :param csound_orchestra_path: Path to the csound orchestra (.orc) file.
    :param csound_score_converter: The :class:`CsoundScoreConverter` that shall be used
        to render the csound score file (.sco) from a mutwo event.
    :param *flag: Flag that shall be added when calling csound. Several of the supported
        csound flags can be found in :mod:`mutwo.converters.frontends.csound_constants`.
    :param remove_score_file: Set to True if :class:`CsoundConverter` shall remove the
        csound score file after rendering. Defaults to False.

    **Disclaimer:** Before using the :class:`CsoundConverter`, make sure
    `Csound <http://www.csounds.com/>`_ has been correctly installed on
    your system.
    """

    def __init__(
        self,
        csound_orchestra_path: str,
        csound_score_converter: CsoundScoreConverter,
        *flag: str,
        remove_score_file: bool = False
    ):
        self.flags = flag
        self.csound_orchestra_path = csound_orchestra_path
        self.csound_score_converter = csound_score_converter
        self.remove_score_file = remove_score_file

    def convert(
        self,
        event_to_convert: events.abc.Event,
        path: str,
        score_path: typing.Optional[str] = None,
    ) -> None:
        """Render sound file from the mutwo event.

        :param event_to_convert: The event that shall be rendered.
        :type event_to_convert: events.abc.Event
        :param path: where to write the sound file
        :type path: str
        :param score_path: where to write the score file
        :type score_path: typing.Optional[str]
        """

        if not score_path:
            score_path = path + ".sco"

        self.csound_score_converter.convert(event_to_convert, score_path)
        command = "csound -o {}".format(path)
        for flag in self.flags:
            command += " {} ".format(flag)
        command += " {} {}".format(self.csound_orchestra_path, score_path)

        os.system(command)

        if self.remove_score_file:
            os.remove(score_path)
