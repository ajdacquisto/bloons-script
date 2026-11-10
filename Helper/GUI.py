import pydirectinput, keyboard, time
from Helper.KeyboardInput import PressKey, ReleaseKey
import pyautogui as pg
from Helper.Tower import Tower
from typing import List
from Helper.Map import Map
from Helper.Hero import Hero

# from Map import MAPS
import Helper.Page as Page


def key_push(c: str) -> None:
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
    if keyboard.is_pressed("CAPSLOCK"):
        print("End time: %.3f sec" % time.time())
        print("<!> Keyboard Interrupt... <!>")
        raise SystemExit
    if keyboard.is_pressed("Up"):
        print("-> %.1f sec" % time.time())


def wait(n: float) -> None:
    interval = 0.1
    for i in range(round(n / interval)):
        exit_key_check()
        time.sleep(interval)


def wait_click(t: float, x: int, y: int) -> None:
    wait(t)
    pg.click(x, y)


def center_cursor() -> None:
    pg.moveTo(960, 540)


def place_tower(t: Tower) -> None:
    x, y = t.get_position()
    key_push(t.get_hotkey())
    pg.moveTo(x, y, duration=0.1)
    wait_click(0, x, y)


def select_tower(t: Tower) -> None:
    x, y = t.get_position()
    wait_click(0.2, x, y)


def sell_tower(t: Tower) -> None:
    select_tower(t)
    key_push("bksp")


def deselect() -> None:
    wait(0.1)
    key_push("esc")


def check_input_vars(map_list: List[Map], params: List[any]) -> None:
    POST_WIN_WAIT, MAP_LOADING_TIME, DEFAULT_MAP, MAP_SELECTION_MODE = params

    # Check POST_WIN_WAIT
    if (POST_WIN_WAIT != POST_WIN_WAIT // 1) or (POST_WIN_WAIT < 0):
        raise ValueError("Invalid Post-Win Wait Time.")

    # Check MAP_LOADING_TIME
    if (MAP_LOADING_TIME != MAP_LOADING_TIME // 1) or (MAP_LOADING_TIME < 0):
        raise ValueError("Invalid Map Loading Time.")

    # Check DEFAULT_MAP
    found = False
    for m in map_list:
        if m.name == DEFAULT_MAP:
            found = True
            break
    if not found:
        raise ValueError("Invalid Default Map Name.")

    # Check MAP_SELECTION_MODE
    if (
        (MAP_SELECTION_MODE != MAP_SELECTION_MODE // 1)
        or (MAP_SELECTION_MODE < 0)
        or (MAP_SELECTION_MODE > 5)
    ):
        raise ValueError("Invalid Map Selection Mode.")


def hero_change_button() -> None:
    wait_click(0.5, 104, 990)


def hero_select_button() -> None:
    wait_click(0.2, 1116, 615)


def back_arrow_button() -> None:
    wait_click(0.2, 80, 50)


def play_button(waitTime) -> None:
    wait_click(waitTime, 833, 936)


def victory_next_button(waittime) -> None:
    wait_click(waittime, 958, 909)  # next


def victory_home_button(waittime) -> None:
    wait_click(waittime, 718, 842)  # home


def defeat_home_button(waittime) -> None:
    wait_click(waittime, 738, 805)  # home


def esc_cancel_button() -> None:
    wait_click(0.1, 796, 747)


def free_monkey_cont_button() -> None:
    wait_click(2, 957, 674)


def auto_start_toggle_switch(waittime) -> None:
    wait_click(waittime, 1325, 307)


def select_hero(H: Hero) -> None:
    if H.name != "None":
        x, y = H.get_coords()
        hero_change_button()
        wait_click(0.5, x, y)  # Hero coords
        hero_select_button()
        back_arrow_button()


def page_button(difficulty: int, waittime: float = 0) -> None:
    C = Page.get_button_coords(difficulty)
    wait_click(waittime, C[0], C[1])


def accept_free_monkeys() -> bool:
    xCoords = [810, 1106, 661, 960, 1261]
    yCoord = 532
    free_monkey_cont_button()
    wait(2)
    for xCoord in xCoords:
        for i in range(2):
            wait_click(0.4, xCoord, yCoord)

    wait_click(0.2, 958, 997)  # cont
    wait(0.2)
    for x in range(3):
        wait(0.2)
        key_push("esc")
    esc_cancel_button()

    return True
