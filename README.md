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

Expert, Easy, Standard, and Deflation templates were checked on fresh captures
after a +/-30-pixel adjacency search. Standard's template center moved down
9 pixels and Deflation's down 8 pixels. These four targets now require an 85%
match and allow a 2-pixel search radius. Other targets retain their existing
calibration except page dots: a compact filled-center template was verified
against all 17 active indicators and their inactive neighbors, with an 85%
threshold and 1-pixel search radius. This is not automatic threshold learning.
Difficulty-tab clicks move the pointer away afterward so hover highlighting
does not invalidate the Expert-tab template.

The console logs startup settings, page navigation, strategy actions and fixed
waits, and vision waits. Vision logs identify the target and required threshold,
report progress every `VISION_LOG_INTERVAL` seconds, and report successful match
scores or timeout best scores and coordinates. `VISION_POLL_INTERVAL` controls
the delay between unsuccessful polling sweeps (default 0.2 seconds); `STOP_KEY`
is checked during polling. Set `LOG_LEVEL` to `"WARNING"` in `constant.py` to
hide informational messages. Screenshots are not saved by this logging.

Deflation waits up to `MAP_LOADING_TIMEOUT_DEFLATION` seconds (default 30) for
its introductory OK prompt. A timeout preserves the vision diagnostics and stops
the run without clicking through or executing the strategy.

The `Helper` folder contains the map, page, and strategy data used by the
automation. Matching templates and reference screenshots are in `Media`.

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
`None,-1,-1` means the strategy does not select or place a hero. Slots below the
visible grid may require scrolling support, which is not currently automated.

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
