import itertools
import numbers
import typing


def scale(
    value: numbers.Number,
    old_min: numbers.Number,
    old_max: numbers.Number,
    new_min: numbers.Number,
    new_max: numbers.Number,
) -> numbers.Number:
    """Scale a value from one range to another range."""
    try:
        assert old_min <= value <= old_max
    except AssertionError:
        msg = "Input value '{}' has to be in the range of (old_min = {}, old_max = {}).".format(
            value, old_min, old_max
        )
        raise ValueError(msg)
    return (((value - old_min) / (old_max - old_min)) * (new_max - new_min)) + new_min


def accumulate_from_n(iterable: typing.Iterable, n: numbers.Number) -> typing.Iterator:
    """Accumulates iterable starting with value n."""
    return itertools.accumulate(itertools.chain((n,), iterable))


def accumulate_from_zero(iterable: typing.Iterable) -> typing.Iterator:
    """Accumulates iterable starting from 0."""
    return accumulate_from_n(iterable, 0)


def insert_next_to(sequence: typing.List, item_to_find, distance: int, item_to_insert):
    """Insert an item into a list relative to the first item equal to a certain value."""
    index = sequence.index(item_to_find)
    if distance == 0:
        sequence[index] = item_to_insert
    else:
        real_distance = distance + 1 if distance < 0 else distance
        sequence.insert(index + real_distance, item_to_insert)
