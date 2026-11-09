# BTD6 Macro
# - Austin D'Acquisto

# Caps lock is the quit key

from Helper import GUI
from Helper.ImageGrabTest import locate
from Helper import Location
from Helper import Map
from Helper import Page

import constant as const
import pyautogui as pg
import time


def navigate(p, log=False):
    if p is None:
        raise ValueError("navigate: Page is None")

    target_diff = p.difficulty
    target_subpage = p.subset_num

    current_page = identify_current_page(log)
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
            n = Page.get_num_subpages(p.difficulty)
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
    SEARCH_RADIUS = 0
    SEARCH_MODE = 0
    ROUNDING = 1
    THRESHOLD = [0.08]
    FILENAME = const.FILE_PREFIX + "mapDot.png"
    COORD_LIST = Page.get_dot_coord_list(const.PAGES)
    TIMEOUT = 2  # seconds
    match_found = False
    match_found, match_coords, match_percent = locate(
        FILENAME, COORD_LIST, SEARCH_RADIUS, THRESHOLD, SEARCH_MODE, ROUNDING
    )

    start_time = time.time()
    while (not match_found) and abs(time.time() - start_time) <= TIMEOUT:
        GUI.exit_key_check()
        match_found, match_coords, match_percent = locate(
            FILENAME, COORD_LIST, SEARCH_RADIUS, THRESHOLD, SEARCH_MODE, ROUNDING
        )

    if not match_found:
        raise Exception("identify_current_page: Unable to identify current page.")

    for p in const.PAGES:
        if p.dot_coords == match_coords:
            if log:
                print(f"Page identified. Currently on {str(p)}")
            return p
    raise Exception("identify_current_page: match_coords not in list.")


def beat_map(m) -> None:
    """
    beat_map will click on the map's menu location (assuming already navigated to proper page) and
    execute each Action in Strategy for the given map. Starts the game, waits for it to end, and returns
    to the main menu.

    :param m: Map variable represents the map to beat.
    :return: No return value.
    """
    # Click on the map that has been chosen.
    GUI.wait_click(0.1, m.page_location.x - 150, m.page_location.y)

    # Use rules to select the strategy to use.
    strategy_to_use = select_strategy(m)

    # According to strategy: select the hero, difficulty, & gamemode
    GUI.select_hero(strategy_to_use.get_hero())
    select_difficulty_smart(strategy_to_use.get_game_difficulty())
    select_gamemode_smart(strategy_to_use.get_game_mode())

    # Overwrite save if necessary
    overwrite_save_smart(timeout=1.5)

    # Let the map load
    try:
        map_loading_wait(timeout=6, post_load_wait=0.8)
    except RuntimeError:
        if strategy_to_use.get_game_mode() == "Deflation":
            raise SystemExit
        elif strategy_to_use.get_game_mode() == "Standard":
            pass
        else:
            raise RuntimeError("Unkown gamemode")

    # Adjust auto start
    try:
        adjust_auto_start_smart(strategy_to_use.get_game_mode())
    except RuntimeError:
        raise RuntimeError("Unable to set auto start.")

    # Carry out series of Actions in Strategy
    perform_strategy(strategy_to_use, log_final_wait=True)

    # Game should be over by now. Handle game result.
    G = check_game_result(timeout=25, log_time_elapsed=True)
    match G:
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


def adjust_auto_start_smart(target_game_mode: str) -> None:
    # Set the auto-start if necessary
    if const.AUTO_START == -1:
        # still needs to be set.
        GUI.key_push("esc")
        try:
            const.AUTO_START = check_auto_start(10)
        except TimeoutError:
            raise RuntimeError("Unkown auto-start setting state.")
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
    strategy_list = m.strategy

    try:
        num_strategies = len(strategy_list)
    except:
        raise ValueError("select_strategy: m.strategy has no length")

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
    match mode:
        case "Deflation":
            # Check for deflation option before clicking there.
            try:
                wait_for_badge(
                    const.FILE_PREFIX + "modeDeflation.png", [(1322, 486)], 3
                )
            except:
                raise Exception("Deflation mode not found. Timed out.")
            GUI.wait_click(0, 1293, 475)  # Deflation button
        case "Standard":
            # Check for standard option before clicking there.
            try:
                wait_for_badge(const.FILE_PREFIX + "modeStandard.png", [(667, 584)], 3)
            except:
                raise Exception("Standard mode not found. Timed out.")
            GUI.wait_click(0, 634, 587)  # Standard button
        case _:
            raise ValueError("select_gamemode: Invalid gamemode.")


def select_difficulty_smart(diff):
    match diff:
        case 0:
            # Check for easy option before clicking there.
            try:
                wait_for_badge(const.FILE_PREFIX + "selectEasy.png", [(627, 406)], 3)
            except:
                raise Exception("Easy option not found. Timed out.")
            GUI.wait_click(0, 618, 417)  # Easy button
        case _:
            raise ValueError("select_difficulty: Invalid difficulty.")


