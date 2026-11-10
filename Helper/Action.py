"""Represent actions performed by a map strategy."""

from typing import Generic, TypeVar


_InfoT = TypeVar("_InfoT")


class Action(Generic[_InfoT]):
    """Pair an action name with its associated payload."""

    def __init__(self, name: str, info: _InfoT):
        self.name = name  # 'Tower' 'Wait' 'Ability' 'Start'
        self.info = info  # list of Tower, or Integer, or String

    def __eq__(a1, a2) -> bool:
        if a1.name != a2.name:
            return False
        return a1.info == a2.info

    def __str__(self) -> str:
        return str(self.name) + ": " + str(self.info)

    def get_name(self) -> str:
        """Return the action name."""
        return self.name

    def get_info(self) -> _InfoT:
        """Return the action payload."""
        return self.info
