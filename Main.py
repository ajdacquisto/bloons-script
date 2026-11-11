"""Run map selection and strategy automation for Bloons TD 6."""

# BTD6 Macro
# - Austin D'Acquisto

# F12 is the stop key

import logging
import time
from pathlib import Path
from collections.abc import Sequence

import constant as const
from Helper import GUI, Location, Map, Page
from Helper.ImageGrabTest import locate


LOGGER = logging.getLogger(__name__)


def wait_for_ui(name, timeout, coords=None):
    """Wait for a centrally calibrated target, optionally at data-driven locations."""
    target = const.UI_TARGETS[name]
    return wait_for_badge(
        const.FILE_PREFIX + target.filename,
        [target.coords] if coords is None else coords,
        timeout, [target.threshold], search_radius=target.radius, label=name,
        rounding=target.rounding,
    )


def wait_for_ui_any(names, timeout):
    """Wait for calibrated alternatives and return the matched target's index."""
    targets = [const.UI_TARGETS[name] for name in names]
    return wait_for_badge_2(
        [const.FILE_PREFIX + target.filename for target in targets],
        [[target.coords] for target in targets],
        timeout,
        thresholds=[[target.threshold] for target in targets],
        search_radii=[target.radius for target in targets],
        roundings=[target.rounding for target in targets],
        labels=list(names),
    )


def navigate(p, log=False):
    """Navigate from the detected page to the requested map-selection page."""
    if p is None:
        raise ValueError("navigate: Page is None")

    target_diff = p.difficulty
    target_subpage = p.subset_num

    current_page = identify_current_page(log)
    LOGGER.info("Navigating: page %s -> %s (difficulty %s, subpage %s)",
                current_page.number, p.number, p.difficulty, p.subset_num)
    if log:
        print(f"Trying to reach: {str(p)}")

    current_diff = current_page.difficulty
    current_subpage = current_page.subset_num

    if p == current_page:
        # Already in the correct section.
        # Already on the right page.
        pass
    elif target_diff == current_diff:
        # Already in the correct section.
        # Navigate to proper subpage in this section:
        difference = target_subpage - current_subpage
        if difference > 0:
            for i in range(difference):
                GUI.page_button(p.difficulty)
        elif difference < 0:
            n = Page.get_num_subpages(const.PAGES, p.difficulty)
            for i in range(n - abs(difference)):
                GUI.page_button(p.difficulty)
        else:
            # Should be on the right page already. Error somewhere
            raise RuntimeError
    else:
        # Need to switch sections:
        GUI.page_button(p.difficulty)

        # Navigate to proper subpage in this section:
        for i in range(target_subpage):
            GUI.page_button(p.difficulty)

    return p


def identify_current_page(log=False):
    """Identify the active map-selection page from its indicator."""
    target = const.UI_TARGETS["map_dot"]
    coord_list = Page.get_dot_coord_list(const.PAGES)
    _, match_coords = _wait_for_matches(
        [const.FILE_PREFIX + target.filename], [coord_list], 2,
        [[target.threshold]], [target.radius], ["map_dot"],
    )

    for p in const.PAGES:
        if p.dot_coords == match_coords:
            if log:
                print(f"Page identified. Currently on {str(p)}")
            return p
    raise Exception("identify_current_page: match_coords not in list.")


def beat_map(m) -> None:
    """Play a map's configured strategy and return to the main menu."""
    # Use rules to select the strategy to use.
    strategy_to_use = select_strategy(m)
    if strategy_to_use is None:
        raise ValueError(f"No strategy defined for {m.name}")

    # Click on the map that has been chosen.
    GUI.wait_click(0.1, m.page_location.x - 150, m.page_location.y)

    LOGGER.info("Playing %s: %s, hero %s", m.name,
                strategy_to_use.get_game_mode(), strategy_to_use.get_hero().get_name())

    # According to strategy: select the hero, difficulty, & gamemode
    select_hero_smart(strategy_to_use.get_hero())
    select_difficulty_smart(strategy_to_use.get_game_difficulty())
    select_gamemode_smart(strategy_to_use.get_game_mode())

    # Overwrite save if necessary
    overwrite_save_smart(timeout=1.5)

    # Let the map load
    if strategy_to_use.get_game_mode() == "Deflation":
        map_loading_wait(
            timeout=const.MAP_LOADING_TIMEOUT_DEFLATION, post_load_wait=0.8
        )
    else:
        try:
            map_loading_wait(timeout=6, post_load_wait=0.8)
        except TimeoutError:
            LOGGER.info("No introductory prompt detected; continuing Standard mode")

    dismiss_monkey_teams_smart()

    # Adjust auto start
    try:
        adjust_auto_start_smart(strategy_to_use.get_game_mode())
    except RuntimeError:
        raise RuntimeError("Unable to set auto start.")

    # Carry out series of Actions in Strategy
    perform_strategy(strategy_to_use, log_final_wait=True)

    # Game should be over by now. Handle game result.
    game_result = check_game_result(timeout=25, log_time_elapsed=True)
    match game_result:
        case 0:  # Win
            GUI.victory_next_button(0)
            GUI.victory_home_button(0.4)
            return True
        case 1:
            print("Loss")
            GUI.defeat_home_button(0)
            return False
        case _:
            raise ValueError("beat_map: Invalid game result.")


