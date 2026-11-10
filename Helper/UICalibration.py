"""Central image targets and game-local click positions."""

from dataclasses import dataclass


@dataclass(frozen=True)
class UITarget:
    """Describe a template match independently of the monitor's desktop origin."""

    filename: str
    coords: tuple[int, int]
    threshold: float = 0.07
    radius: int = 0


# Uncalibrated targets retain their legacy thresholds and coordinates.
UI_TARGETS = {
    "home_play": UITarget("homePlay.png", (960, 945), 0.90),
    "expert": UITarget("expert.png", (1337, 974), 0.85, 2),
    "easy": UITarget("selectEasy.png", (627, 406), 0.85, 2),
    "standard": UITarget("modeStandard.png", (667, 593), 0.85, 2),
    "deflation": UITarget("modeDeflation.png", (1322, 494), 0.85, 2),
    "auto_start_off": UITarget("autoStartOff.png", (1325, 307), 0.5),
    "auto_start_on": UITarget("autoStartOn.png", (1325, 307), 0.5),
    # Actual centers are supplied from pageInfo.dat.
    "map_dot": UITarget("mapDot.png", (0, 0), 0.85, 1),
    "overwrite": UITarget("overwriteBadge.png", (570, 379)),
    "loaded": UITarget("loaded2.png", (960, 392)),
    "round_stopped": UITarget("roundStopped.png", (1832, 1016), 0.90),
    "victory": UITarget("win.png", (944, 209)),
    "defeat": UITarget("loss.png", (944, 209)),
    "collect": UITarget("collectBadge.png", (960, 679)),
}

# Click positions can differ from a template's center.
UI_CLICKS = {
    "focus": (1900, 0),
    "center": (960, 540),
    "home_play": UI_TARGETS["home_play"].coords,
    "easy": (618, 417),
    "standard": (634, 587),
    "deflation": (1293, 475),
    "auto_start": (1325, 307),
    "overwrite": (1137, 729),
    "loaded": (969, 758),
    "change_hero": (104, 990),
    "select_hero": (1116, 615),
    "back": (80, 50),
    "victory_next": (958, 909),
    "victory_home": (718, 842),
    "defeat_home": (738, 805),
    "escape_cancel": (796, 747),
    "free_monkey_continue": (957, 674),
    "beginner_tab": (582, 977),
    "intermediate_tab": (834, 977),
    "advanced_tab": (1086, 977),
    "expert_tab": (1338, 977),
}
