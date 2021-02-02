import functools
import itertools
import operator

from mutwo.generators import edwards
from mutwo.utilities import tools


class ActivityLevel(object):
    """Python implementation of Michael Edwards activity level algorithm.

    :param start_at: from which pattern per level shall be started (can be
        either 0, 1 or 2)

    Activity Levels is a concept derived from Michael Edwards.
    Quoting Michael Edwards, Activity Levels are an "object for determining
    (deterministically) on a call-by-call basis whether a process is active
    or not (boolean).  This is determined by nine 10-element lists
    (actually three versions of each) of hand-coded 1s and 0s, each list
    representing an 'activity-level' (how active the process should be).
    The first three 10-element lists have only one 1 in them, the rest being zeros.
    The second three have two 1s, etc. Activity-levels of 0 and 10 would return
    never active and always active respectively."
    (see https://michael-edwards.org/sc/robodoc/activity-levels_lsp.html#robo23)
    """

    _allowed_range = tuple(range(len(edwards.constants.ACTIVITY_LEVELS)))

    def __init__(self, start_at: int = 0) -> None:
        try:
            assert start_at in (0, 1, 2)
        except AssertionError:
            msg = "start_at has to be either 0, 1 or 2 and not {}, ".format(start_at)
            msg += "because there are only three different tuples defined per level."
            raise ValueError(msg)

        self._activity_level_cycles = tuple(
            itertools.cycle(
                functools.reduce(
                    operator.add, tuple(tools.cyclic_permutations(levels))[start_at]
                )
            )
            for levels in edwards.constants.ACTIVITY_LEVELS
        )

    def __repr__(self) -> str:
        return "ActivityLevel()"

    def __call__(self, level: int) -> bool:
        """Return current state (is active or not) of entered activity level.

        :param level: the activity-level which current state shall be returned
            (should be from 0 to 10)
        """

        try:
            assert level in self._allowed_range
        except AssertionError:
            msg = "level is '{}' but has to be in range '{}'!".format(
                level, self._allowed_range
            )
            raise ValueError(msg)

        return bool(next(self._activity_level_cycles[level]))