def select_hero_smart(hero, attempts=2):
    """Select a hero by scrolling to its card, then confirm its selected checkmark."""
    if hero.get_name() == "None":
        return
    last_row = max(h.row for h in Map.Map.HEROES)
    anchor, card = hero.get_card_position(last_row)
    dx, dy = const.HERO_SELECTED_OFFSET
    check = (card[0] + dx, card[1] + dy)
    LOGGER.info("Selecting hero %s: row %s col %s via %s anchor at %s",
                hero.get_name(), hero.row, hero.col, anchor, card)
    GUI.hero_change_button()
    GUI.wait(1.0)
    for attempt in range(1, attempts + 1):
        GUI.pick_hero_card(anchor, card)
        try:
            wait_for_ui("hero_selected", 3, coords=[check])
            break
        except TimeoutError as exc:
            if attempt == attempts:
                raise RuntimeError(
                    f"Could not confirm {hero.get_name()} was selected"
                ) from exc
            LOGGER.warning("Hero selection not confirmed; retrying (%s/%s)", attempt, attempts)
    GUI.back_arrow_button()


def adjust_auto_start_smart(target_game_mode: str) -> None:
    """Set auto-start as needed for the selected game mode."""
    # Set the auto-start if necessary
    if const.AUTO_START == -1:
        # still needs to be set.
        GUI.key_push("esc")
        try:
            const.AUTO_START = check_auto_start(10)
        except TimeoutError as exc:
            raise RuntimeError("Unknown auto-start setting state.") from exc
        if (target_game_mode == "Deflation" and const.AUTO_START == 0) or (
            target_game_mode == "Standard" and const.AUTO_START == 1
        ):
            GUI.auto_start_toggle_switch(0)
            toggle_auto_start()
        GUI.key_push("esc")
    else:
        if (target_game_mode == "Deflation" and const.AUTO_START == 0) or (
            target_game_mode == "Standard" and const.AUTO_START == 1
        ):
            GUI.key_push("esc")
            GUI.auto_start_toggle_switch(0)
            toggle_auto_start()
            GUI.key_push("esc")


def select_strategy(m):
    """Choose a map strategy, preferring the configured default mode."""
    strategy_list = m.strategy
    if strategy_list is None:
        return None

    try:
        num_strategies = len(strategy_list)
    except TypeError as exc:
        raise ValueError("select_strategy: m.strategy has no length") from exc

    if num_strategies < 1:
        return None
    if num_strategies == 1:
        return strategy_list[0]
    if num_strategies > 1:
        for s in strategy_list:
            if s.get_game_mode() == const.DEFAULT_MODE:
                return s
        # Just take first strategy if default mode is not available
        return strategy_list[0]


def select_gamemode_smart(mode):
    """Wait for and select the requested game mode."""
    if mode not in ("Deflation", "Standard"):
        raise ValueError("select_gamemode: Invalid gamemode.")
    name = mode.lower()
    wait_for_ui(name, 3)
    GUI.wait_click(0, *const.UI_CLICKS[name])


def select_difficulty_smart(diff):
    """Wait for and select the requested game difficulty."""
    match diff:
        case 0:
            wait_for_ui("easy", 3)
            GUI.wait_click(0, *const.UI_CLICKS["easy"])
        case _:
            raise ValueError("select_difficulty: Invalid difficulty.")


