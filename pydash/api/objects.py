"""Functions that operate on lists, dicts, and other objects.

.. versionadded:: 1.0.0
"""

from __future__ import absolute_import

import copy
import datetime
from itertools import islice
import json
import operator
import re

from .arrays import flatten_deep, initial, last
from .utilities import (
    identity,
    iterator,
    itercallback,
    get_item,
    set_item
)
from .._compat import (
    iteritems,
    integer_types,
    number_types,
    string_types,
    text_type,
    izip
)


__all__ = [
    'assign',
    'clone',
    'clone_deep',
    'defaults',
    'extend',
    'find_key',
    'find_last_key',
    'for_in',
    'for_in_right',
    'for_own',
    'for_own_right',
    'functions',
    'has',
    'invert',
    'is_associative',
    'is_boolean',
    'is_date',
    'is_decreasing',
    'is_empty',
    'is_equal',
    'is_error',
    'is_float',
    'is_function',
    'is_increasing',
    'is_indexed',
    'is_instance_of',
    'is_integer',
    'is_json',
    'is_list',
    'is_monotone',
    'is_nan',
    'is_negative',
    'is_none',
    'is_number',
    'is_object',
    'is_plain_object',
    'is_positive',
    'is_re',
    'is_reg_exp',
    'is_strictly_decreasing',
    'is_strictly_increasing',
    'is_string',
    'is_zero',
    'keys',
    'keys_in',
    'map_values',
    'merge',
    'methods',
    'omit',
    'pairs',
    'parse_int',
    'pick',
    'rename_keys',
    'set_path',
    'transform',
    'update_path',
    'values',
    'values_in',
]


RegExp = type(re.compile(''))


def assign(obj, *sources, **kargs):
    """Assigns own enumerable properties of source object(s) to the destination
    object.

    Args:
        obj (dict): Destination object whose properties will be modified.
        *sources (dict): Source objects to assign to `obj`.
        callback (mixed, optional): Callback applied per iteration.

    Returns:
        dict: Modified `obj`.

    Warning:
        `obj` is modified in place.

    See Also:
        - :func:`assign` (main definition)
        - :func:`extend` (alias)

    .. versionadded:: 1.0.0
    """
    sources = list(sources)
    callback = kargs.get('callback')

    if callback is None and callable(sources[-1]):
        callback = sources.pop()

    for source in sources:
        for key, value in iteritems(source):
            obj[key] = (value if callback is None
                        else callback(obj.get(key), value))

    return obj


extend = assign


def clone(value, is_deep=False, callback=None):
    """Creates a clone of `value`. If `is_deep` is ``True`` nested valueects
    will also be cloned, otherwise they will be assigned by reference. If a
    callback is provided it will be executed to produce the cloned values. The
    callback is invoked with one argument: ``(value)``.

    Args:
        value (list|dict): Object to clone.
        is_deep (bool, optional): Whether to perform deep clone.
        callback (mixed, optional): Callback applied per iteration.

    Returns:
        list|dict: Cloned object.

    .. versionadded:: 1.0.0
    """
    if callback is None:
        callback = identity

    copier = copy.deepcopy if is_deep else copy.copy
    value = copier(value)

    obj = [(key, callback(val)) for key, val in iterator(value)]

    if isinstance(value, list):
        obj = [val for _, val in obj]
    else:
        obj = dict(obj)

    return obj


def clone_deep(value, callback=None):
    """Creates a deep clone of `value`. If a callback is provided it will be
    executed to produce the cloned values. The callback is invoked with one
    argument: ``(value)``.

    Args:
        value (list|dict): Object to clone.
        callback (mixed, optional): Callback applied per iteration.

    Returns:
        list|dict: Cloned object.

    .. versionadded:: 1.0.0
    """
    return clone(value, is_deep=True, callback=callback)


def defaults(obj, *sources):
    """Assigns own enumerable properties of source object(s) to the destination
    object for all destination properties that resolve to undefined.

    Args:
        obj (dict): Destination object whose properties will be modified.
        *sources (dict): Source objects to assign to `obj`.

    Returns:
        dict: Modified `obj`.

    Warning:
        `obj` is modified in place.

    .. versionadded:: 1.0.0
    """
    for source in sources:
        for key, value in iteritems(source):
            obj.setdefault(key, value)

    return obj


