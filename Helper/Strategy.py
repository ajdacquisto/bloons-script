from Helper.Hero import Hero
from Helper.Action import Action
from typing import List


class Strategy:
    def __init__(
        self, game_difficulty: int, game_mode: str, hero: Hero, actions: List[Action]
    ):
        self.game_difficulty = game_difficulty  # int [0-2]
        self.game_mode = game_mode  # str "Xx xx"
        self.hero = hero  # Hero type
        self.actions = actions  # [Action, Action, ...]

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Strategy):
            return NotImplemented
        if self.get_game_difficulty() != other.get_game_difficulty():
            return False
        if self.get_game_mode() != other.get_game_mode():
            return False
        if self.get_hero() != other.get_hero():
            return False
        return self.get_actions() == other.get_actions()

    def __str__(self) -> str:
        action_list_str = "(" + ",".join(str(a) for a in self.actions) + ")"
        d = self.get_game_difficulty()
        m = self.get_game_mode()
        h = self.get_hero()
        return f"S[diff={d},mode={m},hero={h},actions={action_list_str}]"

    def get_game_difficulty(self) -> int:
        return self.game_difficulty

    def get_game_mode(self) -> str:
        return self.game_mode

    def get_hero(self) -> Hero:
        return self.hero

    def get_actions(self) -> List[Action]:
        return self.actions