def overwrite_save_smart(timeout=1.5):
    """Overwrite an existing save when the prompt appears."""
    # Check for saved game, & overwrite if necessary
    try:
        wait_for_ui("overwrite", timeout)
    except TimeoutError:
        LOGGER.info("No overwrite prompt detected; continuing")
    else:
        GUI.wait_click(0, *const.UI_CLICKS["overwrite"])


def map_loading_wait(timeout=20, post_load_wait=0.8):
    """Wait for the map-loaded prompt and dismiss it."""
    # Check for map to be loaded.
    wait_for_ui("loaded", timeout)
    GUI.wait_click(0, *const.UI_CLICKS["loaded"])
    GUI.wait(post_load_wait)


def dismiss_monkey_teams_smart(timeout=2):
    """Dismiss the optional post-load notice and verify that it closes."""
    try:
        wait_for_ui("monkey_teams", timeout)
    except TimeoutError:
        LOGGER.info("No Monkey Teams notice detected; continuing")
        return

    GUI.wait_click(0, *const.UI_CLICKS["monkey_teams"])
    deadline = time.monotonic() + 3
    GUI.wait(0.8)
    target = const.UI_TARGETS["monkey_teams"]
    while True:
        GUI.exit_key_check()
        found, _, score = locate(
            const.FILE_PREFIX + target.filename, [target.coords], target.radius,
            [target.threshold], 0, target.rounding,
        )
        if not found:
            LOGGER.info("Monkey Teams notice dismissed")
            return
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise RuntimeError(
                f"Monkey Teams notice still visible after OK click "
                f"({score:.1%} match); stopping before strategy execution."
            )
        GUI.wait(min(const.VISION_POLL_INTERVAL, remaining))


def perform_strategy(s, log_final_wait=False):
    """Execute the strategy actions in order."""
    strategy_to_use = s
    action_list = strategy_to_use.get_actions()

    for i, a in enumerate(action_list):
        LOGGER.info("Strategy action %s/%s: %s", i + 1, len(action_list), a.get_name())
        if log_final_wait and i == len(action_list) - 1:
            # On final action.
            try:
                final_wait_time = int(a.get_info())
            except:
                final_wait_time = None
            print(f"<log>Final wait time: {final_wait_time}")
        execute_action(a)


def check_auto_start(timeout=5):
    """Detect whether auto-start is enabled or disabled."""
    try:
        result = wait_for_ui_any(("auto_start_off", "auto_start_on"), timeout)
    except TimeoutError as exc:
        raise TimeoutError("check_auto_start: Unknown result. Timed out.") from exc

    # result of 0: auto start is OFF
    # result of 1: auto start is ON
    # error thrown: unkown state

    return result


def toggle_auto_start():
    """Toggle the cached auto-start state."""
    current_state = const.AUTO_START
    if current_state != 0 and current_state != 1:
        raise ValueError
    elif current_state == 0:
        const.AUTO_START = 1
    else:
        const.AUTO_START = 0


def check_game_result(timeout=30, log_time_elapsed=False):
    """Wait for a victory or defeat indicator and return its index."""
    if log_time_elapsed:
        start_time = time.time()
    # Check for game result.
    try:
        game_result = wait_for_ui_any(("victory", "defeat"), timeout)
    except TimeoutError as exc:
        raise RuntimeError("beat_map: Unknown game result. Timed out.") from exc

    if log_time_elapsed:
        end_time = time.time()
        elapsed_time = round(abs(end_time - start_time), 3)
        if elapsed_time < 1 or elapsed_time > 2:
            print(f"<log>Time elapsed: {elapsed_time} <!>")
        else:
            print(f"<log>Time elapsed: {elapsed_time}")

    return game_result