def find_key(obj, callback=None):
    """This method is like :func:`pydash.api.arrays.find_index` except that it
    returns the key of the first element that passes the callback check,
    instead of the element itself.

    Args:
        obj (list|dict): Object to search.
        callback (mixed): Callback applied per iteration.

    Returns:
        mixed: Found key or ``None``.

    See Also:
        - :func:`find_key` (main definition)
        - :func:`find_last_key` (alias)

    .. versionadded:: 1.0.0
    """
    for result, _, key, _ in itercallback(obj, callback):
        if result:
            return key


find_last_key = find_key


def for_in(obj, callback=None):
    """Iterates over own and inherited enumerable properties of `obj`,
    executing `callback` for each property.

    Args:
        obj (list|dict): Object to process.
        callback (mixed): Callback applied per iteration.

    Returns:
        list|dict: `obj`.

    See Also:
        - :func:`for_in` (main definition)
        - :func:`for_own` (alias)

    .. versionadded:: 1.0.0
    """
    for result, _, _, _ in itercallback(obj, callback):
        if result is False:
            break

    return obj


for_own = for_in


def for_in_right(obj, callback=None):
    """This function is like :func:`for_in` except it iterates over the
    properties in reverse order.

    Args:
        obj (list|dict): Object to process.
        callback (mixed): Callback applied per iteration.

    Returns:
        list|dict: `obj`.

    See Also:
        - :func:`for_in_right` (main definition)
        - :func:`for_own_right` (alias)

    .. versionadded:: 1.0.0
    """
    for result, _, _, _ in itercallback(obj, callback, reverse=True):
        if result is False:
            break

    return obj


for_own_right = for_in_right


def functions(obj):
    """Creates a list of keys of an object that are callable.

    Args:
        obj (list|dict): Object to inspect.

    Returns:
        list: All keys whose values are callable.

    See Also:
        - :func:`functions` (main definition)
        - :func:`methods` (alias)

    .. versionadded:: 1.0.0
    """
    return [key for key, value in iterator(obj) if callable(value)]


methods = functions


def has(obj, key):
    """Checks if `key` exists as a key of `obj`.

    Args:
        obj (mixed): Object to test.
        key (mixed): Key to test for.

    Returns:
        bool: Whether `obj` has `key`.

    .. versionadded:: 1.0.0
    """
    return key in (key for key, value in iterator(obj))


def invert(obj):
    """Creates an object composed of the inverted keys and values of the given
    object.

    Args:
        obj (dict): dict to invert

    Returns:
        dict: Inverted dict

    Note:
        Assumes `dict` values are hashable as `dict` keys.

    .. versionadded:: 1.0.0
    """
    return dict((value, key) for key, value in iterator(obj))


def is_associative(value):
    """Checks if `value` is an associative object meaning that it can be
    accessed via an index or key

    Args:
        value (mixed): Value to check.

    Returns:
        bool: Whether `value` is associative.

    .. versionadded:: 2.0.0
    """
    return hasattr(value, '__getitem__')


def is_boolean(value):
    """Checks if `value` is a boolean value.

    Args:
        value (mixed): Value to check.

    Returns:
        bool: Whether `value` is a boolean.

    .. versionadded:: 1.0.0
    """
    return isinstance(value, bool)


def is_date(value):
    """Check if `value` is a date object.

    Args:
        value (mixed): Value to check.

    Returns:
        bool: Whether `value` is a date object.

    Note:
        This will also return ``True`` for datetime objects.

    .. versionadded:: 1.0.0
    """
    return isinstance(value, datetime.date)


def is_decreasing(value):
    """Check if `value` is monotonically increasing.

    Args:
        value (list): Value to check.

    Returns:
        bool: Whether `value` is monotonically increasing.

    .. versionadded:: 2.0.0
    """
    return is_monotone(value, operator.ge)


def is_empty(value):
    """Checks if `value` is empty.

    Args:
        value (mixed): Value to check.

    Returns:
        bool: Whether `value` is empty.

    Note:
        Returns ``True`` for booleans and numbers.

    .. versionadded:: 1.0.0
    """
    return any([is_boolean(value), is_number(value), not value])


