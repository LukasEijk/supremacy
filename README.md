![supremacy](https://github.com/europython2023gametournament/supremacy/assets/39047984/fd147b1a-252b-4aed-b949-e2cb943f80dd)

# Supremacy

## Installation

### Launcher

If you have been given a game code, you can use the AI Game Launcher to install and configure the game.

1. Download and run the [AI Game Launcher](https://jl-wynen.github.io/aigl/)
2. Install the game through the GUI.
3. Follow the instructions in the launcher to set up your environment and run Supremacy.

### Manual setup (clean baseline)

Expected workspace layout:

mkdir supremacy
cd supremacy
git clone https://github.com/nvaytet/supremacy.git
git clone https://github.com/<USERNAME>/<MYPLAYERNAME>_ai.git
git clone https://github.com/nvaytet/supremacy_ai.git

- `~/repos/supremacy/supremacy` (this repo, game engine)
- `~/repos/supremacy/supremacy_ai` (template AI repo, source folder)
- `~/repos/supremacy/your_bot` (your own bot package or source folder)

1. Pre-event: install tools

Install:

- `git`
- Python `3.11`
- one environment workflow: `uv` (recommended), `conda`, or `venv`

Quick checks:

```bash
git --version
python3 --version
conda --version
uv --version
```

You only need one of `uv` or `conda`.

2. Create and activate your environment

#### Option A: uv

```bash
mkdir -p ~/repos/supremacy
cd ~/repos/supremacy
uv venv --python 3.11 .venv
source .venv/bin/activate
uv pip install -U pip setuptools wheel
```

#### Option B: conda

```bash
conda create -n vkb-supremacy -c conda-forge python=3.11 pip
conda activate vkb-supremacy
python -m pip install -U pip setuptools wheel
```

#### Option C: plain venv

```bash
mkdir -p ~/repos/supremacy
cd ~/repos/supremacy
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip setuptools wheel
```

3. Event day: clone repositories

```bash
mkdir -p ~/repos/supremacy
cd ~/repos/supremacy
git clone <EVENT_REPO_URL_MAIN>
git clone <EVENT_REPO_URL_AI_TEMPLATE>
```

4. Install the game package from workspace root

```bash
cd ~/repos/supremacy
python -m pip install -U pip setuptools wheel
python -m pip install -e ./supremacy
```

If you use `uv`, the install step can also be:

```bash
uv pip install -e ./supremacy
```

Important:

- Do not run `pip install -e ./supremacy_ai` unless it is explicitly turned into a package.
- In the standard event layout, `supremacy_ai` is a source folder and is imported via workspace path.

5. Make local bot modules importable

```bash
export PYTHONPATH=~/repos/supremacy
```

Optional persistence for zsh:

```bash
echo 'export PYTHONPATH=~/repos/supremacy' >> ~/.zshrc
```

6. Verify setup

```bash
cd ~/repos/supremacy
python -c "import supremacy; import supremacy_ai; import numpy; print('setup ok')"
supremacy supremacy/config.toml
```

If both commands run, your setup is correct.

7. Add your own bot and configure players

Create `~/repos/supremacy/your_bot` with at least:

- `your_bot/__init__.py` (exports `CREATOR` and `PlayerAi`)
- `your_bot/my_ai.py`

Minimal `your_bot/__init__.py`:

```python
from .my_ai import CREATOR, PlayerAi

__all__ = ["CREATOR", "PlayerAi"]
```

If `your_bot` is a proper Python package (`pyproject.toml` or `setup.py` exists), install it:

```bash
python -m pip install -e ./your_bot
```

If `your_bot` is a source folder only, keep running commands from `~/repos/supremacy` with `PYTHONPATH` set as above.

Example player config in `supremacy/config.toml`:

```toml
[[player]]
package = "your_bot"

[[player]]
package = "supremacy_ai"
overrides = { name = "PracticeBot", color = "#2fb0ac" }
```

8. Run modes

Normal run:

```bash
supremacy supremacy/config.toml
```

Tournament-style run:

```bash
supremacy supremacy/config-tournament.toml
```

Typical tournament flags in `supremacy/config-tournament.toml`:

- `test = false`
- `safe = true`
- `fullscreen = true`
- `super-crystal = true` (only if your event setup expects it)

9. Troubleshooting

Quick import checks:

```bash
python -c "import supremacy; import supremacy_ai; print('imports ok')"
python -c "import your_bot; print('your_bot ok')"
```

- If `supremacy` is not found, reactivate your environment and rerun `python -m pip install -e ./supremacy` from `~/repos/supremacy`.
- If `import supremacy_ai` or `import your_bot` fails for source-folder bots, check that your current directory is `~/repos/supremacy` and that `PYTHONPATH` is set correctly.

## Game preview

<table>
  <tr>
    <td>Time = 2min</td><td>Time = 4min</td>
  </tr>
  <tr>
    <td><img src="https://github.com/europython2023gametournament/supremacy/assets/39047984/faa2b2c6-67c0-4017-af47-1f8a8b2d42b0" width="100%" /></td>
    <td><img src="https://github.com/europython2023gametournament/supremacy/assets/39047984/b3915e43-48dd-41ff-978d-24a213a0934a" width="100%" /></td>
  </tr>
</table>

## Goal

- Mine resources to build an army
- Destroy enemy bases and eliminate other players

## Rounds

- All participants play on the map at the same time
- Each round lasts 8 minutes
- The tournament will consist of 8 rounds of 8 minutes

## Game map

- The map is auto-generated every round
- It has periodic boundary conditions (for example when a vehicle arrives at the right edge of the map, it will re-appear at the left edge)
- The map size will scale with the number of players (more players = larger map)
- Coordinate system: lower left corner: `(x=0, y=0)`, upper right corner: `(x=nx, y=ny)`

## Mining

- Everyone starts with 1 base, housing 1 mine
- Every timestep, each mine will extract `crystal = 2 * number_of_mines`
- Crystal is used to build mines and vehicles
- Mines too close to other bases compete for resources: `crystal = 2 * number_of_mines / number_of_bases_inside_square_of_80px`
- Bases that contain mines that are competing with others will have a “C” label on them:

![Screenshot at 2023-07-17 10-07-33](https://github.com/europython2023gametournament/supremacy/assets/39047984/d4e96611-0e40-4364-8b07-afc8b5f64023)

## Fights

- Whenever two or more vehicles or bases from opposing teams come within 5px from each other, they will fight
- During each time step, every object hits all the others with its attack force, and it takes damage from all other objects

## Vehicles

<table>
  <tr>
    <th></th>
    <th>Tank &nbsp;&nbsp;&nbsp; <img src="https://github.com/europython2023gametournament/supremacy/assets/39047984/d8a69d16-62f3-4bb3-924e-7c3ec5821813" />
</th>
    <th>Ship &nbsp;&nbsp;&nbsp; <img src="https://github.com/europython2023gametournament/supremacy/assets/39047984/3e8b2b2d-272d-4159-8c7d-4901c30f459e" />
</th>
    <th>Jet &nbsp;&nbsp;&nbsp; <img src="https://github.com/europython2023gametournament/supremacy/assets/39047984/6ffa27ce-fe80-4fbf-95c4-c57696525df3" />
</th>
  </tr>
  <tr>
    <td>Speed</td>
    <td>10</td>
    <td>5</td>
    <td>20</td>
  </tr>
  <tr>
    <td>Attack</td>
    <td>20</td>
    <td>10</td>
    <td>30</td>
  </tr>
  <tr>
    <td>Health</td>
    <td>50</td>
    <td>200</td>
    <td>50</td>
  </tr>
  <tr>
    <td>Cost</td>
    <td>500</td>
    <td>2000</td>
    <td>4000</td>
  </tr>
  <tr>
    <td>Can travel</td>
    <td>On land</td>
    <td>On sea</td>
    <td>Anywhere</td>
  </tr>
  <tr>
    <td></td>
    <td></td>
    <td>Can turn into base</td>
    <td></td>
  </tr>
</table>

## Additional rules:

- Mine cost doubles for every new mine on a given base (first mine=1000, second=2000, third=4000, etc…)
- Base has `health = 100`, mine has `health = 50` (both have `0` attack)
- Vehicles move at `speed * dt` (`dt = 1/15s`)
- A ship can be turned into a new base, by calling `convert_to_base()`
- A conversion to base will only work if there is land in the immediate vicinity
- A player is eliminated when all his/her bases have been destroyed
- If a player is eliminated, all his/her vehicles disappear instantly

## Scoring

- +1 point if you destroy a base
- If a player gets eliminated, they receive a number of points equal to the number of players that were eliminated before them
- At the end of the round, every player still alive gets a number of points equal to the number of eliminated players

## The control center - the AI

- To play the game, you will have to create a Python program.
- It should contain a class named `PlayerAI` and that class should have a method named `run`.
- Every time step, the `run` method will be called, and it will be inside that function that you should control your vehicles, decide what to build, etc...
- You are provided with a `supremacy_ai` package to give you an example.

Look at the comments in the `simple_ai.py` (in `supremacy_ai/src/supremacy_ai/`) for details on what information is available to you at every time step and what methods can be called.
If you want to start from a template with less pre-filled logic, use `barebones_ai.py` instead and adjust `__init__.py` accordingly.

### `game_map`

- The `game_map` is one of the arguments the `run` function will receive.
- It is a Numpy array that automatically gets filled when your vehicles or bases visit that region of the map.
- `1` means land, `0` means sea, `-1` means no info.
- Any visit makes anything in that part of the map permanently visible.
- This is basically what defines which enemy bases and vehicles you get in your info every time step.

![Screenshot at 2023-07-17 14-27-22](https://github.com/europython2023gametournament/supremacy/assets/39047984/fe37e030-b9ef-43d8-8d60-138c3ddb7b45)

## Optimizing development

There are 3 ways you can speed up your development.

### 1. The high contrast mode

Activate `high_contrast = True` to see the land borders better and competing areas for mines:

![Screenshot at 2023-07-17 10-08-09](https://github.com/europython2023gametournament/supremacy/assets/39047984/762506cc-d444-439e-ab67-2701f91846d4)

### 2. Crystal boost

Waiting for things to develop can be time consuming.
You can artificially increase mine yield using `crystal_boost=5` (or any number you want, although behavior is untested beyond 10).

### 3. Use the 'Pause' Luke (experimental)

While the game is running, you can hit `P` on the keyboard.
This will pause the game.
You can edit your AI code.
When the game resumes (hit `P` again), it will reload your AI module.