def execute_action(a):
    """Execute one action from a map strategy."""
    match a.get_name():
        case "Tower":
            for t in a.info:
                do_tower_action(t)
        case "WaitSec":
            LOGGER.info("Fixed strategy wait: %s seconds (not watching for results)", a.info)
            GUI.center_cursor()
            GUI.wait(a.info)
        case "WaitRound":
            try:
                n = len(a.info)
            except TypeError:
                num_rounds_to_wait = a.info
                is_first_round = False
            else:
                if n == 2:
                    num_rounds_to_wait, is_first_round = a.info
                elif n == 1:
                    num_rounds_to_wait = a.info[1]
                    is_first_round = False
                else:
                    raise ValueError("execute_action: a.info is bad length.")

            round_timeout = 60

            for i in range(num_rounds_to_wait):
                # Start then wait
                GUI.key_push(" ")
                if is_first_round:
                    GUI.wait(0.1)
                    GUI.key_push(" ")
                    is_first_round = False
                GUI.center_cursor()
                GUI.wait(1.5)
                try:
                    wait_for_ui("round_stopped", round_timeout)
                except TimeoutError as exc:
                    raise RuntimeError("Round exceeded wait_time.") from exc

        case "Ability":
            GUI.key_push(a.info)
        case "Start":
            try:
                n = len(a.info)
            except TypeError:
                is_first_round = True
                wait_time = a.info
            else:
                if n == 2:
                    wait_time, is_first_round = a.info
                elif n == 1:
                    is_first_round = True
                    wait_time = a.info[0]
                else:
                    raise ValueError("execute_action: a.info is bad length.")
            # Start then wait
            GUI.key_push(" ")
            if is_first_round:
                GUI.wait(0.1)
                GUI.key_push(" ")
                is_first_round = False
            GUI.center_cursor()
            LOGGER.info("Starting play; fixed wait: %s seconds", wait_time)
            GUI.wait(wait_time)
        case _:
            raise ValueError("execute_action: Invalid action name.")


def do_tower_action(t):
    """Place, upgrade, target, or sell a tower."""
    LOGGER.info("Tower instruction: %s at %s, upgrade clicks %s, targeting tabs %s",
                t.name, t.get_position(), t.get_upgrades(), t.targeting)
    this_hot_key = t.get_hotkey()
    upgrade_keys = [",", ".", "/"]

    if this_hot_key == "bksp":
        GUI.sell_tower(t)
        return
    if this_hot_key != "0":
        GUI.place_tower(t)
    if t.upgrades == [0, 0, 0] and t.targeting == 0:
        return
    GUI.select_tower(t)

    # Upgrade tower
    u = t.get_upgrades()
    for path_num, upgrade_count in enumerate(u):
        for i in range(upgrade_count):
            GUI.wait(0.08)
            GUI.key_push(upgrade_keys[path_num])

    # Set targeting priority
    for n in range(t.targeting):
        GUI.wait(0.08)
        GUI.key_push("tab")

    GUI.deselect()


def _wait_for_matches(
    filenames: list[str],
    coord_lists: list[list[tuple[int, int]]],
    timeout: float,
    thresholds: Sequence[Sequence[float]],
    radii: list[int],
    labels: list[str],
    roundings: list[int] | None = None,
) -> tuple[int, tuple[int, int]]:
    """Poll with cancellation, bounded progress logs, and per-target diagnostics."""
    if timeout < 0:
        raise ValueError("Vision timeout must be nonnegative")
    if const.VISION_POLL_INTERVAL <= 0 or const.VISION_LOG_INTERVAL <= 0:
        raise ValueError("Vision poll and log intervals must be positive")
    if roundings is None:
        roundings = [1] * len(filenames)
    if not filenames or not (
        len(filenames) == len(coord_lists) == len(thresholds) == len(radii)
        == len(labels) == len(roundings)
    ):
        raise ValueError("Vision targets must have matching, nonempty settings")
    if any(rounding < 1 for rounding in roundings):
        raise ValueError("Vision rounding values must be positive")

    start = time.monotonic()
    deadline = start + timeout
    next_log = start + const.VISION_LOG_INTERVAL
    best: list[tuple[float, tuple[int, int]]] = [(-1.0, (0, 0)) for _ in filenames]
    descriptions = [
        f"{label} ({Path(filename).name}, coords={coords}, "
        f"threshold={limits}, radius={radius})"
        for label, filename, coords, limits, radius in
        zip(labels, filenames, coord_lists, thresholds, radii)
    ]
    LOGGER.info("Waiting up to %.1fs for %s", timeout, " OR ".join(descriptions))

    def summary() -> str:
        return "; ".join(
            f"{label}: best={score:.1%} at {coords}, required>{limits}"
            for label, (score, coords), limits in zip(labels, best, thresholds)
        )

    while True:
        GUI.exit_key_check()
        for index, (filename, coords, limits, radius, rounding) in enumerate(
            zip(filenames, coord_lists, thresholds, radii, roundings)
        ):
            GUI.exit_key_check()
            found, match_coords, score = locate(
                filename, coords, radius, limits, 0, rounding
            )
            if score > best[index][0]:
                best[index] = (score, match_coords)
            if found:
                LOGGER.info("Detected %s at %s: %.1f%% match after %.2fs",
                            labels[index], match_coords, 100 * score,
                            time.monotonic() - start)
                return index, match_coords
            if time.monotonic() >= deadline:
                break

        now = time.monotonic()
        if now >= deadline:
            message = f"Vision timed out after {now - start:.2f}s: {summary()}"
            LOGGER.warning(message)
            raise TimeoutError(message)
        if now >= next_log:
            LOGGER.info("Still waiting (%.1fs elapsed): %s", now - start, summary())
            next_log = now + const.VISION_LOG_INTERVAL
        GUI.wait(min(const.VISION_POLL_INTERVAL, deadline - now))