def is_equal(a, b, callback=None):
    """Performs a comparison between two values to determine if they are
    equivalent to each other. If a callback is provided it will be executed to
    compare values. If the callback returns ``None``, comparisons will be
    handled by the method instead. The callback is invoked with two arguments:
    ``(a, b)``.

    Args:
        a (list|dict): Object to compare.
        b (list|dict): Object to compare.
        callback (mixed, optional): Callback used to compare values from `a`
            and `b`.

    Returns:
        bool: Whether `a` and `b` are equal.

    .. versionadded:: 1.0.0
    """
    # If callback provided, use it for comparision.
    equal = callback(a, b) if callable(callback) else None

    # Return callback results if anything but None.
    if equal is not None:
        pass
    elif (callable(callback) and
          type(a) is type(b) and
          isinstance(a, (list, dict)) and
          isinstance(b, (list, dict)) and
          len(a) == len(b)):
        # Walk a/b to determine equality using callback.
        for key, value in iterator(a):
            if has(b, key):
                equal = is_equal(value, b[key], callback)
            else:
                equal = False

            if not equal:
                break
    else:
        # Use basic == comparision.
        equal = a == b

    return equal


def is_error(value):
    """Checks if `value` is an ``Exception``.

    Args:
        value (mixed): Value to check.

    Returns:
        bool: Whether `value` is an exception.

    .. versionadded:: 1.1.0
    """
    return isinstance(value, Exception)


def is_even(value):
    """Checks if `value` is even.

    Args:
        value (mixed): Value to check.

    Returns:
        bool: Whether `value` is even.

    .. versionadded:: 2.0.0
    """
    return is_number(value) and value % 2 == 0


def is_float(value):
    """Checks if `value` is a float.

    Args:
        value (mixed): Value to check.

    Returns:
        bool: Whether `value` is a float.

    .. versionadded:: 2.0.0
    """
    return isinstance(value, float)


def is_function(value):
    """Checks if `value` is a function.

    Args:
        value (mixed): Value to check.

    Returns:
        bool: Whether `value` is callable.

    .. versionadded:: 1.0.0
    """
    return callable(value)


def is_increasing(value):
    """Check if `value` is monotonically increasing.

    Args:
        value (list): Value to check.

    Returns:
        bool: Whether `value` is monotonically increasing.

    .. versionadded:: 2.0.0
    """
    return is_monotone(value, operator.le)


def is_indexed(value):
    """Checks if `value` is integer indexed, i.e., ``list`` or ``str``.

    Args:
        value (mixed): Value to check.

    Returns:
        bool: Whether `value` is integer indexed.

    .. versionadded:: 2.0.0
    """
    return is_list(value) or is_string(value)


def is_instance_of(value, types):
    """Checks if `value` is an instance of `types`.

    Args:
        value (mixed): Value to check.
        types (mixed): Types to check against. Pass as ``tuple`` to check if
            `value` is one of multiple types.

    Returns:
        bool: Whether `value` is an instance of `types`.

    .. versionadded:: 2.0.0
    """
    return isinstance(value, types)


def is_integer(value):
    """Checks if `value` is a integer.

    Args:
        value (mixed): Value to check.

    Returns:
        bool: Whether `value` is a integer.

    .. versionadded:: 2.0.0
    """
    return is_number(value) and isinstance(value, integer_types)


def is_json(value):
    """Checks if `value` is a valid JSON string.

    Args:
        value (mixed): Value to check.

    Returns:
        bool: Whether `value` is JSON.

    .. versionadded:: 2.0.0
    """
    try:
        json.loads(value)
        return True
    except Exception:  # pylint: disable=broad-except
        return False


def is_list(value):
    """Checks if `value` is a list.

    Args:
        value (mixed): Value to check.

    Returns:
        bool: Whether `value` is a list.

    .. versionadded:: 1.0.0
    """
    return isinstance(value, list)


def is_monotone(value, op):
    """Checks if `value` is monotonic when `operator` used for comparison.

    Args:
        value (list): Value to check.
        op (function): Operation to used for comparison.

    Returns:
        bool: Whether `value` is monotone.

    .. versionadded:: 2.0.0
    """
    if not is_list(value):
        value = [value]

    result = True
    for x, y in izip(value, islice(value, 1, None)):
        if not op(x, y):
            result = False
            break

    return result


