# BTD6 Macro

This project automates Bloons TD 6 using screen-image matching and mouse and
keyboard input. It is designed for Windows and the screen layout and coordinates
used by the project.

## Requirements

- Windows
- Python 3.10 or newer
- Bloons TD 6 running with a screen layout compatible with the hard-coded coordinates in the script

## Setup

From this directory, create and activate a virtual environment, then install the dependencies:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Run

Start Bloons TD 6 and leave it at the home screen, then run:

```powershell
python .\Main.py
```

The script begins controlling the mouse and keyboard and repeats its automation
loop. Press **F12** to stop it (configured by `STOP_KEY` in `constant.py`).
Caps Lock no longer stops the macro. Review the map-selection and game settings
in `constant.py` before running. The automation relies on fixed screen
coordinates and image templates for a 1920x1080 layout, so a different
resolution, UI scale, or game layout can cause incorrect input.

To display the live mouse coordinates without running the macro, use:

```powershell
python .\mouse_coords.py
```

This standalone script uses only Python's standard library and the Windows
API. It prints desktop coordinates. Press **Caps Lock** to pause or resume the
display, and **Ctrl+C** to exit.

### Using another monitor

Set `GAME_SCREEN_ORIGIN` near the top of `constant.py` to the desktop coordinates
of the game monitor's top-left corner:

```python
GAME_SCREEN_ORIGIN = (-1920, 290)
```

The default `(0, 0)` uses the primary display. The selected display must use the
same 1920x1080 game layout and UI scale; this setting translates coordinates,
not resolution or DPI scaling. Mouse input is offset to that display and live
image matching captures its 1920x1080 rectangle, including negative desktop
coordinates. Keep strategy, page, and button coordinates relative to the game's
top-left corner, not the desktop. For coordinates recorded on the example
monitor, subtract its origin: `local_x = desktop_x + 1920` and
`local_y = desktop_y - 290`.

The game must remain visible and focused. The macro still controls the shared
mouse and keyboard, so another monitor does not provide independent input.

### UI calibration and live logging

`Helper/UICalibration.py` centralizes template filenames, game-local detection
centers, thresholds, search radii, and related click positions. Detection and
click coordinates can differ: the template may cover only part of a button.
Page-dot positions still come from `Helper/pageInfo.dat`, map-card positions
from `Helper/Location.py`, and tower coordinates from each strategy.

Expert, Easy, and Deflation match stable labels on the current game layout.
Their templates were checked against repeated live captures and unrelated
screens; Easy uses a 60% threshold, Expert and Deflation use 80%, all with a
2-pixel search radius. Auto Start uses distinct on/off switch templates with
a 40% threshold; live matches reached 80% and the opposite-state cross-match
stayed below 11%. Standard retains its existing icon calibration. A compact filled-center page-dot
template was verified against all 17 active indicators and their inactive
neighbors, with an 85% threshold and 1-pixel search radius. This is not
automatic threshold learning. Difficulty-tab clicks move the pointer away
afterward so hover highlighting does not invalidate the Expert-tab template.

The console logs startup settings, page navigation, strategy actions and fixed
waits, and vision waits. Vision logs identify the target and required threshold,
report progress every `VISION_LOG_INTERVAL` seconds, and report successful match
scores or timeout best scores and coordinates. `VISION_POLL_INTERVAL` controls
the delay between unsuccessful polling sweeps (default 0.2 seconds); `STOP_KEY`
is checked during polling. Set `LOG_LEVEL` to `"WARNING"` in `constant.py` to
hide informational messages. Screenshots are not saved by this logging.
After each game, the macro waits up to `RETURN_HOME_TIMEOUT` seconds
(default 60) for the home screen or free-monkey reward.
Hero-selection checks use a compact checkmark crop with tolerant color rounding
so the card artwork beneath the badge does not prevent verification.

Deflation waits up to `MAP_LOADING_TIMEOUT_DEFLATION` seconds (default 30) for
its introductory OK prompt. A timeout preserves the vision diagnostics and stops
the run without clicking through or executing the strategy.

After loading, both game modes check for the optional Monkey Teams notice for
up to two seconds. Only a detected notice triggers its OK click; the macro
verifies that it disappears before changing Auto Start or placing towers.
If it remains visible, the run stops with an error instead of sending the
strategy's inputs into the popup.

Injected scan-code keys are held for `KEY_HOLD_SECONDS` (default 0.1) from
`Helper/UICalibration.py`; near-instant presses can be missed by the game.
Escape uses its existing direct-input path.

The `Helper` folder contains the map, page, and strategy data used by the
automation. Matching templates and reference screenshots are in `Media`.

Workshop builds two 0-0-2 Villages for stacked discounts before buying its
0-3-1 Super, 0-3-0 Wizard, and 3-0-1 Alchemist. It then upgrades the first
Village to 0-1-2, sells the temporary second Village, and finishes the first
at 0-2-2 for camo detection. Keep this purchase/sell order and the tight nook
placements in `Helper/Map.py`. Tower-action logs report input commands, not
confirmation that a tower was placed or an upgrade was affordable.
The live-checked budget used Monkey Knowledge bonuses and $20,200 starting
cash, with only $37 remaining after setup.

Ouch places its 3-0-2 Alchemist near Churchill and the Ninja, with the Carrier
in range. The previous Alchemist location did not place, and the 4-0-2 upgrade
left too little for the intended Ninja upgrades. A manually assembled run
using Monkey Knowledge and $20,200 starting cash won with 200 lives remaining.

Map-selection pages are defined in `Helper/pageInfo.dat`; navigation derives
each difficulty's page count from this file. Keep page numbers sequential from
zero and subpages sequential from zero within each difficulty. Update map page
numbers and card positions in `Helper/mapLocations.dat` when the game adds maps.
Random, ordered, and reward-based selection only choose maps with at least one
strategy defined in `Helper/Map.py`; maps without strategies can remain in the
location data. Reward searches skip unsupported and unlisted cards, and ordered
fallbacks cycle through playable maps. Modes 0 and 3 require the configured
default map to have a strategy. The current default is mode 1: random playable
maps, without event-reward searches. Set `MAP_SELECTION_MODE` in `constant.py`
to change it.

Hero names and zero-based selection slots come from `Helper/heroes.dat`
(`Name,Row,Col`), loaded before map strategies are built. Edit that file when
the hero grid changes; no separate hard-coded hero list needs updating.
`None,-1,-1` means the strategy does not select or place a hero.

Hero selection scrolls the grid fully to the top or bottom (whichever anchor
shows the card), clicks the card, and confirms the selected checkmark
(`Media/heroSelected.png`) before leaving the screen; one retry is made, then
the run stops with an error. Card positions are derived from the last row in
`heroes.dat`, so adding heroes needs no coordinate changes. Grid geometry lives
in `Helper/UICalibration.py` (`HERO_GRID_*`). The game ignores PyAutoGUI wheel
events, so scrolling uses `SendInput` wheel notches after a small relative mouse
move that registers the hover.

## Development

Install the development dependencies and run the automated checks:

```powershell
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v

$files = @(git ls-files '*.py' | ForEach-Object { $_ -replace '/', '\' })
python -m pylint --disable=R,W,E,F --reports=n --score=n $files
```

The tests mock mouse and keyboard input; they do not play the game. The Pylint
command checks convention diagnostics. Omit `--disable=R,W,E,F` to see the
remaining errors, warnings, and refactoring suggestions as well. Existing module
names and legacy public keyword names are retained for compatibility.
