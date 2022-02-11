# Copyright (C) nerdguyahmad 2022-present
# Under the MIT license, See LICENSE for more details.

from __future__ import annotations

from typedclasses._internal import prepare_typed_instance
import typing

TC = typing.TypeVar("TC", bound="TypedClass")

def _typed_class_repr(self: TypedClass) -> str:
    ret = f"{self.__class__.__name__}(%s)"
    params = self.__tc_options__["params"]
    return ret % (", ".join(f"{k}={getattr(self, k)!r}" for k in params))

class TypedClass:
    """Represents a typed class that provides robust type validation at runtime.

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
    ignore_extra: :class:`builtins.bool`
        Whether to ignore extra keyword parameters passed during initialization.
        Defaults to ``False``.
    repr: :class:`builtins.bool`
        Whether to add a ``__repr__`` method to the class. Defaults to ``True``.
    """

    __tc_options__: typing.Dict[str, typing.Any]

    def __new__(cls: type[TC], *args, **kwargs) -> TC:
        if args:
            raise TypeError(f"{cls.__name__}() takes no positional arguments.")

        instance = super().__new__(cls)
        return prepare_typed_instance(instance, kwargs)

    def __init_subclass__(cls,
        ignore_internal: bool = True,
        ignore_extra: bool = False,
        repr: bool = True,
    ) -> None:

        cls.__tc_options__ = options = dict()

        # Passing parameters to options
        options["ignore_extra"] = ignore_extra

        optional_params = options.get("optional_params", dict())
        required_params = options.get("required_params", dict())

        members = vars(cls)

        # cls.__annotations__ may have stringified values when using
        # 'from __future__ import annotations' so using typing.get_type_hints()
        # to get proper annotations.

        annotations = typing.get_type_hints(cls)
        params = []

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

            params.append(name)

        # Update the options with new ones.
        options["optional_params"] = optional_params
        options["required_params"] = required_params

        options["params"] = params

        if repr:
            cls.__repr__ = _typed_class_repr