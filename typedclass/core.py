# Copyright (C) nerdguyahmad 2022-present
# Under the MIT license, See LICENSE for more details.

from __future__ import annotations

import inspect
import typing

TC = typing.TypeVar("TC", bound="TypedClass")

class TypedClass:
    """Represents a typed class that provides type validation at runtime.

    Example::

        class User(typedclass.TypedClass):
            id: int
            name: str
            email: typing.Optional[str] = None # default value is set so this is optional.

        >>> User(id=1, name='foo') # ok
        >>> User(id='1', name='foo')
        TypeError: Parameter 'id' in User() must be an instance of <class 'int'>, Not <class 'str'>

    Following generic classes from :py-module:`typing` are also supported
    and properly validated by this class:

    - :py-class:`typing.Optional`
    - :py-class:`typing.Union`
    - :py-class:`typing.Type`
    - :py-class:`typing.Literal`

    Support for other generic types will also be added soon. If you want to suggest
    one, Consider opening an issue on our GitHub repository!

    Subclassing Parameters
    ----------------------
    ignore_internal: :class:`builtins.bool`
        Whether to ignore the annotations starting with single underscore.
        Defaults to ``True``.
    """

    __tc_options__: typing.Dict[str, typing.Any]

    def __new__(cls: type[TC], *args, **kwargs) -> TC:
        if args:
            raise TypeError(f"{cls.__name__}() takes no positional arguments.")

        instance = super().__new__(cls)
        return prepare_typed_instance(instance, kwargs)

    def __init_subclass__(cls, ignore_internal: bool = True) -> None:
        cls.__tc_options__ = options = dict()

        optional_params = options.get("optional_params", dict())
        required_params = options.get("required_params", dict())

        members = vars(cls)

        # cls.__annotations__ may have stringified values when using
        # 'from __future__ import annotations' so using typing.get_type_hints()
        # to get proper annotations.

        annotations = typing.get_type_hints(cls)

        for name, tp in annotations.items():
            if name.startswith("__"):
                continue
            if name.startswith("_") and ignore_internal:
                continue

            if name in members:
                if name in required_params:
                    # name can be in required_params when inheriting
                    # a typed class, so remove it.
                    required_params.pop(name)

                optional_params[name] = tp
            else:
                if name in optional_params:
                    optional_params.pop(name)

                required_params[name] = tp

        # Update the options with new ones.
        options["optional_params"] = optional_params
        options["required_params"] = required_params


def apply_from_typing_origin(origin, tc: TypedClass, val: typing.Any, tp: type, name: str):
    args = typing.get_args(tp)

    if origin is typing.Union and args[1] is type(None) and len(args) == 2:
        # typing.Optional[tp] is used which is internally taken
        # as typing.Union[tp, None] so args[0] would be our required type.

        if val is not None and not isinstance(val, args[0]):
            raise TypeError(f"Parameter {name!r} in {tc.__class__.__name__}() must be None or " \
                            f"{args[0]!r}, Not {val.__class__!r}")

        return setattr(tc, name, val)

    elif origin is typing.Union:
        for arg in args:
            origin = typing.get_origin(arg)

            if origin is not None:
                try:
                    apply_from_typing_origin(origin, tc, val, arg, name)
                except TypeError:
                    continue
                else:
                    return

            if isinstance(val, arg):
                setattr(tc, name, val)
                return

        raise TypeError(f"Parameter {name!r} in {tc.__class__.__name__}() must be an instance " \
                        f"of one of {', '.join(repr(arg) for arg in args)}, Not {val.__class__!r}")

    elif origin is typing.Literal:
        for arg in args:
            if val is arg:
                setattr(tc, name, tp)
                return

        raise TypeError(f"Parameter {name!r} in {tc.__class__.__name__}() must be exactly one " \
                        f"of {', '.join(repr(arg) for arg in args)}, Not {val!r}")

    elif origin is type:
        if not inspect.isclass(val) or not issubclass(val, args[0]):
            raise TypeError(f"Parameter {name!r} in {tc.__class__.__name__}() must be a type "
                            f"instance of {args[0]!r}, Not {val!r}")

        setattr(tc, name, val)

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