def overwrite_save_smart(timeout=1.5):
    # Check for saved game, & overwrite if necessary
    try:
        wait_for_badge(const.FILE_PREFIX + "overwriteBadge.png", [(570, 379)], timeout)
    except:
        pass  # No overwrite required
    else:
        GUI.wait_click(0, 1137, 729)  # Overwrite Save


def map_loading_wait(timeout=20, post_load_wait=0.8):
    # Check for map to be loaded.
    try:
        wait_for_badge(const.FILE_PREFIX + "loaded2.png", [(960, 392)], timeout)
    except:
        print("Map loaded screen not found. Timed out.")
        raise RuntimeError
    GUI.wait_click(0, 969, 758)  # okay
    GUI.wait(post_load_wait)


def perform_strategy(s, log_final_wait=False):
    strategy_to_use = s
    action_list = strategy_to_use.get_actions()

    for i, a in enumerate(action_list):
        if log_final_wait and i == len(action_list) - 1:
            # On final action.
            try:
                final_wait_time = int(a.get_info())
            except:
                final_wait_time = None
            print(f"<log>Final wait time: {final_wait_time}")
        execute_action(a)


def check_auto_start(timeout=5):
    try:
        result = wait_for_badge_2(
            [
                const.FILE_PREFIX + "autoStartOff.png",
                const.FILE_PREFIX + "autoStartOn.png",
            ],
            [[(1325, 307)], [(1325, 307)]],
            timeout,
            match_threshold=[0.5],
        )
    except:
        raise TimeoutError("check_auto_start: Unknown result. Timed out.")

    # result of 0: auto start is OFF
    # result of 1: auto start is ON
    # error thrown: unkown state

    return result


def toggle_auto_start():
    currentState = const.AUTO_START
    if currentState != 0 and currentState != 1:
        raise ValueError
    elif currentState == 0:
        const.AUTO_START = 1
    else:
        const.AUTO_START = 0


def check_game_result(timeout=30, log_time_elapsed=False):
    if log_time_elapsed:
        start_time = time.time()
    # Check for game result.
    try:
        G = wait_for_badge_2(
            [const.FILE_PREFIX + "win.png", const.FILE_PREFIX + "loss.png"],
            [[(944, 209)], [(944, 209)]],
            timeout,
        )
    except:
        raise Exception("beat_map: Unknown game result. Timed out.")

    if log_time_elapsed:
        end_time = time.time()
        elapsed_time = round(abs(end_time - start_time), 3)
        if elapsed_time < 1 or elapsed_time > 2:
            print(f"<log>Time elapsed: {elapsed_time} <!>")
        else:
            print(f"<log>Time elapsed: {elapsed_time}")

    return G


def execute_action(a):
    match a.get_name():
        case "Tower":
            for t in a.info:
                do_tower_action(t)
        case "WaitSec":
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

            ROUND_TIMEOUT = 60

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
                    wait_for_badge(
                        const.FILE_PREFIX + "roundStopped.png",
                        [(1832, 1016)],
                        ROUND_TIMEOUT,
                        threshold=[0.9],
                    )
                except:
                    raise RuntimeError("Round exceeded wait_time.")

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
            GUI.wait(wait_time)
        case _:
            raise ValueError("execute_action: Invalid action name.")


def do_tower_action(t):
    this_hot_key = t.get_hotkey()
    UPGRADE_KEYS = [",", ".", "/"]

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
    for path_num in range(len(u)):
        for i in range(u[path_num]):
            GUI.wait(0.08)
            GUI.key_push(UPGRADE_KEYS[path_num])

    # Set targeting priority
    for n in range(t.targeting):
        GUI.wait(0.08)
        GUI.key_push("tab")

    GUI.deselect()


def wait_for_badge(filename, coords, timeout, threshold=[0.07]):
    SEARCH_RADIUS = 0
    SEARCH_MODE = 0
    ROUNDING = 1

    try:
        x = len(threshold)
    except:
        threshold = [threshold]

    match_found = False
    match_found, match_coords, match_percent = locate(
        filename, coords, SEARCH_RADIUS, threshold, SEARCH_MODE, ROUNDING
    )

    start_time = time.time()
    while (not match_found) and abs(time.time() - start_time) <= timeout:
        GUI.exit_key_check()
        match_found, match_coords, match_percent = locate(
            filename, coords, SEARCH_RADIUS, threshold, SEARCH_MODE, ROUNDING
        )

    if not match_found:
        raise TimeoutError("wait_for_badge: Timed out. Not found.")
    else:
        return True


def wait_for_badge_2(filenames, coordMx, timeout, match_threshold=[0.07]):
    n = len(filenames)
    SEARCH_RADIUS = 0
    SEARCH_MODE = 0
    ROUNDING = 1
    match_found = False

    start_time = time.time()  # (####.###) seconds.

    while abs(time.time() - start_time) <= timeout:
        GUI.exit_key_check()
        for i in range(n):
            filename = filenames[i]
            coords = coordMx[i]

            match_found, match_coords, match_percent = locate(
                filename, coords, SEARCH_RADIUS, match_threshold, SEARCH_MODE, ROUNDING
            )
            if match_found:
                return i

    raise TimeoutError("wait_for_badge_2: Timed out. Neither found.")


