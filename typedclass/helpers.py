# Copyright (C) nerdguyahmad 2022-present
# Under the MIT license, See LICENSE for more details.

from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    from typedclass.core import TypedClass

    TC = typing.TypeVar("TC", bound="TypedClass")

def apply_from_typing_origin(origin, tc: TypedClass, val: typing.Any, tp: type, name: str):
    args = typing.get_args(tp)

    if origin is typing.Union and args[1] is type(None):
        # typing.Optional[tp] is used which is internally taken
        # as typing.Union[tp, None] so args[0] would be our required type.
        if val is None:
            return True

        if not isinstance(val, args[0]):
            raise TypeError(f"Parameter {name!r} in {tc.__class__.__name__}() must be None or " \
                            f"{args[0]!r}, Not {val.__class__!r}")

        return setattr(tc, name, val)

def apply_attr(tc: TypedClass, val: typing.Any, tp: type, name: str):
    origin = typing.get_origin(tp)

    if origin is not None:
        apply_from_typing_origin(origin, tc, val, tp, name)
        return

    if not isinstance(val, tp):
        raise TypeError(f"Parameter {name!r} in {tc.__class__.__name__}() must be an " \
                        f"instance of {tp!r}, Not {val.__class__!r}")

    setattr(tc, name, val)

def prepare_typed_instance(tc: TC, params: typing.Dict[str, typing.Any]) -> TC:
    options = tc.__tc_options__

    required_params = options["required_params"]
    optional_params = options["optional_params"]

    missing_params = []

    for p_name, p_type in required_params.items():
        if not p_name in params:
            missing_params.append(p_name)
            continue

        apply_attr(tc, params[p_name], p_type, p_name)
        params.pop(p_name)


    if missing_params:
        raise TypeError(f"{tc.__class__.__name__}() is missing required parameters " \
                        f"{', '.join(repr(p) for p in missing_params)}")

    for p_name, p_type in optional_params.items():
        if not p_name in params:
            continue

        apply_attr(tc, params[p_name], p_type, p_name)
        params.pop(p_name)

    if params:
        raise TypeError(f"{tc.__class__.__name__}() got unexpected parameters " \
                        f"{', '.join(repr(p) for p in params)}")

    return tc