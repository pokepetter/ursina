import sys
import warnings
# can removed when Python3.13 releases
class deprecated:
    def __init__(self, message: str, /, *, category: type[Warning] | None = DeprecationWarning, stacklevel: int = 1, ) -> None:
        if not isinstance(message, str):
            raise TypeError(f"Expected an object of type str for 'message', not {type(message).__name__!r}")
        self.message = message
        self.category = category
        self.stacklevel = stacklevel

    def __call__(self, arg, /):
        msg = self.message
        category = self.category
        stacklevel = self.stacklevel
        if category is None:
            arg.__deprecated__ = msg
            return arg
        elif isinstance(arg, type):
            import functools
            from types import MethodType

            original_new = arg.__new__

            @functools.wraps(original_new)
            def __new__(cls, *args, **kwargs):
                if cls is arg:
                    warnings.warn(msg, category=category, stacklevel=stacklevel + 1)
                if original_new is not object.__new__:
                    return original_new(cls, *args, **kwargs)
                # Mirrors a similar check in object.__new__.
                elif cls.__init__ is object.__init__ and (args or kwargs):
                    raise TypeError(f"{cls.__name__}() takes no arguments")
                else:
                    return original_new(cls)

            arg.__new__ = staticmethod(__new__)

            original_init_subclass = arg.__init_subclass__
            # We need slightly different behavior if __init_subclass__
            # is a bound method (likely if it was implemented in Python)
            if isinstance(original_init_subclass, MethodType):
                original_init_subclass = original_init_subclass.__func__

                @functools.wraps(original_init_subclass)
                def __init_subclass__(*args, **kwargs):
                    warnings.warn(msg, category=category, stacklevel=stacklevel + 1)
                    return original_init_subclass(*args, **kwargs)

                arg.__init_subclass__ = classmethod(__init_subclass__)
            # Or otherwise, which likely means it's a builtin such as
            # object's implementation of __init_subclass__.
            else:
                @functools.wraps(original_init_subclass)
                def __init_subclass__(*args, **kwargs):
                    warnings.warn(msg, category=category, stacklevel=stacklevel + 1)
                    return original_init_subclass(*args, **kwargs)

                arg.__init_subclass__ = __init_subclass__

            arg.__deprecated__ = __new__.__deprecated__ = msg
            __init_subclass__.__deprecated__ = msg
            return arg
        elif callable(arg):
            import functools

            @functools.wraps(arg)
            def wrapper(*args, **kwargs):
                warnings.warn(msg, category=category, stacklevel=stacklevel + 1)
                return arg(*args, **kwargs)

            arg.__deprecated__ = wrapper.__deprecated__ = msg
            return wrapper
        else:
            raise TypeError(
                "@deprecated decorator with non-None category must be applied to "
                f"a class or callable, not {arg!r}"
            )


_DEPRECATED_MSG = "{name!r} is deprecated and slated for removal in Python {remove}"

def _deprecated(name, message=_DEPRECATED_MSG, *, remove, _version=sys.version_info):
    remove_formatted = f"{remove[0]}.{remove[1]}"
    if (_version[:2] > remove) or (_version[:2] == remove and _version[3] != "alpha"):
        msg = f"{name!r} was slated for removal after Python {remove_formatted} alpha"
        raise RuntimeError(msg)
    else:
        msg = message.format(name=name, remove=remove_formatted)
        warnings.warn(msg, DeprecationWarning, stacklevel=3)
