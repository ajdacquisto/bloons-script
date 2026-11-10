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
loop. Press **Caps Lock** to stop it. Review the map-selection and game settings
in `constant.py` before running. The automation relies on fixed screen
coordinates and image templates for a 1920x1080 layout, so a different
resolution, UI scale, or game layout can cause incorrect input.

The `Helper` folder contains the map, page, and strategy data used by the
automation. Matching templates and reference screenshots are in `Media`.

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