def wait_for_badge(
    filename, coords, timeout, threshold=None, *, search_radius=0, label=None,
    rounding=1,
):
    """Wait for one template; legacy scalar and per-coordinate thresholds work."""
    if threshold is None:
        threshold = [0.07]
    elif isinstance(threshold, (int, float)):
        threshold = [threshold]
    _wait_for_matches(
        [filename], [coords], timeout, [threshold], [search_radius],
        [label if label is not None else Path(filename).name], [rounding],
    )
    return True


def wait_for_badge_2(
    filenames,
    coordMx,  # pylint: disable=invalid-name
    timeout,
    match_threshold=None,
    *,
    thresholds=None,
    search_radii=None,
    roundings=None,
    labels=None,
):
    """Wait for any of the supplied templates and return its index."""
    if match_threshold is None:
        match_threshold = [0.07]
    count = len(filenames)
    index, _ = _wait_for_matches(
        filenames, coordMx, timeout,
        thresholds if thresholds is not None else [match_threshold] * count,
        search_radii if search_radii is not None else [0] * count,
        labels if labels is not None else [Path(name).name for name in filenames],
        roundings,
    )
    return index


def find_rewards_map(diff, filename, rad=0):
    """Search playable map cards for a reward badge and return the matching map."""
    curr_debug_mode = rad != 0

    mode = 0
    rou = 1
    t_list = const.get_matches()
    c_list = Location.get_coord_list()
    if len(t_list) not in (1, len(c_list)):
        raise ValueError(
            f"Expected 1 or {len(c_list)} reward thresholds, got {len(t_list)}"
        )
    playable_maps = Map.get_playable_maps(const.MAPS)

    current_page = navigate(Page.get_page_by_info(const.PAGES, diff, 1))

    # Check for expert button before continuing.
    wait_for_ui("expert", 5)

    m_found = False
    m_coords = (0, 0)
    m_ratio = 0.0
    notable = (None, (0, 0), 0)
    # pageNum, coords, matchRatio

    for _ in range(Page.get_num_subpages(const.PAGES, diff)):
        playable_coords = {
            (m.page_location.x, m.page_location.y)
            for m in playable_maps if m.page == current_page.number
        }
        indexes = [i for i, coords in enumerate(c_list) if coords in playable_coords]
        if indexes:
            LOGGER.info("Searching reward badge on page %s, radius %s (%s playable slots)",
                        current_page.number, rad, len(indexes))
            GUI.wait(0.4)
            scan_coords = [c_list[i] for i in indexes]
            scan_thresholds = t_list if len(t_list) == 1 else [t_list[i] for i in indexes]
            m_found, m_coords, m_ratio = locate(
                filename, scan_coords, rad, scan_thresholds, mode, rou,
                debug_mode=curr_debug_mode,
            )

            if curr_debug_mode:
                print(f"# [{m_coords[0]} {m_coords[1]}] {percentage(m_ratio)} match.")

            if m_ratio > notable[2]:
                notable = (current_page, m_coords, m_ratio)

            if m_found:
                break
        else:
            LOGGER.info("Skipping reward scan on page %s: no maps with strategies",
                        current_page.number)

        if curr_debug_mode:
            print("-> Next page.")
        current_page = navigate(Page.get_next_in_diff(const.PAGES, current_page))

    if m_found:
        match_page, match_coords, match_ratio = current_page, m_coords, m_ratio
    else:
        match_page, match_coords, match_ratio = notable
        if match_page is None or match_ratio <= 0.01:
            print("Done searching. [No matches found]")
            return None

    match_location = Location.get_loc_from_coords(match_coords)
    if match_location is None:
        raise RuntimeError("find_rewards_map: Locate returned invalid coords.")

    loc_num = Location.get_loc_num(match_location)
    threshold_index = 0 if len(t_list) == 1 else loc_num
    prev_min_ratio = t_list[threshold_index]
    if not m_found:
        print(
            f"No {100*prev_min_ratio}% matches, but a "
            f"{percentage(match_ratio)} match was found."
        )
        if match_ratio <= prev_min_ratio:
            const.set_match(threshold_index, match_ratio, do_reporting=True)

    return Map.get_map_from_location(playable_maps, match_page.number, match_location)


