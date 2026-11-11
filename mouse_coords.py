"""Print live mouse coordinates using only the Windows API."""

import ctypes
import time


class Point(ctypes.Structure):
    """Windows screen point."""

    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]


def get_mouse_position():
    """Return the mouse position in desktop coordinates."""
    point = Point()
    if not ctypes.windll.user32.GetCursorPos(ctypes.byref(point)):
        raise ctypes.WinError()
    return point.x, point.y


def caps_lock_pressed():
    """Return whether Caps Lock is currently held down."""
    return bool(ctypes.windll.user32.GetAsyncKeyState(0x14) & 0x8000)


def main():
    """Print the current mouse position; Caps Lock pauses or resumes output."""
    paused = False
    caps_lock_down = False
    print("Press Caps Lock to pause/resume; Ctrl+C to exit.")

    try:
        while True:
            is_down = caps_lock_pressed()
            if is_down and not caps_lock_down:
                paused = not paused
                print("\nPaused." if paused else "\nResumed.")
            caps_lock_down = is_down

            if not paused:
                x, y = get_mouse_position()
                print(f"\r({x}, {y})", end="", flush=True)
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
