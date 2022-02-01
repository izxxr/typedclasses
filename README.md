# typed-class
Python classes with types validation at runtime. ***(Experimental & Under Development)***

## Installation
You can install this library using Python's favorite, `pip` package manager. 

```sh
pip install -U typed-class
```

## How it works
Using typedclass, you can create classes in `dataclasses`-like manner i.e using type annotations and library will enforce types for
that class at runtime. Here's an example:

```py
import typing
from typedclass import TypedClass

class User(TypedClass):
  id: int
  name: str
  email: typing.Optional[str] = None
```

Parameters will be validated when initialising above class. Since `email` has a default value set, It is optional to pass
it as a parameter while instansiating:

```py
>>> User(id=1, name="foobar") # runs fine
>>> User(id="1", name="foobar")
TypeError: Parameter 'id' must be an instance of <class 'int'>, <class 'str'> is unsupported.
```

This library also provides validation for *various* generic types from `typing` module:

```py
class Foo(TypedClass):
  str_or_int: typing.Union[str, int]
  
Foo("a") # ok
Foo(1) # ok
Foo(True) # invalid
```

List of all types supported from `typing` module can be found in the documentation.