def is_nan(value):
    """Checks if `value` is not a number.

    Args:
        value (mixed): Value to check.

    Returns:
        bool: Whether `value` is not a number.

    .. versionadded:: 1.0.0
    """
    return not is_number(value)


def is_negative(value):
    """Checks if `value` is negative.

    Args:
        value (mixed): Value to check.

    Returns:
        bool: Whether `value` is negative.

    .. versionadded:: 2.0.0
    """
    return is_number(value) and value < 0


def is_none(value):
    """Checks if `value` is `None`.

    Args:
        value (mixed): Value to check.

    Returns:
        bool: Whether `value` is ``None``.

    .. versionadded:: 1.0.0
    """
    return value is None


def is_number(value):
    """Checks if `value` is a number.

    Args:
        value (mixed): Value to check.

    Returns:
        bool: Whether `value` is a number.

    Note:
        Returns ``True`` for ``int``, ``long`` (PY2), ``float``, and
        ``decimal.Decimal``.

    .. versionadded:: 1.0.0
    """
    return not is_boolean(value) and isinstance(value, number_types)


def is_object(value):
    """Checks if `value` is a ``list`` or ``dict``.

    Args:
        value (mixed): Value to check.

    Returns:
        bool: Whether `value` is ``list`` or ``dict``.

    .. versionadded:: 1.0.0
    """
    return isinstance(value, (list, dict))


def is_odd(value):
    """Checks if `value` is odd.

    Args:
        value (mixed): Value to check.

    Returns:
        bool: Whether `value` is odd.

    .. versionadded:: 2.0.0
    """
    return is_number(value) and value % 2 != 0


def is_plain_object(value):
    """Checks if `value` is a ``dict``.

    Args:
        value (mixed): Value to check.

    Returns:
        bool: Whether `value` is a ``dict``.

    .. versionadded:: 1.0.0
    """
    return isinstance(value, dict)


def is_positive(value):
    """Checks if `value` is positive.

    Args:
        value (mixed): Value to check.

    Returns:
        bool: Whether `value` is positive.

    .. versionadded:: 2.0.0
    """
    return is_number(value) and value > 0


def is_reg_exp(value):
    """Checks if `value` is a ``RegExp`` object.

    Args:
        value (mxied): Value to check.

    Returns:
        bool: Whether `value` is a RegExp object.

    See Also:
        - :func:`is_reg_exp` (main definition)
        - :func:`is_re` (alias)

    .. versionadded:: 1.1.0
    """
    return isinstance(value, RegExp)


is_re = is_reg_exp


def is_strictly_decreasing(value):
    """Check if `value` is strictly decreasing.

    Args:
        value (list): Value to check.

    Returns:
        bool: Whether `value` is strictly decreasing.

    .. versionadded:: 2.0.0
    """
    return is_monotone(value, operator.gt)


def is_strictly_increasing(value):
    """Check if `value` is strictly increasing.

    Args:
        value (list): Value to check.

    Returns:
        bool: Whether `value` is strictly increasing.

    .. versionadded:: 2.0.0
    """
    return is_monotone(value, operator.lt)


def is_string(value):
    """Checks if `value` is a string.

    Args:
        value (mixed): Value to check.

    Returns:
        bool: Whether `value` is a string.

    .. versionadded:: 1.0.0
    """
    return isinstance(value, string_types)


def is_zero(value):
    """Checks if `value` is ``0``.

    Args:
        value (mixed): Value to check.

    Returns:
        bool: Whether `value` is ``0``.

    .. versionadded:: 2.0.0
    """
    return value is 0


def keys(obj):
    """Creates a list composed of the keys of `obj`.

    Args:
        obj (mixed): Object to extract keys from.

    Returns:
        list: List of keys.

    See Also:
        - :func:`keys` (main definition)
        - :func:`keys_in` (alias)

    .. versionadded:: 1.0.0

    .. versionchanged:: 1.1.0
       Added :func:`keys_in` as alias.
    """
    return [key for key, _ in iterator(obj)]


keys_in = keys