def find_rewards_map(diff, filename, rad=0):
    curr_debug_mode = rad != 0

    mode = 0
    rou = 1
    t_list = const.get_matches()
    c_list = Location.get_coord_list()

    current_page = navigate(Page.get_page_by_info(const.PAGES, diff, 1))

    # Check for expert button before continuing.
    try:
        wait_for_badge(const.FILE_PREFIX + "expert.png", [(1337, 974)], 5)
    except:
        raise Exception("Expert button not found. Timed out.")

    m_found = False  # initial value.

    notable = (None, (0, 0), 0)
    # pageNum, coords, matchRatio

    for i in range(Page.get_num_subpages(diff)):
        GUI.wait(0.4)

        ### Check current page at each location in c_list ###
        m_found, m_coords, m_ratio = locate(
            filename, c_list, rad, t_list, mode, rou, debug_mode=curr_debug_mode
        )

        if curr_debug_mode:
            print(f"# [{m_coords[0]} {m_coords[1]}] {percentage(m_ratio)} match.")

        if m_ratio > notable[2]:
            # notable keeps track of the current best
            notable = (current_page, m_coords, m_ratio)

        # Quit if a match is found.
        if m_found:
            break

        # Otherwise, go to the next page and try again.
        if curr_debug_mode:
            print("-> Next page.")
        current_page = navigate(Page.get_next_in_diff(current_page))

    notable_ratio = notable[2]

    if m_found or (notable[0] is not None and notable_ratio > 0.01):
        # Retrieve Location from given coords.
        if m_found:
            match_location = Location.get_loc_from_coords(m_coords)
        else:
            match_location = Location.get_loc_from_coords(notable[1])

        # Handle bad result.
        if match_location is None:
            raise RuntimeError("find_rewards_map: Locate returned invalid coords.")

        loc_num = Location.get_loc_num(match_location)  # Identify data index
        prev_min_ratio = const.get_match(loc_num)  # Retrive data at given index

        if not m_found:
            print(
                f"No {100*prev_min_ratio}% matches, but a {percentage(notable_ratio)} match was found."
            )

        if notable_ratio <= prev_min_ratio:
            const.set_match(loc_num, notable_ratio, do_reporting=True)  # Update data.txt

        # Return Map from given Location
        return Map.get_map_from_location(
            const.MAPS, notable[0].number, match_location
        )
    else:
        print("Done searching. [No matches found]")
        return None


def percentage(decimal):
    return str(round(100 * decimal, 1)) + "%"


### Start of Main ###
def main():
    const.init()
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
    except ValueError:
        print("Invalid settings.")
        raise SystemError

    GUI.wait_click(0, 1900, 0)  # click top right of screen to focus

    i = 0
    money_earned = 0
    while True:
        # Wait for home screen before continuing.
        try:
            wait_for_badge(const.FILE_PREFIX + "homePlay.png", [(834, 933)], 30, 0.90)
        except:
            raise Exception("Must start on home screen. Timed out.")
        GUI.play_button(0)

        # Check for expert button before continuing.
        try:
            wait_for_badge(const.FILE_PREFIX + "expert.png", [(1337, 974)], 5)
        except:
            raise Exception("Expert button not found. Timed out.")

        match const.MAP_SELECTION_MODE:
            case 0:
                m = Map.get_map_by_name(const.MAPS, const.DEFAULT_MAP)
            case 1:
                m = Map.pick_rand(const.MAPS)
            case 2:  # Play maps in order
                m = const.MAPS[i % len(const.MAPS)]
            case 3:
                search_file = const.FILE_PREFIX + const.BADGE_NAME
                m = find_rewards_map(diff=3, filename=search_file)
                if m is None:
                    m = Map.get_map_by_name(const.MAPS, const.DEFAULT_MAP)
            case 4:
                search_file = const.FILE_PREFIX + const.BADGE_NAME
                m = find_rewards_map(diff=3, filename=search_file)
                if m is None:
                    m = const.MAPS[i % len(const.MAPS)]
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
                    m = const.MAPS[i % len(const.MAPS)]
            case _:
                raise ValueError("Invalid Map Selection Mode.")

        print(f"{i+1}.\t{m.name}")
        navigate(const.PAGES[m.page])
        isWin = beat_map(m)

        if isWin:
            money_earned += 66
        print("Money earned: $", money_earned)

        GUI.wait(1)

        try:
            R = wait_for_badge_2(
                [
                    const.FILE_PREFIX + "homePlay.png",
                    const.FILE_PREFIX + "collectBadge.png",
                ],
                [[(834, 933)], [(960, 679)]],
                25,
            )
        except:
            raise Exception("Unknown free monkey status. Timed out.")
        match R:
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
