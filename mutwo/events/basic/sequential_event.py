from mutwo.events import abc
from mutwo.utils import tools


class SequentialEvent(abc.ComplexEvent):
    """Event-Object, which contains other Event-Objects, which happen one after another."""

    @abc.ComplexEvent.duration.getter
    def duration(self):
        return sum(event.duration for event in self)

    @property
    def absolute_points(self) -> tuple:
        """Return absolute point in time for each event."""
        return tools.accumulate_from_zero((event.duration for event in self))