def map_values(obj, callback=None):
    """Creates an object with the same keys as `obj` and values generated by
    running each property of `obj` through the `callback`. The callback is
    invoked with three arguments: ``(value, key, object)``. If a property name
    is provided for `callback` the created :func:`pydash.api.collections.pluck`
    style callback will return the property value of the given element. If an
    object is provided for callback the created
    :func:`pydash.api.collections.where` style callback will return ``True``
    for elements that have the properties of the given object, else ``False``.

    Args:
        obj (list|dict): Object to map.
        callback (mixed): Callback applied per iteration.

    Returns:
        list|dict: Results of running `obj` through `callback`.

    .. versionadded:: 1.0.0
    """
    return dict((key, result)
                for result, _, key, _ in itercallback(obj, callback))


def merge(obj, *sources, **kargs):
    """Recursively merges own enumerable properties of the source object(s)
    that don't resolve to undefined into the destination object. Subsequent
    sources will overwrite property assignments of previous sources. If a
    callback is provided it will be executed to produce the merged values of
    the destination and source properties. If the callback returns undefined
    merging will be handled by the method instead. The callback is invoked with
    two arguments: ``(obj_value, source_value)``.

    Args:
        obj (dict): Destination object to merge source(s) into.
        *sources (dict): Source objects to merge from. subsequent sources
            overwrite previous ones.

    Keyword Args:
        callback (function, optional): Callback function to handle merging
            (must be passed in as keyword argument).

    Returns:
        dict: Merged object.

    Warning:
        `obj` is modified in place.

    .. versionadded:: 1.0.0
    """
    callback = kargs.get('callback')

    for source in sources:
        for key, src_value in iterator(source):
            obj_value = get_item(obj, key, default=None)
            is_sequences = all([src_value,
                                isinstance(src_value, list),
                                isinstance(obj_value, list)])
            is_mappings = all([src_value,
                               isinstance(src_value, dict),
                               isinstance(obj_value, dict)])

            if (is_sequences or is_mappings) and not callback:
                result = merge(obj_value, src_value)
            elif callback:
                result = callback(obj_value, src_value)
            else:
                result = src_value

            set_item(obj, key, result)

    return obj


def omit(obj, callback=None, *properties):
    """Creates a shallow clone of object excluding the specified properties.
    Property names may be specified as individual arguments or as lists of
    property names. If a callback is provided it will be executed for each
    property of object omitting the properties the callback returns truthy for.
    The callback is invoked with three arguments: ``(value, key, object)``.

    Args:
        obj (mixed): Object to process.
        *properties (str): Property values to omit.
        callback (mixed, optional): Callback used to determine whic properties
            to omit.

    Returns:
        dict: Results of omitting properties.

    .. versionadded:: 1.0.0
    """
    if not callable(callback):
        callback = callback if callback is not None else []
        properties = flatten_deep([callback, properties])
        callback = lambda value, key, item: key in properties

    return dict((key, value) for key, value in iterator(obj)
                if not callback(value, key, obj))


def pairs(obj):
    """Creates a two dimensional list of an object's key-value pairs, i.e.
    ``[[key1, value1], [key2, value2]]``.

    Args:
        obj (mixed): Object to process.

    Returns:
        list: Two dimensional list of object's key-value pairs.

    .. versionadded:: 1.0.0
    """
    return [[key, value] for key, value in iterator(obj)]


def parse_int(value, radix=None):
    """Converts the given `value` into an integer of the specified `radix`. If
    `radix` is falsey a radix of ``10`` is used unless the `value` is a
    hexadecimal, in which case a radix of 16 is used.

    Args:
        value (mixed): Value to parse.
        radix (int, optional): Base to convert to.

    Returns:
        mixed: Integer if parsable else ``None``.

    .. versionadded:: 1.0.0
    """
    if not radix and is_string(value):
        try:
            # Check if value is hexadcimal and if so use base-16 conversion.
            int(value, 16)
        except ValueError:
            pass
        else:
            radix = 16

    if not radix:
        radix = 10

    try:
        # NOTE: Must convert value to string when supplying radix to int().
        # Dropping radix arg when 10 is needed to allow floats to parse
        # correctly.
        args = (value,) if radix == 10 else (text_type(value), radix)
        parsed = int(*args)
    except (ValueError, TypeError):
        parsed = None

    return parsed


