"""Mouse and keyboard helpers for navigating the game UI."""

import time
from typing import List

import keyboard
import pyautogui as pg
import pydirectinput

import constant as const
import Helper.Page as Page
from Helper.Hero import Hero
from Helper.KeyboardInput import PressKey, ReleaseKey
from Helper.Map import Map
from Helper.Tower import Tower


def key_push(c: str) -> None:
    """Send a supported key press, checking the exit key first."""
    exit_key_check()
    if c == "esc":
        pydirectinput.press("esc")
        return

    match c:
        # case 'esc': code = 0x01

        case "1":
            code = 0x02
        case "2":
            code = 0x03
        case "3":
            code = 0x04
        case "4":
            code = 0x05
        case "5":
            code = 0x06
        case "6":
            code = 0x07
        case "7":
            code = 0x08
        case "8":
            code = 0x09
        case "9":
            code = 0x0A
        case "0":
            code = 0x0B

        case "-":
            code = 0x0C
        case "=":
            code = 0x0D
        case "bksp":
            code = 0x0E
        case "tab":
            code = 0x0F

        case "q":
            code = 0x10
        case "w":
            code = 0x11
        case "e":
            code = 0x12
        case "r":
            code = 0x13
        case "t":
            code = 0x14
        case "y":
            code = 0x15
        case "u":
            code = 0x16
        case "i":
            code = 0x17
        case "o":
            code = 0x18
        case "p":
            code = 0x19
        case "[":
            code = 0x1A
        case "]":
            code = 0x1B

        case "enter":
            code = 0x1C

        case "a":
            code = 0x1E
        case "s":
            code = 0x1F
        case "d":
            code = 0x20
        case "f":
            code = 0x21
        case "g":
            code = 0x22
        case "h":
            code = 0x23
        case "j":
            code = 0x24
        case "k":
            code = 0x25
        case "l":
            code = 0x26

        case ";":
            code = 0x27
        case "'":
            code = 0x28
        case "`":
            code = 0x29

        case "\\":
            code = 0x2B

        case "z":
            code = 0x2C
        case "x":
            code = 0x2D
        case "c":
            code = 0x2E
        case "v":
            code = 0x2F
        case "b":
            code = 0x30
        case "n":
            code = 0x31
        case "m":
            code = 0x32

        case ",":
            code = 0x33
        case ".":
            code = 0x34
        case "/":
            code = 0x35

        case " ":
            code = 0x39
        case "caps":
            code = 0x3A

        case _:
            raise ValueError(f"key_push: Invalid character. {c}")

    PressKey(code)
    ReleaseKey(code)


def exit_key_check() -> None:
    """Exit on Caps Lock or print the current time on Up."""
    if keyboard.is_pressed("CAPSLOCK"):
        print(f"End time: {time.time():.3f} sec")
        print("<!> Keyboard Interrupt... <!>")
        raise SystemExit
    if keyboard.is_pressed("Up"):
        print(f"-> {time.time():.1f} sec")


def wait(n: float) -> None:
    """Wait in short intervals while checking for the exit key."""
    interval = 0.1
    for i in range(round(n / interval)):
        exit_key_check()
        time.sleep(interval)


def wait_click(t: float, x: int, y: int) -> None:
    """Wait, then click at the specified game-local coordinates."""
    wait(t)
    pg.click(*const.get_desktop_coords(x, y))


def center_cursor() -> None:
    """Move the cursor to the center of the expected screen."""
    pg.moveTo(*const.get_desktop_coords(*const.UI_CLICKS["center"]))


def place_tower(t: Tower) -> None:
    """Select and place a tower at its configured position."""
    x, y = t.get_position()
    key_push(t.get_hotkey())
    pg.moveTo(*const.get_desktop_coords(x, y), duration=0.1)
    wait_click(0, x, y)


def select_tower(t: Tower) -> None:
    """Select a tower at its configured position."""
    x, y = t.get_position()
    wait_click(0.2, x, y)


