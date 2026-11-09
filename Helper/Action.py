from typing import List


class Action:
    def __init__(self, name: str, info: List[any]):
        self.name = name  # 'Tower' 'Wait' 'Ability' 'Start'
        self.info = info  # list of Tower, or Integer, or String

    def __eq__(a1, a2) -> bool:
        if a1.name != a2.name:
            return False
        return a1.info == a2.info

    def __str__(self) -> str:
        return str(self.name) + ": " + str(self.info)

    def get_name(self) -> str:
        return self.name

    def get_info(self) -> List[any]:
        return self.info
