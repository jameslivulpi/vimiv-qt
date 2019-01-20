# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""`Utilities to map commands to a sequence of keys`.

Adding a new default keybinding is done using the :func:`register` decorator.
This decorator requires the sequence of keys to bind to as first argument, the
command as second argument and, similar to :func:`vimiv.api.commands.register`
supports the ``mode`` keyword to define the mode in which the keybinding is
valid.

As an example, let's bind the ``:hello-earth`` command from before to the key
sequence ``ge``::

    from vimiv.api import commands, keybindings

    @keybindings.register("ge", "hello-earth")
    @commands.register()
    def hello_earth():
        print("hello earth")

If the keybinding requires passing any arguments to the command, these must be
passed as part of the command. For example, to great venus with ``gv`` and
earth with ``ge`` we could use::

    @keybindings.register("gv", "hello-planet --name=venus")
    @keybindings.register("ge", "hello-planet")
    @commands.register()
    def hello_planet(name: str = "earth"):
        print("hello", name)
"""

import collections
from typing import Any, Callable, ItemsView

from . import commands, modes


def register(
    keybinding: str, command: str, mode: modes.Mode = modes.GLOBAL
) -> Callable:
    """Decorator to add a new keybinding.

    Args:
        keybinding: Key sequence to bind.
        command: Command to bind to.
        mode: Mode in which the keybinding is valid.
    """

    def decorator(function: Callable) -> Callable:
        bind(keybinding, command, mode)

        def inside(*args: Any, **kwargs: Any) -> None:
            return function(*args, **kwargs)

        return inside

    return decorator


def bind(keybinding: str, command: str, mode: modes.Mode) -> None:
    """Store keybinding in registry.

    See config/configcommands.bind for the corresponding command.
    """
    _registry[mode][keybinding] = command


def unbind(keybinding: str, mode: modes.Mode) -> None:
    """Remove keybinding from registry.

    See config/configcommands.unbind for the corresponding command.
    """
    if mode in modes.GLOBALS and keybinding in _registry[modes.GLOBAL]:
        del _registry[modes.GLOBAL][keybinding]
    elif keybinding in _registry[mode]:
        del _registry[mode][keybinding]
    else:
        raise commands.CommandError("No binding found for '%s'" % (keybinding))


class _Bindings(collections.UserDict):
    """Store keybindings of one mode.

    Essentially a simple python dictionary which is stored in the module
    attribute _registry at initialization so it can be accessed with the
    get(mode) function.
    """

    def __add__(self, other: "_Bindings") -> "_Bindings":
        if not isinstance(other, _Bindings):
            raise ValueError(
                "Cannot add type '%s' to '%s'"
                % (other.__name__, self.__class__.__qualname__)
            )
        return _Bindings({**self, **other})

    def partial_match(self, keys: str) -> bool:
        """Check if keys match some of the bindings partially.

        Args:
            keys: String containing the keynames to check, e.g. "g".
        Return:
            True for match.
        """
        if not keys:
            return False
        for binding in self:
            if binding.startswith(keys):
                return True
        return False


_registry = {mode: _Bindings() for mode in modes.ALL}


def get(mode: modes.Mode) -> _Bindings:
    """Return the keybindings of one specific mode."""
    if mode in modes.GLOBALS:
        return _registry[mode] + _registry[modes.GLOBAL]
    return _registry[mode]


def items() -> ItemsView[modes.Mode, _Bindings]:
    return _registry.items()


def clear() -> None:
    """Clear all keybindings."""
    for bindings in _registry.values():
        bindings.clear()