def sell_tower(t: Tower) -> None:
    """Select and sell a tower at its configured position."""
    select_tower(t)
    key_push("bksp")


def deselect() -> None:
    """Close the current selection."""
    wait(0.1)
    key_push("esc")


def check_input_vars(map_list: List[Map], params: List[any]) -> None:
    """Validate the configured waits, default map, and selection mode."""
    post_win_wait, map_loading_time, default_map, map_selection_mode = params

    # Check POST_WIN_WAIT
    if (post_win_wait != post_win_wait // 1) or (post_win_wait < 0):
        raise ValueError("Invalid Post-Win Wait Time.")

    # Check MAP_LOADING_TIME
    if (map_loading_time != map_loading_time // 1) or (map_loading_time < 0):
        raise ValueError("Invalid Map Loading Time.")

    # Check DEFAULT_MAP
    found = False
    for m in map_list:
        if m.name == default_map:
            found = True
            break
    if not found:
        raise ValueError("Invalid Default Map Name.")

    # Check MAP_SELECTION_MODE
    if (
        (map_selection_mode != map_selection_mode // 1)
        or (map_selection_mode < 0)
        or (map_selection_mode > 5)
    ):
        raise ValueError("Invalid Map Selection Mode.")


def hero_change_button() -> None:
    """Open the hero-selection screen."""
    wait_click(0.5, *const.UI_CLICKS["change_hero"])


def hero_select_button() -> None:
    """Confirm the selected hero."""
    wait_click(0.2, *const.UI_CLICKS["select_hero"])


def back_arrow_button() -> None:
    """Click the back arrow."""
    wait_click(0.2, *const.UI_CLICKS["back"])


def play_button(waitTime) -> None:  # pylint: disable=invalid-name
    """Wait, then click Play."""
    wait_click(waitTime, *const.UI_CLICKS["home_play"])


def victory_next_button(waittime) -> None:
    """Wait, then advance from the victory screen."""
    wait_click(waittime, *const.UI_CLICKS["victory_next"])


def victory_home_button(waittime) -> None:
    """Wait, then return home after a victory."""
    wait_click(waittime, *const.UI_CLICKS["victory_home"])


def defeat_home_button(waittime) -> None:
    """Wait, then return home after a defeat."""
    wait_click(waittime, *const.UI_CLICKS["defeat_home"])


def esc_cancel_button() -> None:
    """Click Cancel in the escape menu."""
    wait_click(0.1, *const.UI_CLICKS["escape_cancel"])


def free_monkey_cont_button() -> None:
    """Continue to the free-monkey selection screen."""
    wait_click(2, *const.UI_CLICKS["free_monkey_continue"])


def auto_start_toggle_switch(waittime) -> None:
    """Wait, then toggle auto-start."""
    wait_click(waittime, *const.UI_CLICKS["auto_start"])


def select_hero(H: Hero) -> None:  # pylint: disable=invalid-name
    """Select the specified hero unless the strategy uses no hero."""
    if H.name != "None":
        x, y = H.get_coords()
        hero_change_button()
        wait_click(0.5, x, y)  # Hero coords
        hero_select_button()
        back_arrow_button()


def page_button(difficulty: int, waittime: float = 0) -> None:
    """Click the page tab for a map difficulty."""
    coords = Page.get_button_coords(difficulty)
    wait_click(waittime, coords[0], coords[1])
    center_cursor()


def accept_free_monkeys() -> bool:
    """Collect available free monkeys and dismiss the reward screens."""
    x_coords = [810, 1106, 661, 960, 1261]
    y_coord = 532
    free_monkey_cont_button()
    wait(2)
    for x_coord in x_coords:
        for i in range(2):
            wait_click(0.4, x_coord, y_coord)

    wait_click(0.2, 958, 997)  # cont
    wait(0.2)
    for x in range(3):
        wait(0.2)
        key_push("esc")
    esc_cancel_button()

    return True