def percentage(decimal):
    """Format a decimal fraction as a percentage."""
    return str(round(100 * decimal, 1)) + "%"


### Start of Main ###
def main():
    """Run the map-selection and gameplay loop."""
    logging.basicConfig(
        level=const.LOG_LEVEL, format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
    )
    const.init()
    LOGGER.info("Starting macro: origin=%s, selection mode=%s, default=%s/%s; "
                "%s stops input", const.GAME_SCREEN_ORIGIN,
                const.MAP_SELECTION_MODE, const.DEFAULT_MAP, const.DEFAULT_MODE,
                const.STOP_KEY.upper())
    try:
        GUI.check_input_vars(
            const.MAPS,
            (
                const.POST_WIN_WAIT,
                const.MAP_LOADING_TIME,
                const.DEFAULT_MAP,
                const.MAP_SELECTION_MODE,
            ),
        )
    except ValueError as exc:
        raise ValueError(f"Invalid settings: {exc}") from exc

    GUI.wait_click(0, *const.UI_CLICKS["focus"])

    i = 0
    money_earned = 0
    while True:
        # Wait for home screen before continuing.
        try:
            wait_for_ui("home_play", 30)
        except TimeoutError as exc:
            raise RuntimeError("Must start on home screen. Timed out.") from exc
        GUI.play_button(0)

        # Check for expert button before continuing.
        wait_for_ui("expert", 5)

        match const.MAP_SELECTION_MODE:
            case 0:
                m = Map.get_map_by_name(const.MAPS, const.DEFAULT_MAP)
            case 1:
                m = Map.pick_rand(const.MAPS)
            case 2:  # Play maps in order
                m = Map.pick_ordered(const.MAPS, i)
            case 3:
                search_file = const.FILE_PREFIX + const.BADGE_NAME
                m = find_rewards_map(diff=3, filename=search_file)
                if m is None:
                    m = Map.get_map_by_name(const.MAPS, const.DEFAULT_MAP)
            case 4:
                search_file = const.FILE_PREFIX + const.BADGE_NAME
                m = find_rewards_map(diff=3, filename=search_file)
                if m is None:
                    m = Map.pick_ordered(const.MAPS, i)
            case 5:
                exp_rad = 0
                search_file = const.FILE_PREFIX + const.BADGE_NAME
                m = find_rewards_map(diff=3, filename=search_file)
                while m is None and exp_rad < 20:
                    exp_rad += 1
                    print(f"Expanding. New radius:{exp_rad}")
                    m = find_rewards_map(
                        diff=3, filename=search_file, rad=exp_rad
                    )
                if m is None:
                    m = Map.pick_ordered(const.MAPS, i)
            case _:
                raise ValueError("Invalid Map Selection Mode.")

        print(f"{i+1}.\t{m.name}")
        navigate(const.PAGES[m.page])
        is_win = beat_map(m)

        if is_win:
            money_earned += 66
        print("Money earned: $", money_earned)

        GUI.wait(1)

        try:
            reward_status = wait_for_ui_any(("home_play", "collect"), 25)
        except TimeoutError as exc:
            raise RuntimeError("Unknown free monkey status. Timed out.") from exc
        match reward_status:
            case 0:
                pass  # No free monkeys
            case 1:
                GUI.accept_free_monkeys()
            case _:
                raise Exception("main: Impossible free monkey status.")

        i += 1
    # end of while


# end of main

if __name__ == "__main__":
    main()