def pick(obj, callback=None, *properties):
    """Creates a shallow clone of object composed of the specified properties.
    Property names may be specified as individual arguments or as lists of
    property names. If a callback is provided it will be executed for each
    property of object picking the properties the callback returns truthy for.
    The callback is invoked with three arguments: ``(value, key, object)``.

    Args:
        obj (list|dict): Object to pick from.
        *properties (str): Property values to pick.
        callback (mixed, optional): Callback used to determine whic properties
            to pick.

    Returns:
        dict: Results of picking properties.

    .. versionadded:: 1.0.0
    """
    if not callable(callback):
        callback = callback if callback is not None else []
        properties = flatten_deep([callback, properties])
        callback = lambda value, key, item: key in properties

    return dict((key, value) for key, value in iterator(obj)
                if callback(value, key, obj))


def rename_keys(obj, key_map):
    """Rename the keys of `obj` using `key_map` and return new object.

    Args:
        obj (dict): Object to rename.
        key_map (dict): Renaming map whose keys correspond to existing keys in
            `obj` and whose values are the new key name.

    Returns:
        dict: Renamed `obj`.

    .. versionadded:: 2.0.0
    """
    return dict((key_map.get(key, key), value)
                for key, value in iteritems(obj))


def set_path(obj, value, keys, default=None):
    """Sets the value of an object described by `keys`. If any part of the
    object path doesn't exist, it will be created with `default`.

    Args:
        obj (list|dict): Object to modify.
        value (mixed): Value to set.
        keys (list): Target path to set value to.
        default (callable): Callable that returns default value to assign if
            path part is not set. Defaults to ``{}`` is `obj` is a ``dict`` or
            ``[]`` if `obj` is a ``list``.

    Returns:
        mixed: Modified `obj`.

    .. versionadded:: 2.0.0
    """
    return update_path(obj, lambda *_: value, keys, default=default)


def transform(obj, callback=None, accumulator=None):
    """An alernative to :func:`pydash.api.collections.reduce`, this method
    transforms `obj` to a new accumulator object which is the result of running
    each of its properties through a callback, with each callback execution
    potentially mutating the accumulator object. The callback is invoked with
    four arguments: ``(accumulator, value, key, object)``. Callbacks may exit
    iteration early by explicitly returning ``False``.

    Args:
        obj (list|dict): Object to process.
        callback (mixed): Callback applied per iteration.
        accumulator (mixed, optional): Accumulated object. Defaults to
            ``list``.

    Returns:
        mixed: Accumulated object.

    .. versionadded:: 1.0.0
    """
    if callback is None:
        callback = lambda accumulator, *args: accumulator

    if accumulator is None:
        accumulator = []

    for key, value in iterator(obj):
        result = callback(accumulator, value, key, obj)
        if result is False:
            break

    return accumulator


def update_path(obj, callback, keys, default=None):
    """Update the value of an object described by `keys` using `callback`. If
    any part of the object path doesn't exist, it will be created with
    `default`. The callback is invoked with the last key value of `obj`:
    ``(value)``

    Args:
        obj (list|dict): Object to modify.
        callback (callable): Function that returns updated value.
        keys (list): A list of string keys that describe the object path to
            modify.
        default (mixed): Default value to assign if path part is not set.
            Defaults to ``{}`` if `obj` is a ``dict`` or ``[]`` if `obj` is a
            ``list``.

    Returns:
        mixed: Updated `obj`.

    .. versionadded:: 2.0.0
    """
    if default is None:
        default = {} if isinstance(obj, dict) else []

    if not is_list(keys):
        keys = [keys]

    last_key = last(keys)
    obj = clone_deep(obj)
    target = obj

    for key in initial(keys):
        set_item(target, key, clone_deep(default), allow_override=False)
        target = target[key]

    set_item(target, last_key, callback(get_item(target,
                                                 last_key,
                                                 default=None)))

    return obj


def values(obj):
    """Creates a list composed of the values of `obj`.

    Args:
        obj (mixed): Object to extract values from.

    Returns:
        list: List of values.

    See Also:
        - :func:`values` (main definition)
        - :func:`values_in` (alias)

    .. versionadded:: 1.0.0

    .. versionchanged:: 1.1.0
       Added :func:`values_in` as alias.
    """
    return [value for _, value in iterator(obj)]


values_in = values
