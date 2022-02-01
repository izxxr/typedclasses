# Copyright (C) nerdguyahmad 2022-present
# Under the MIT license, See LICENSE for more details.

from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    from typedclass.core import TypedClass

    TC = typing.TypeVar("TC", bound="TypedClass")

def is_valid(val: typing.Any, tp: type):
    return isinstance(val, tp)

def prepare_typed_instance(tc: TC, params: typing.Dict[str, typing.Any]) -> TC:
    options = tc.__tc_options__

    required_params = options["required_params"]
    optional_params = options["optional_params"]

    missing_params = []

    for p_name, p_type in required_params.items():
        if not p_name in params:
            missing_params.append(p_name)
            continue

        val = params[p_name]

        if not is_valid(val, p_type):
            raise TypeError(f"Parameter {p_name!r} in {tc.__class__.__name__}() must be an " \
                            f"instance of {p_type!r}, Not {val.__class__!r}")

        setattr(tc, p_name, val)
        params.pop(p_name)


    if missing_params:
        raise TypeError(f"{tc.__class__.__name__}() is missing required parameters " \
                        f"{', '.join(repr(p) for p in missing_params)}")

    for p_name, p_type in optional_params.items():
        if not p_name in params:
            continue

        val = params[p_name]
        if not is_valid(val, p_type):
            raise TypeError(f"Parameter {p_name!r} in {tc.__class__.__name__}() must be an " \
                            f"instance of {p_type!r}, Not {val.__class__!r}")

        setattr(tc, p_name, val)
        params.pop(p_name)

    if params:
        raise TypeError(f"{tc.__class__.__name__}() got unexpected parameters " \
                        f"{', '.join(repr(p) for p in params)}")

    return tc