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

    def __eq__(s1, s2) -> bool:
        if s1.get_game_difficulty() != s2.get_game_difficulty():
            return False
        if s1.get_game_mode() != s2.get_game_mode():
            return False
        if s1.get_hero() != s2.get_hero():
            return False
        for ac1, ac2 in zip(s1.get_actions(), s2.get_actions()):
            if ac1 != ac2:
                return False
        return True

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
