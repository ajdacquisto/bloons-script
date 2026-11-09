# BTD6 Macro

This script automates repetitive tasks in Bloons TD 6.

## Requirements

- Windows
- Python 3
- Bloons TD 6 running with a screen layout compatible with the hard-coded coordinates in the script

## Setup

From this directory, create and activate a virtual environment, then install the dependencies:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Important

`BTD6_Auto_Candy.py` immediately starts controlling the mouse and keyboard and repeats its game automation loop indefinitely. Its coordinates are hard-coded, so it may click or type in the wrong place if your game or display layout differs. Review the script before running it, and only run it when you intend to automate the game. To stop it, press `Ctrl+C` in the terminal running it.

Run it from this directory so it can find `pumpkin.csv`:

```powershell
python .\BTD6_Auto_Candy.py
```
