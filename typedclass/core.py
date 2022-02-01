# Copyright (C) nerdguyahmad 2022-present
# Under the MIT license, See LICENSE for more details.

from __future__ import annotations

from typedclass import helpers
import typing

TC = typing.TypeVar("TC", bound="TypedClass")

class TypedClass:
    """Represents a typed class that provides type validation at runtime.

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
        return helpers.prepare_typed_instance(instance, kwargs)

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
